/**
 * @file datasource/local.ts
 * @description 로컬 파일시스템을 통해 프로젝트 데이터를 읽는 DataSource 구현체
 *
 * 보안 제약 (SEC-001-02, REQ-009-03):
 * - 생성자에서 basePath를 path.resolve()로 정규화한다.
 * - path.relative() 경계와 realpath를 함께 검사해 prefix 충돌과 symlink 이탈을 차단한다.
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
  RuntimeDelegationRecord,
  DocNode,
  CommitEntry,
  PathTraversalError,
  EXTERNAL_DOC_EXTENSIONS,
} from '../types'
import { RuntimeActivitySchema, SessionDataSchema, VulcanConfigSchema } from '../schemas'
import { assertPathInside, isPathInside, UnsafePathError } from '../pathSecurity'

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
    try {
      return assertPathInside(this.resolvedBasePath, targetPath)
    } catch (err) {
      if (err instanceof UnsafePathError) {
        throw new PathTraversalError(targetPath)
      }
      throw err
    }
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
        current_branch: this.readGitBranch(this.resolvedBasePath),
        workflow: result.data.workflow ?? runtime.workflow ?? null,
        active_executions: activeExecutions,
        worktrees: this.readRuntimeWorktrees(activeExecutions),
        delegations: this.readRuntimeDelegations(),
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
            const result = RuntimeActivitySchema.safeParse(this.mergeRuntimeStatus(parsed))
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

  private mergeRuntimeStatus(activity: unknown): unknown {
    if (!activity || typeof activity !== 'object') return activity
    const base = activity as Record<string, unknown>
    const statusFile = typeof base.status_file === 'string' ? base.status_file : ''
    if (!statusFile) return base

    try {
      const statusPath = path.resolve(this.resolvedBasePath, statusFile)
      this.assertSafePath(statusPath)
      if (!fs.existsSync(statusPath) || !fs.statSync(statusPath).isFile()) return base

      const statusStat = fs.statSync(statusPath)
      const statusJson = JSON.parse(fs.readFileSync(statusPath, 'utf-8')) as Record<string, unknown>
      const ageSeconds = Math.max(0, Math.floor((Date.now() - statusStat.mtimeMs) / 1000))
      const merged: Record<string, unknown> = {
        ...base,
        ...statusJson,
        status_file: statusFile.replace(/\\/g, '/'),
        last_update: typeof statusJson.last_update === 'string'
          ? statusJson.last_update
          : statusStat.mtime.toISOString(),
        last_update_age_seconds: ageSeconds,
        status_stale: base.status === 'running' && ageSeconds > 300,
      }
      if (merged.status_stale && merged.status === 'running') {
        merged.status = 'stale'
      }
      return merged
    } catch (err) {
      console.warn('[LocalDataSource] runner status 읽기 실패:', err)
      return base
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
      if (!isPathInside(this.resolvedBasePath, resolved)) return

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

  private readRuntimeDelegations(): NonNullable<ProjectRuntime['delegations']> {
    return this.mergeRuntimeDelegations([
      ...this.readDelegationSidecars(),
      ...this.readRunDelegations(),
    ]).slice(0, 12)
  }

  private readDelegationSidecars(): NonNullable<ProjectRuntime['delegations']> {
    const delegationsPath = path.join(this.resolvedBasePath, '.vulcan', 'delegations')
    this.assertSafePath(delegationsPath)

    if (!fs.existsSync(delegationsPath)) return []

    try {
      return fs.readdirSync(delegationsPath)
        .filter((name) => name.toLowerCase().endsWith('.json'))
        .flatMap((name) => {
          const filePath = path.join(delegationsPath, name)
          this.assertSafePath(filePath)
          if (!fs.statSync(filePath).isFile()) return []

          try {
            const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8')) as Record<string, unknown>
            const record = this.normalizeDelegationSidecar(name, parsed)
            return record ? [record] : []
          } catch {
            return []
          }
        })
    } catch (err) {
      console.warn('[LocalDataSource] delegation sidecar 읽기 실패:', err)
      return []
    }
  }

  private normalizeDelegationSidecar(
    fileName: string,
    payload: Record<string, unknown>,
  ): RuntimeDelegationRecord | null {
    const runId = this.stringValue(payload.run_id)
      ?? this.stringValue(payload.target_id)
      ?? fileName.match(/(?:RUN|RV|QA)-\d+/i)?.[0]?.toUpperCase()
    if (!runId) return null

    const changedFiles = this.stringArrayValue(payload.changed_files)
    const selfCheck = this.arrayValue(payload.self_check) ?? this.arrayValue(payload.self_checks)
    const orchestratorVerification = this.arrayValue(payload.orchestrator_verification)
      ?? this.arrayValue(payload.verification)

    return {
      run_id: runId,
      run_file: this.stringValue(payload.run_file) ?? undefined,
      sidecar_path: `.vulcan/delegations/${fileName}`,
      mode: this.stringValue(payload.mode) ?? this.stringValue(payload.runner) ?? 'unknown',
      delegate: this.stringValue(payload.delegate) ?? undefined,
      task: this.stringValue(payload.task) ?? undefined,
      status: this.stringValue(payload.status) ?? undefined,
      result_summary: this.stringValue(payload.result_summary) ?? this.stringValue(payload.summary) ?? undefined,
      model: this.stringValue(payload.model) ?? undefined,
      reasoning_effort: this.stringValue(payload.reasoning_effort) ?? this.stringValue(payload.effort) ?? undefined,
      model_source: this.stringValue(payload.model_source) ?? undefined,
      effort_source: this.stringValue(payload.effort_source) ?? undefined,
      model_policy_role: this.stringValue(payload.model_policy_role) ?? undefined,
      model_fallback_reason: this.stringValue(payload.model_fallback_reason) ?? undefined,
      changed_count: changedFiles.length > 0 ? changedFiles.length : undefined,
      changed_files: changedFiles.length > 0 ? changedFiles : undefined,
      started_at: this.stringValue(payload.started_at) ?? undefined,
      last_activity_at: this.stringValue(payload.last_activity_at) ?? this.stringValue(payload.last_update) ?? undefined,
      completed_at: this.stringValue(payload.completed_at) ?? undefined,
      verified_at: this.stringValue(payload.verified_at) ?? undefined,
      verification_status: this.stringValue(payload.verification_status) ?? undefined,
      self_check_count: selfCheck?.length,
      orchestrator_verification_count: orchestratorVerification?.length,
      source: 'delegation_sidecar',
    }
  }

  private mergeRuntimeDelegations(records: RuntimeDelegationRecord[]): RuntimeDelegationRecord[] {
    const byKey = new Map<string, RuntimeDelegationRecord>()

    for (const record of records) {
      const key = [
        record.run_id,
        record.mode,
        record.delegate ?? '',
      ].join('|')
      if (!byKey.has(key)) {
        byKey.set(key, record)
      }
    }

    return Array.from(byKey.values()).sort((a, b) => {
      const aRank = this.delegationStatusRank(a.status)
      const bRank = this.delegationStatusRank(b.status)
      if (aRank !== bRank) return aRank - bRank
      return this.delegationTimeValue(b) - this.delegationTimeValue(a)
    })
  }

  private delegationStatusRank(status?: string): number {
    const normalized = (status ?? '').toLowerCase()
    if (['running', 'worker_running', 'delegated', 'orchestrator_verifying'].includes(normalized)) return 0
    if (['blocked', 'failed', 'timeout', 'environment_blocked'].includes(normalized)) return 1
    if (['completed_no_result_change', 'completed', 'verified'].includes(normalized)) return 2
    return 3
  }

  private delegationTimeValue(record: RuntimeDelegationRecord): number {
    const value = record.last_activity_at ?? record.completed_at ?? record.started_at ?? record.verified_at
    if (!value) return 0
    const parsed = Date.parse(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  private stringValue(value: unknown): string | null {
    return typeof value === 'string' && value.trim() ? value.trim() : null
  }

  private stringArrayValue(value: unknown): string[] {
    if (!Array.isArray(value)) return []
    return value.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
  }

  private arrayValue(value: unknown): unknown[] | null {
    return Array.isArray(value) ? value : null
  }

  private readRunDelegations(): NonNullable<ProjectRuntime['delegations']> {
    const runsPath = path.join(this.resolvedBasePath, 'docs', 'runs')
    this.assertSafePath(runsPath)

    if (!fs.existsSync(runsPath)) return []

    try {
      return fs.readdirSync(runsPath)
        .filter((name) => name.toLowerCase().endsWith('.md'))
        .flatMap((name) => {
          const filePath = path.join(runsPath, name)
          this.assertSafePath(filePath)
          if (!fs.statSync(filePath).isFile()) return []
          const content = fs.readFileSync(filePath, 'utf-8')
          return this.parseRunDelegations(name, content)
        })
        .slice(0, 12)
    } catch (err) {
      console.warn('[LocalDataSource] Run 위임 기록 읽기 실패:', err)
      return []
    }
  }

  private parseRunDelegations(fileName: string, content: string): NonNullable<ProjectRuntime['delegations']> {
    const runId = this.extractRunId(fileName, content)
    const runFile = `docs/runs/${fileName}`
    const records = this.parseDelegationRecordsBlock(content, runId, runFile)
    if (records.length > 0) return records

    if (/^#{2,4}\s*Run Execution Record\b/m.test(content)) {
      return [{
        run_id: runId,
        run_file: runFile,
        mode: 'external-runner',
        delegate: this.extractScalar(content, 'runner') ?? undefined,
        task: this.extractScalar(content, 'task') ?? this.extractScalar(content, 'goal') ?? undefined,
        status: this.extractScalar(content, 'status') ?? undefined,
        model: this.extractScalar(content, 'model') ?? undefined,
        reasoning_effort: this.extractScalar(content, 'reasoning_effort') ?? undefined,
        model_source: this.extractScalar(content, 'model_source') ?? undefined,
        effort_source: this.extractScalar(content, 'effort_source') ?? undefined,
        model_policy_role: this.extractScalar(content, 'model_policy_role') ?? undefined,
        model_fallback_reason: this.extractScalar(content, 'model_fallback_reason') ?? undefined,
        source: 'run_execution_record',
      }]
    }

    if (/orchestrator_direct_edit_reason\s*:/i.test(content)) {
      return [{
        run_id: runId,
        run_file: runFile,
        mode: 'manual',
        delegate: 'orchestrator',
        task: this.extractScalar(content, 'goal') ?? undefined,
        status: this.extractScalar(content, 'status') ?? undefined,
        source: 'direct_edit',
      }]
    }

    return []
  }

  private parseDelegationRecordsBlock(
    content: string,
    runId: string,
    runFile: string,
  ): NonNullable<ProjectRuntime['delegations']> {
    const lines = content.split(/\r?\n/)
    const start = lines.findIndex((line) => /^delegation_records\s*:/i.test(line.trim()))
    if (start < 0) return []
    if (/\[\s*\]\s*$/.test(lines[start] ?? '')) return []

    const block: string[] = []
    for (let index = start + 1; index < lines.length; index += 1) {
      const line = lines[index] ?? ''
      if (line.trim() === '') {
        block.push(line)
        continue
      }
      if (/^\S/.test(line)) break
      block.push(line)
    }

    const records: NonNullable<ProjectRuntime['delegations']> = []
    let current: Record<string, string> | null = null
    let inChangedFiles = false
    let changedCount = 0

    const pushCurrent = () => {
      if (!current) return
      const mode = current.mode || current.runner || current.delegate || 'unknown'
      records.push({
        run_id: runId,
        run_file: runFile,
        mode: this.cleanYamlScalar(mode),
        delegate: current.delegate ? this.cleanYamlScalar(current.delegate) : undefined,
        task: current.task ? this.cleanYamlScalar(current.task) : undefined,
        status: current.status ? this.cleanYamlScalar(current.status) : undefined,
        result_summary: current.result_summary ? this.cleanYamlScalar(current.result_summary) : undefined,
        model: current.model ? this.cleanYamlScalar(current.model) : undefined,
        reasoning_effort: current.reasoning_effort ? this.cleanYamlScalar(current.reasoning_effort) : undefined,
        model_source: current.model_source ? this.cleanYamlScalar(current.model_source) : undefined,
        effort_source: current.effort_source ? this.cleanYamlScalar(current.effort_source) : undefined,
        model_policy_role: current.model_policy_role ? this.cleanYamlScalar(current.model_policy_role) : undefined,
        model_fallback_reason: current.model_fallback_reason ? this.cleanYamlScalar(current.model_fallback_reason) : undefined,
        changed_count: changedCount || undefined,
        source: 'delegation_records',
      })
    }

    for (const rawLine of block) {
      const itemMatch = rawLine.match(/^\s*-\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$/)
      if (itemMatch) {
        pushCurrent()
        current = { [itemMatch[1] ?? 'mode']: itemMatch[2] ?? '' }
        inChangedFiles = false
        changedCount = 0
        continue
      }
      if (!current) continue

      const keyValueMatch = rawLine.match(/^\s+([A-Za-z_][\w-]*)\s*:\s*(.*)$/)
      if (keyValueMatch) {
        const key = keyValueMatch[1] ?? ''
        const value = keyValueMatch[2] ?? ''
        current[key] = value
        inChangedFiles = key === 'changed_files'
        continue
      }

      if (inChangedFiles && /^\s+-\s+/.test(rawLine)) {
        changedCount += 1
      }
    }
    pushCurrent()

    return records
  }

  private extractRunId(fileName: string, content: string): string {
    const fromContent = content.match(/^run_id\s*:\s*["']?([A-Z]+-\d+)/im)?.[1]
    if (fromContent) return fromContent
    return fileName.match(/(?:RUN|RV|QA)-\d+/i)?.[0]?.toUpperCase() ?? fileName.replace(/\.md$/i, '')
  }

  private extractScalar(content: string, key: string): string | null {
    const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const match = content.match(new RegExp(`^\\s*${escaped}\\s*:\\s*(.+)$`, 'im'))
    return match?.[1] ? this.cleanYamlScalar(match[1]) : null
  }

  private cleanYamlScalar(value: string): string {
    const trimmed = value.trim()
    if (trimmed === '[]' || trimmed === '{}' || trimmed === 'null') return ''
    return trimmed.replace(/^["']|["']$/g, '')
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
      if (err instanceof PathTraversalError) throw err
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
