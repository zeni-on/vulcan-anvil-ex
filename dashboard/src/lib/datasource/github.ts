/**
 * @file datasource/github.ts
 * @description GitHub REST API를 통해 프로젝트 데이터를 읽는 DataSource 구현체
 *
 * 보안 제약 (REQ-009-02, SEC-001-01):
 * - GITHUB_TOKEN은 이 모듈을 호출하는 API Route(서버사이드)에서만 주입한다.
 * - 클라이언트 번들에 이 파일이 포함되지 않도록 API Route에서만 import한다.
 * - token 값은 어떠한 응답 바디에도 포함하지 않는다.
 *
 * @see docs/02-design/req-001-004-design.md §GitHubDataSource
 */

import {
  DataSource,
  SessionData,
  DocNode,
  CommitEntry,
  DataSourceError,
} from '../types'
import { SessionDataSchema } from '../schemas'

interface GitHubDataSourceConfig {
  repo: string   // "owner/repo" 형식
  branch: string
  token: string  // 서버사이드에서만 주입 (process.env.GITHUB_TOKEN)
}

const GITHUB_API_BASE = 'https://api.github.com'

export class GitHubDataSource implements DataSource {
  private readonly repo: string
  private readonly branch: string
  private readonly token: string

  constructor(config: GitHubDataSourceConfig) {
    if (!config.token) {
      throw new DataSourceError(
        'GITHUB_TOKEN이 설정되지 않았습니다. .env.local에 GITHUB_TOKEN을 추가하세요.'
      )
    }
    this.repo = config.repo
    this.branch = config.branch
    this.token = config.token
  }

  /** 공통 fetch 래퍼 — GitHub API 인증 헤더 및 에러 처리 포함 */
  private async ghFetch(path: string): Promise<unknown> {
    const url = `${GITHUB_API_BASE}${path}`
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${this.token}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
      // Next.js 캐싱 비활성화 — 항상 최신 데이터 패치
      cache: 'no-store',
    })

    if (!res.ok) {
      throw new DataSourceError(
        `GitHub API 오류: ${res.status} ${res.statusText} (${url})`
      )
    }

    return res.json()
  }

  /**
   * session.json을 GitHub API로 읽어 SessionData로 파싱한다.
   *
   * GET /repos/{repo}/contents/session.json?ref={branch}
   * → content 필드를 Base64 디코드 → JSON 파싱 → Zod 검증
   *
   * UT-002-01: 정상 응답 Base64 디코드 및 JSON 파싱
   * UT-002-02: GitHub API 404 응답 시 DataSourceError throw
   */
  async getSession(): Promise<SessionData | null> {
    try {
      const data = await this.ghFetch(
        `/repos/${this.repo}/contents/session.json?ref=${this.branch}`
      ) as { content?: string; encoding?: string }

      if (!data.content || data.encoding !== 'base64') {
        throw new DataSourceError('session.json 응답 형식이 올바르지 않습니다.')
      }

      // Base64 디코드 (Node.js 환경)
      const decoded = Buffer.from(data.content.replace(/\n/g, ''), 'base64').toString('utf-8')
      const parsed = JSON.parse(decoded)

      const result = SessionDataSchema.safeParse(parsed)
      if (!result.success) {
        // 스키마 오류 시 null 반환 — UI에서 "데이터 없음" 표시 (REQ-009-06)
        console.warn('[GitHubDataSource] session.json 스키마 오류:', result.error.message)
        return null
      }

      return result.data as SessionData
    } catch (err) {
      if (err instanceof DataSourceError) throw err
      throw new DataSourceError('session.json 읽기 실패', err)
    }
  }

  /**
   * docs/ 경로의 파일 목록을 GitHub Git Trees API로 읽어 DocNode[]로 변환한다.
   *
   * GET /repos/{repo}/git/trees/{branch}?recursive=1
   * → docs/ 경로 필터링 → .md 파일만 포함 → DocNode[] 변환
   */
  async getDocTree(): Promise<DocNode[]> {
    try {
      const data = await this.ghFetch(
        `/repos/${this.repo}/git/trees/${this.branch}?recursive=1`
      ) as { tree?: Array<{ path: string; type: string }> }

      if (!data.tree) return []

      // docs/ 하위 .md 파일만 필터링
      const docFiles = data.tree.filter(
        (item) => item.type === 'blob' && item.path.startsWith('docs/') && item.path.endsWith('.md')
      )

      return buildDocTree(docFiles.map((f) => f.path))
    } catch (err) {
      if (err instanceof DataSourceError) throw err
      throw new DataSourceError('문서 트리 읽기 실패', err)
    }
  }

  /**
   * 커밋 이력을 GitHub Commits API로 읽어 CommitEntry[]로 변환한다.
   *
   * GET /repos/{repo}/commits?sha={branch}&per_page={limit}
   *
   * UT-002-03: limit 파라미터가 per_page 쿼리로 전달됨
   */
  async getCommits(limit: number): Promise<CommitEntry[]> {
    try {
      const data = await this.ghFetch(
        `/repos/${this.repo}/commits?sha=${this.branch}&per_page=${limit}`
      ) as Array<{
        sha: string
        commit: {
          message: string
          author?: { name?: string; date?: string }
        }
      }>

      if (!Array.isArray(data)) return []

      return data.map((item) => ({
        sha: item.sha,
        message: item.commit.message.split('\n')[0], // 첫 줄만
        author: item.commit.author?.name ?? 'Unknown',
        date: item.commit.author?.date ?? '',
      }))
    } catch (err) {
      if (err instanceof DataSourceError) throw err
      throw new DataSourceError('커밋 이력 읽기 실패', err)
    }
  }

  /**
   * docs/{relPath} 파일 내용을 GitHub Contents API로 읽어 UTF-8 문자열로 반환한다.
   * GET /repos/{repo}/contents/docs/{relPath}?ref={branch}
   * REQ-010-01, REQ-010-05
   */
  async readDocFile(relPath: string): Promise<string> {
    try {
      const data = await this.ghFetch(
        `/repos/${this.repo}/contents/docs/${relPath}?ref=${this.branch}`
      ) as { content?: string; encoding?: string }

      if (!data.content || data.encoding !== 'base64') {
        throw new DataSourceError('파일 응답 형식이 올바르지 않습니다.')
      }

      return Buffer.from(data.content.replace(/\n/g, ''), 'base64').toString('utf-8')
    } catch (err) {
      if (err instanceof DataSourceError) throw err
      throw new DataSourceError(`파일 읽기 실패: docs/${relPath}`, err)
    }
  }
}

// ── 내부 유틸: 경로 목록 → DocNode 트리 변환 ──────────────────────────────────

/**
 * 평면 경로 목록을 DocNode 트리로 변환한다.
 * 예: ['docs/01-requirements/REQUIREMENTS.md'] → DocNode[]
 */
function buildDocTree(paths: string[]): DocNode[] {
  interface DirEntry {
    node: DocNode
    childMap: Map<string, DirEntry>
  }

  const rootMap = new Map<string, DirEntry>()

  for (const filePath of paths.sort()) {
    const parts = filePath.split('/')
    const segments = parts.slice(1) // 'docs' 제외

    let currentMap = rootMap
    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i]
      const slug = parts.slice(0, i + 2)
      const isLast = i === segments.length - 1

      if (!currentMap.has(segment)) {
        const node: DocNode = isLast
          ? { name: segment.replace(/\.md$/, ''), slug, type: 'file' }
          : { name: segment, slug, type: 'dir', children: [] }
        currentMap.set(segment, { node, childMap: new Map() })
      }

      if (!isLast) {
        currentMap = currentMap.get(segment)!.childMap
      }
    }
  }

  function collect(map: Map<string, DirEntry>): DocNode[] {
    return Array.from(map.values()).map((entry) => {
      if (entry.node.type === 'dir') {
        entry.node.children = collect(entry.childMap)
      }
      return entry.node
    })
  }

  return collect(rootMap)
}

