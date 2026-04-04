/**
 * @file __tests__/api/session-docs-commits.test.ts
 * @description GET /api/projects/[id]/session|docs|commits API Route 단위 테스트
 *
 * 커버 UT-ID:
 * - UT-005-01: GET /api/projects/[id]/session — 존재하는 id → SessionData 반환 (200)
 * - UT-005-02: GET /api/projects/[id]/session — 존재하지 않는 id → 404 반환
 * - UT-005-03: GET /api/projects/[id]/session — session.json 없음(로컬) → session: null 200 반환
 * - UT-005-04: GET /api/projects/[id]/docs — docs/ 파일 목록 → DocNode[] 반환 (200)
 * - UT-005-05: GET /api/projects/[id]/docs — docs/ 비어있을 때 → 빈 배열 200 반환
 * - UT-005-06: GET /api/projects/[id]/commits — 로컬 git log 정상 → CommitEntry[] 반환 (200)
 * - UT-005-07: GET /api/projects/[id]/commits — git log 실패(비git 폴더) → 빈 배열 200 반환
 * - UT-005-08: GET /api/projects/[id]/commits — GitHub 모드 → API 호출로 CommitEntry[] 반환
 * - UT-009-01: Path Traversal 감지 → 403 반환
 * - UT-009-02: DataSourceError → 503 반환
 *
 * 전략:
 * - projects.ts, datasource를 jest.mock으로 대체하여 파일시스템 / 네트워크 격리
 * - route 함수를 직접 호출 (Next.js Request 모킹)
 * - DataSource 메서드는 jest.fn()으로 주입하여 각 시나리오 제어
 *
 * @see docs/02-design/req-005-009-design.md §API Route 설계
 * @see docs/03-test-plan/TEST_PLAN.md UT-005-01~08, UT-009-01~02
 */

import { NextRequest } from 'next/server'

// ── projects.ts 모킹 (fs 격리) ─────────────────────────────────────────────

jest.mock('../../lib/projects', () => ({
  readProjects: jest.fn(),
}))

// ── datasource 모킹 (네트워크/파일시스템 격리) ──────────────────────────────

const mockGetSession = jest.fn()
const mockGetDocTree = jest.fn()
const mockGetCommits = jest.fn()

jest.mock('../../lib/datasource', () => ({
  createDataSource: jest.fn(() => ({
    getSession: mockGetSession,
    getDocTree: mockGetDocTree,
    getCommits: mockGetCommits,
  })),
}))

import { readProjects } from '../../lib/projects'
import { createDataSource } from '../../lib/datasource'
import { GET as sessionGET } from '../../app/api/projects/[id]/session/route'
import { GET as docsGET } from '../../app/api/projects/[id]/docs/route'
import { GET as commitsGET } from '../../app/api/projects/[id]/commits/route'
import { DataSourceError, PathTraversalError } from '../../lib/types'
import type { Project, SessionData, DocNode, CommitEntry } from '../../lib/types'

const mockReadProjects = readProjects as jest.MockedFunction<typeof readProjects>
const mockCreateDataSource = createDataSource as jest.MockedFunction<typeof createDataSource>

// ── 테스트 픽스처 ─────────────────────────────────────────────────────────────

const LOCAL_PROJECT: Project = {
  id: 'local-test-abc123',
  name: 'Local Test Project',
  type: 'local',
  path: '/tmp/test-project',
  addedAt: '2026-04-04T00:00:00.000Z',
}

const GITHUB_PROJECT: Project = {
  id: 'github-owner-repo-abc123',
  name: 'GitHub Test Project',
  type: 'github',
  repo: 'owner/repo',
  branch: 'main',
  addedAt: '2026-04-04T00:00:00.000Z',
}

const VALID_SESSION: SessionData = {
  project: 'TestProject',
  vulcan_version: '1.0.0',
  current_gate: 'gate2',
  gate_status: {
    gate1: 'done',
    gate2: 'in-progress',
    gate3: 'pending',
    impl: 'pending',
    gate4: 'pending',
    gate5: 'pending',
  },
  started: '2026-04-04',
  completed: ['Gate 1 완료'],
  pending: [],
  blocked: [],
}

const VALID_DOCS: DocNode[] = [
  { name: 'REQUIREMENTS', slug: ['docs', '01-requirements', 'REQUIREMENTS.md'], type: 'file' },
  {
    name: '01-requirements',
    slug: ['docs', '01-requirements'],
    type: 'dir',
    children: [
      { name: 'REQUIREMENTS', slug: ['docs', '01-requirements', 'REQUIREMENTS.md'], type: 'file' },
    ],
  },
]

const VALID_COMMITS: CommitEntry[] = [
  { sha: 'abc1234', message: 'feat: 초기 커밋', author: 'developer', date: '2026-04-04T00:00:00Z' },
  { sha: 'def5678', message: 'fix: 버그 수정', author: 'developer', date: '2026-04-03T00:00:00Z' },
]

/** RouteContext 헬퍼 */
function makeContext(id: string): { params: Promise<{ id: string }> } {
  return { params: Promise.resolve({ id }) }
}

/** NextRequest 헬퍼 */
function makeRequest(url: string): NextRequest {
  return new NextRequest(url)
}

beforeEach(() => {
  jest.clearAllMocks()
  // 기본값: createDataSource가 정상 DataSource 반환
  mockCreateDataSource.mockImplementation(() => ({
    getSession: mockGetSession,
    getDocTree: mockGetDocTree,
    getCommits: mockGetCommits,
    readDocFile: jest.fn(),
  }))
})

// ── UT-005-01~03: GET /api/projects/[id]/session ─────────────────────────────

describe('GET /api/projects/[id]/session', () => {
  /**
   * UT-005-01: 존재하는 id → SessionData 반환 (200)
   */
  it('UT-005-01: 존재하는 id와 정상 session → { session, fetchedAt } 200 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetSession.mockResolvedValue(VALID_SESSION)

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/session')
    const ctx = makeContext('local-test-abc123')
    const res = await sessionGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.session).toBeDefined()
    expect(body.session.project).toBe('TestProject')
    expect(body.session.current_gate).toBe('gate2')
    expect(body.fetchedAt).toBeTruthy()
  })

  /**
   * UT-005-02: 존재하지 않는 id → 404 반환
   */
  it('UT-005-02: 존재하지 않는 id → 404', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])

    const req = makeRequest('http://localhost:3001/api/projects/nonexistent/session')
    const ctx = makeContext('nonexistent')
    const res = await sessionGET(req, ctx)

    expect(res.status).toBe(404)
    expect(mockGetSession).not.toHaveBeenCalled()
  })

  /**
   * UT-005-03: session.json 없음(로컬) → session: null 200 반환
   * LocalDataSource.getSession()이 null을 반환하는 시나리오.
   */
  it('UT-005-03: session.json 없음(getSession이 null 반환) → { session: null } 200 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    // session.json이 없거나 스키마 오류 시 LocalDataSource는 null 반환
    mockGetSession.mockResolvedValue(null)

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/session')
    const ctx = makeContext('local-test-abc123')
    const res = await sessionGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.session).toBeNull()
    expect(body.fetchedAt).toBeTruthy()
  })

  it('UT-009-01: PathTraversalError → 403 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetSession.mockRejectedValue(new PathTraversalError('/etc/passwd'))

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/session')
    const ctx = makeContext('local-test-abc123')
    const res = await sessionGET(req, ctx)

    expect(res.status).toBe(403)
  })

  it('UT-009-02: DataSourceError → 503 반환', async () => {
    mockReadProjects.mockReturnValue([GITHUB_PROJECT])
    mockGetSession.mockRejectedValue(new DataSourceError('GitHub API 오류'))

    const req = makeRequest('http://localhost:3001/api/projects/github-owner-repo-abc123/session')
    const ctx = makeContext('github-owner-repo-abc123')
    const res = await sessionGET(req, ctx)

    expect(res.status).toBe(503)
  })

  it('createDataSource가 DataSourceError throw(GITHUB_TOKEN 미설정) → 503', async () => {
    mockReadProjects.mockReturnValue([GITHUB_PROJECT])
    mockCreateDataSource.mockImplementation(() => {
      throw new DataSourceError('GITHUB_TOKEN이 설정되지 않았습니다.')
    })

    const req = makeRequest('http://localhost:3001/api/projects/github-owner-repo-abc123/session')
    const ctx = makeContext('github-owner-repo-abc123')
    const res = await sessionGET(req, ctx)

    expect(res.status).toBe(503)
  })
})

// ── UT-005-04~05: GET /api/projects/[id]/docs ────────────────────────────────

describe('GET /api/projects/[id]/docs', () => {
  /**
   * UT-005-04: docs/ 경로 파일 목록 → DocNode[] 반환 (200)
   */
  it('UT-005-04: 정상 docs 목록 → { docs, fetchedAt } 200 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetDocTree.mockResolvedValue(VALID_DOCS)

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/docs')
    const ctx = makeContext('local-test-abc123')
    const res = await docsGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(Array.isArray(body.docs)).toBe(true)
    expect(body.docs).toHaveLength(VALID_DOCS.length)
    expect(body.fetchedAt).toBeTruthy()
  })

  /**
   * UT-005-05: docs/ 비어있을 때 → 빈 배열 200 반환
   */
  it('UT-005-05: docs/ 비어있음(빈 배열 반환) → { docs: [] } 200', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetDocTree.mockResolvedValue([])

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/docs')
    const ctx = makeContext('local-test-abc123')
    const res = await docsGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.docs).toEqual([])
  })

  it('존재하지 않는 id → 404', async () => {
    mockReadProjects.mockReturnValue([])

    const req = makeRequest('http://localhost:3001/api/projects/nonexistent/docs')
    const ctx = makeContext('nonexistent')
    const res = await docsGET(req, ctx)

    expect(res.status).toBe(404)
  })

  it('PathTraversalError → 403 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetDocTree.mockRejectedValue(new PathTraversalError('/etc/passwd'))

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/docs')
    const ctx = makeContext('local-test-abc123')
    const res = await docsGET(req, ctx)

    expect(res.status).toBe(403)
  })

  it('DataSourceError → 503 반환', async () => {
    mockReadProjects.mockReturnValue([GITHUB_PROJECT])
    mockGetDocTree.mockRejectedValue(new DataSourceError('GitHub API 오류'))

    const req = makeRequest('http://localhost:3001/api/projects/github-owner-repo-abc123/docs')
    const ctx = makeContext('github-owner-repo-abc123')
    const res = await docsGET(req, ctx)

    expect(res.status).toBe(503)
  })
})

// ── UT-005-06~08: GET /api/projects/[id]/commits ─────────────────────────────

describe('GET /api/projects/[id]/commits', () => {
  /**
   * UT-005-06: 로컬 git log 정상 → CommitEntry[] 반환 (200)
   */
  it('UT-005-06: 정상 커밋 목록 → { commits, fetchedAt } 200 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetCommits.mockResolvedValue(VALID_COMMITS)

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/commits')
    const ctx = makeContext('local-test-abc123')
    const res = await commitsGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(Array.isArray(body.commits)).toBe(true)
    expect(body.commits).toHaveLength(VALID_COMMITS.length)
    expect(body.commits[0].sha).toBe('abc1234')
    expect(body.fetchedAt).toBeTruthy()
  })

  /**
   * UT-005-07: git log 실패(비git 폴더) → 빈 배열 200 반환
   * LocalDataSource.getCommits()는 git 실패 시 빈 배열을 반환한다 (에러 아님).
   */
  it('UT-005-07: git log 실패(비git 폴더, 빈 배열 반환) → { commits: [] } 200', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    // git log 실패 시 LocalDataSource는 빈 배열 반환 (throw 하지 않음)
    mockGetCommits.mockResolvedValue([])

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/commits')
    const ctx = makeContext('local-test-abc123')
    const res = await commitsGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.commits).toEqual([])
  })

  /**
   * UT-005-08: GitHub 모드 → API 호출로 CommitEntry[] 반환
   */
  it('UT-005-08: GitHub 모드 → CommitEntry[] 반환 (200)', async () => {
    mockReadProjects.mockReturnValue([GITHUB_PROJECT])
    const githubCommits: CommitEntry[] = [
      { sha: 'aaabbb1234567', message: 'chore: CI 설정', author: 'ci-bot', date: '2026-04-04T00:00:00Z' },
    ]
    mockGetCommits.mockResolvedValue(githubCommits)

    const req = makeRequest('http://localhost:3001/api/projects/github-owner-repo-abc123/commits')
    const ctx = makeContext('github-owner-repo-abc123')
    const res = await commitsGET(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.commits[0].sha).toBe('aaabbb1234567')
    // COMMITS_LIMIT=10으로 getCommits가 호출되어야 한다
    expect(mockGetCommits).toHaveBeenCalledWith(10)
  })

  it('존재하지 않는 id → 404', async () => {
    mockReadProjects.mockReturnValue([])

    const req = makeRequest('http://localhost:3001/api/projects/nonexistent/commits')
    const ctx = makeContext('nonexistent')
    const res = await commitsGET(req, ctx)

    expect(res.status).toBe(404)
  })

  it('PathTraversalError → 403 반환', async () => {
    mockReadProjects.mockReturnValue([LOCAL_PROJECT])
    mockGetCommits.mockRejectedValue(new PathTraversalError('/etc/shadow'))

    const req = makeRequest('http://localhost:3001/api/projects/local-test-abc123/commits')
    const ctx = makeContext('local-test-abc123')
    const res = await commitsGET(req, ctx)

    expect(res.status).toBe(403)
  })

  it('DataSourceError → 503 반환', async () => {
    mockReadProjects.mockReturnValue([GITHUB_PROJECT])
    mockGetCommits.mockRejectedValue(new DataSourceError('GitHub API rate limit 초과'))

    const req = makeRequest('http://localhost:3001/api/projects/github-owner-repo-abc123/commits')
    const ctx = makeContext('github-owner-repo-abc123')
    const res = await commitsGET(req, ctx)

    expect(res.status).toBe(503)
  })
})
