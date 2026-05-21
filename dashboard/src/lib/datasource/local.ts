/**
 * @file datasource/local.ts
 * @description 로컬 파일시스템을 통해 프로젝트 데이터를 읽는 DataSource 구현체
 *
 * 보안 제약 (SEC-001-02, REQ-009-03):
 * - 생성자에서 basePath를 path.resolve()로 정규화한다.
 * - 모든 파일 접근 전에 resolvedPath.startsWith(resolvedBasePath)를 검증한다.
 * - 검증 실패 시 PathTraversalError를 throw한다.
 *
 * 에러 처리:
 * - session.json 미존재 시 기본값 SessionData 반환 (UT-002-05)
 * - git log 실패 시 빈 배열 반환 (비 git 폴더 허용)
 *
 * @see docs/02-design/req-001-004-design.md §LocalDataSource
 */

import fs from 'fs'
import path from 'path'
import { execSync } from 'child_process'
import {
  DataSource,
  SessionData,
  ProjectRuntime,
  DocNode,
  CommitEntry,
  PathTraversalError,
  EXTERNAL_DOC_EXTENSIONS,
} from '../types'
import { RuntimeActivitySchema, SessionDataSchema, VulcanConfigSchema } from '../schemas'

/** 산출물 트리에 포함할 파일 확장자 (점 포함, 소문자) */
const ALLOWED_DOC_EXTENSIONS = new Set<string>([
  '.md',
  ...EXTERNAL_DOC_EXTENSIONS.map((e) => '.' + e),
])

function getFileExtension(name: string): string | null {
  const i = name.lastIndexOf('.')
  if (i < 0) return null
  return name.slice(i).toLowerCase()
}

interface LocalDataSourceConfig {
  path: string // projects.json에 등록된 절대 경로
}

/** session.json이 없을 때 반환하는 기본값 */
const DEFAULT_SESSION: SessionData = {
  project: 'Unknown Project',
  vulcan_version: '0.0.0',
  current_gate: 'phase0',
  gate_status: {
    gate1: 'pending',
    gate2: 'pending',
    gate3: 'pending',
    impl: 'pending',
    gate4: 'pending',
    gate5: 'pending',
  },
  started: '',
  completed: [],
  pending: [],
  blocked: [],
}

export class LocalDataSource implements DataSource {
  /** path.resolve()로 정규화된 basePath — Path Traversal 방어 기준선 */
  private readonly resolvedBasePath: string

  constructor(config: LocalDataSourceConfig) {
    this.resolvedBasePath = path.resolve(config.path)
  }

  /**
   * 경로 안전성 검증.
   * resolvedPath가 resolvedBasePath로 시작하지 않으면 PathTraversalError를 throw한다.
   * SEC-001-02, REQ-009-03
   */
  private assertSafePath(targetPath: string): string {
    const resolved = path.resolve(targetPath)
    if (!resolved.startsWith(this.resolvedBasePath)) {
      throw new PathTraversalError(targetPath)
    }
    return resolved
  }

  /**
   * session.json을 로컬 파일시스템에서 읽어 SessionData로 파싱한다.
   *
   * UT-002-04: 파일 존재 시 정상 파싱
   * UT-002-05: 파일 부재 시 기본값 Session 반환
   */
  async getSession(): Promise<SessionData | null> {
    const sessionPath = path.join(this.resolvedBasePath, 'session.json')

    // Path Traversal 검증
    this.assertSafePath(sessionPath)

    if (!fs.existsSync(sessionPath)) {
      // 파일 없음 → 기본값 반환 (앱 크래시 방지)
      return { ...DEFAULT_SESSION }
    }

    try {
      const content = fs.readFileSync(sessionPath, 'utf-8')
      const parsed = JSON.parse(content)
      const result = SessionDataSchema.safeParse(parsed)

      if (!result.success) {
        console.warn('[LocalDataSource] session.json 스키마 오류:', result.error.message)
        return null
      }

      return result.data as SessionData
    } catch (err) {
      console.warn('[LocalDataSource] session.json 읽기 실패:', err)
      return null
    }
  }

  async getRuntime(): Promise<ProjectRuntime | null> {
    const configPath = path.join(this.resolvedBasePath, 'vulcan.config.json')
    this.assertSafePath(configPath)

    if (!fs.existsSync(configPath)) {
      return null
    }

    try {
      const content = fs.readFileSync(configPath, 'utf-8')
      const parsed = JSON.parse(content)
      const result = VulcanConfigSchema.safeParse(parsed)

      if (!result.success) {
        console.warn('[LocalDataSource] vulcan.config.json 스키마 오류:', result.error.message)
        return null
      }

      const runtime = result.data.runtime ?? null
      if (!runtime) return null
      const activeExecutions = this.readRuntimeActivities()

      return {
        ...runtime,
        active_executions: activeExecutions,
        worktrees: this.readRuntimeWorktrees(activeExecutions),
      }
    } catch (err) {
      console.warn('[LocalDataSource] vulcan.config.json 읽기 실패:', err)
      return null
    }
  }

  private readRuntimeActivities(): ProjectRuntime['active_executions'] {
    const execPath = path.join(this.resolvedBasePath, 'docs', 'runs', '_exec')
    this.assertSafePath(execPath)

    if (!fs.existsSync(execPath)) return []

    try {
      return fs.readdirSync(execPath)
        .filter((name) => name.endsWith('-activity.json'))
        .map((name) => path.join(execPath, name))
        .filter((filePath) => {
          this.assertSafePath(filePath)
          return fs.statSync(filePath).isFile()
        })
        .map((filePath) => {
          try {
            const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8'))
            const result = RuntimeActivitySchema.safeParse(parsed)
            return result.success ? result.data : null
          } catch {
            return null
          }
        })
        .filter((activity): activity is ProjectRuntime['active_executions'][number] => Boolean(activity))
        .sort((a, b) => (b.started_at ?? '').localeCompare(a.started_at ?? ''))
        .slice(0, 8)
    } catch (err) {
      console.warn('[LocalDataSource] runner activity 읽기 실패:', err)
      return []
    }
  }

  private readRuntimeWorktrees(activities: ProjectRuntime['active_executions']): ProjectRuntime['worktrees'] {
    const worktreeRoot = path.join(this.resolvedBasePath, '.vulcan', 'worktrees')
    this.assertSafePath(worktreeRoot)

    const byPath = new Map<string, ProjectRuntime['worktrees'][number]>()
    const now = Date.now()

    const addWorktree = (
      worktreePath: string,
      activity?: ProjectRuntime['active_executions'][number],
      existsOverride?: boolean,
    ) => {
      const resolved = path.resolve(worktreePath)
      if (!resolved.startsWith(this.resolvedBasePath)) return

      const exists = existsOverride ?? fs.existsSync(resolved)
      const changedFiles = exists ? this.readGitChangedFiles(resolved) : []
      const activityStatus = activity?.status ?? null
      const deadlineTime = activity?.deadline_at ? Date.parse(activity.deadline_at) : NaN
      const stale = activityStatus === 'running' && Number.isFinite(deadlineTime) && deadlineTime < now
      const status = stale
        ? 'stale'
        : activityStatus === 'running'
          ? 'running'
          : !exists
            ? 'missing'
            : changedFiles.length > 0
              ? 'review_needed'
              : activityStatus ?? 'clean'

      if (!exists && activityStatus !== 'running') return

      byPath.set(resolved, {
        id: path.basename(resolved),
        path: path.relative(this.resolvedBasePath, resolved).replace(/\\/g, '/'),
        branch: activity?.branch ?? (exists ? this.readGitBranch(resolved) : null),
        runner: activity?.runner ?? null,
        target_id: activity?.target_id ?? null,
        target_type: activity?.target_type ?? null,
        status,
        exists,
        changed_files: changedFiles,
        changed_count: changedFiles.length,
        activity_status: activityStatus,
        deadline_at: activity?.deadline_at ?? null,
        stale,
      })
    }

    for (const activity of activities) {
      if (activity.worktree_path) {
        addWorktree(activity.worktree_path, activity)
      }
    }

    if (fs.existsSync(worktreeRoot)) {
      try {
        for (const name of fs.readdirSync(worktreeRoot)) {
          const candidate = path.join(worktreeRoot, name)
          this.assertSafePath(candidate)
          if (!fs.existsSync(candidate) || !fs.statSync(candidate).isDirectory()) continue
          const matchedActivity = activities.find((activity) => {
            if (!activity.worktree_path) return false
            return path.resolve(activity.worktree_path) === path.resolve(candidate)
          })
          addWorktree(candidate, matchedActivity, true)
        }
      } catch (err) {
        console.warn('[LocalDataSource] worktree 목록 읽기 실패:', err)
      }
    }

    return Array.from(byPath.values()).sort((a, b) => {
      const aRunning = a.status === 'running' || a.status === 'stale'
      const bRunning = b.status === 'running' || b.status === 'stale'
      if (aRunning !== bRunning) return aRunning ? -1 : 1
      return a.id.localeCompare(b.id)
    })
  }

  private readGitChangedFiles(worktreePath: string): string[] {
    try {
      const raw = execSync('git status --porcelain', {
        cwd: worktreePath,
        encoding: 'utf-8',
        timeout: 3000,
      })
      return raw
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
          const value = line.length > 3 ? line.slice(3) : line
          if (!value.includes(' -> ')) return value
          const parts = value.split(' -> ')
          return parts[parts.length - 1] ?? value
        })
    } catch {
      return []
    }
  }

  private readGitBranch(worktreePath: string): string | null {
    try {
      const branch = execSync('git branch --show-current', {
        cwd: worktreePath,
        encoding: 'utf-8',
        timeout: 3000,
      }).trim()
      return branch || null
    } catch {
      return null
    }
  }

  /**
   * docs/ 디렉토리를 재귀 순회하여 .md 및 허용된 외부 산출물 파일 목록을 DocNode[]로 반환한다.
   *
   * UT-002-06, UT-002-07: Path Traversal 방지 적용
   */
  async getDocTree(): Promise<DocNode[]> {
    const docsPath = path.join(this.resolvedBasePath, 'docs')

    // Path Traversal 검증
    this.assertSafePath(docsPath)

    if (!fs.existsSync(docsPath)) return []

    try {
      return this.buildDocTree(docsPath, [])
    } catch (err) {
      console.warn('[LocalDataSource] 문서 트리 읽기 실패:', err)
      return []
    }
  }

  /**
   * git log를 child_process로 실행하여 CommitEntry[]로 반환한다.
   * git 명령 실패 시 빈 배열 반환 (비 git 폴더 허용).
   */
  async getCommits(limit: number): Promise<CommitEntry[]> {
    try {
      const raw = execSync(
        `git log --pretty=format:"%H|%aI|%s|%an" -n ${limit}`,
        { cwd: this.resolvedBasePath, encoding: 'utf-8' }
      )

      return raw
        .trim()
        .split('\n')
        .filter(Boolean)
        .map((line) => {
          const parts = line.replace(/^"|"$/g, '').split('|')
          return {
            sha: parts[0] ?? '',
            date: parts[1] ?? '',
            message: parts[2] ?? '',
            author: parts[3] ?? 'Unknown',
          }
        })
    } catch {
      // git log 실패 (비 git 폴더 등) → 빈 배열 반환
      return []
    }
  }

  /**
   * docs/ 하위 relPath의 .md 파일 내용을 UTF-8 문자열로 반환한다.
   * assertSafePath()로 Path Traversal 방어. 파일 미존재 시 ENOENT 에러 throw.
   * REQ-010-01, SEC-010-01
   */
  async readDocFile(relPath: string): Promise<string> {
    const filePath = path.join(this.resolvedBasePath, 'docs', relPath)
    this.assertSafePath(filePath)
    return fs.readFileSync(filePath, 'utf-8')
  }

  /**
   * 디렉토리를 재귀 순회하여 DocNode 트리를 구성한다.
   * .md 및 허용된 외부 산출물 파일만 포함, 숨김 파일 제외.
   */
  private buildDocTree(dir: string, slugPrefix: string[]): DocNode[] {
    // 각 항목 접근 전 Path Traversal 검증
    this.assertSafePath(dir)

    if (!fs.existsSync(dir)) return []

    return (fs
      .readdirSync(dir)
      .filter((f) => !f.startsWith('.') && !f.endsWith('.gitkeep'))
      .sort()
      .map((f): DocNode | null => {
        const fullPath = path.join(dir, f)

        // 개별 경로도 검증
        this.assertSafePath(fullPath)

        const slug = [...slugPrefix, f]
        const stat = fs.statSync(fullPath)

        if (stat.isDirectory()) {
          const children = this.buildDocTree(fullPath, slug)
          if (children.length === 0) return null
          return { name: f, slug, type: 'dir' as const, children }
        }

        const ext = getFileExtension(f)
        if (!ext || !ALLOWED_DOC_EXTENSIONS.has(ext)) return null
        // .md는 기존 호환성을 위해 확장자를 떼고, 그 외는 파일명 그대로 노출 (UI 분기용)
        const name = ext === '.md' ? f.slice(0, -3) : f
        return { name, slug, type: 'file' as const }
      })
      .filter((node): node is DocNode => node !== null))
  }
}
