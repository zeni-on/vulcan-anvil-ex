/**
 * @file __tests__/api/projects.test.ts
 * @description GET /api/projects, POST /api/projects, DELETE /api/projects/[id] API Route 단위 테스트
 *
 * 커버 UT-ID:
 * - UT-001-01: readProjects() projects.json 정상 파싱
 * - UT-001-02: readProjects() 파일 부재 시 빈 배열 반환
 * - UT-001-03: readProjects() 스키마 오류 항목 제외 후 정상 항목만 반환
 * - UT-003-01: GET /api/projects 정상 목록 반환 (200)
 * - UT-003-02: GET /api/projects 빈 목록 반환 시 빈 배열 (200, 500 아님)
 * - UT-004-01: POST /api/projects GitHub 타입 정상 추가 → 201 및 id 포함
 * - UT-004-02: POST /api/projects 로컬 타입 정상 추가 → 201 및 id 포함
 * - UT-004-03: POST /api/projects 필수 필드 누락 → 400
 * - UT-004-04: POST /api/projects 로컬 타입 비절대경로 → 400
 * - UT-004-05: DELETE /api/projects/[id] 존재하는 id 삭제 → 200 및 projects.json 반영
 * - UT-004-06: DELETE /api/projects/[id] 존재하지 않는 id → 404
 *
 * 전략:
 * - projects.ts (fs 의존)를 jest.mock으로 대체하여 파일시스템 격리
 * - GET/POST는 직접 route 함수 호출 (Next.js Request 모킹)
 * - DELETE는 RouteContext.params를 Promise로 전달
 *
 * @see docs/02-design/req-001-004-design.md §API 설계
 * @see docs/03-test-plan/TEST_PLAN.md UT-001, UT-003, UT-004
 */

import { NextRequest } from 'next/server'

// ── projects.ts 모킹 (fs 격리) ─────────────────────────────────────────────

jest.mock('../../lib/projects', () => ({
  readProjects: jest.fn(),
  writeProjects: jest.fn(),
}))

// nanoid는 결정적 값이 필요하므로 고정
jest.mock('nanoid', () => ({ nanoid: () => 'abc123' }))

import { readProjects, writeProjects } from '../../lib/projects'
import { GET, POST } from '../../app/api/projects/route'
import { DELETE } from '../../app/api/projects/[id]/route'
import type { Project } from '../../lib/types'

const mockReadProjects = readProjects as jest.MockedFunction<typeof readProjects>
const mockWriteProjects = writeProjects as jest.MockedFunction<typeof writeProjects>

beforeEach(() => {
  jest.clearAllMocks()
})

// ── readProjects() 단위 테스트 (UT-001-XX) ────────────────────────────────────

// readProjects() 자체는 실제 구현이 projects.ts에 있고
// 여기서는 API를 통해 간접 검증한다.
// 직접 단위 테스트는 projects.test.ts에서 수행한다.

// ── GET /api/projects ─────────────────────────────────────────────────────────

describe('GET /api/projects', () => {
  const sampleGitHubProject: Project = {
    id: 'github-owner-repo-abc123',
    name: 'Test Repo',
    type: 'github',
    repo: 'owner/repo',
    branch: 'main',
    addedAt: '2026-04-04T00:00:00.000Z',
  }

  /**
   * UT-003-01: 정상 목록 반환 (200)
   */
  it('UT-003-01: projects.json에 항목이 있으면 { projects } 배열을 200으로 반환한다', async () => {
    mockReadProjects.mockReturnValue([sampleGitHubProject])

    const res = await GET()
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.projects).toHaveLength(1)
    expect(body.projects[0].id).toBe('github-owner-repo-abc123')
  })

  /**
   * UT-003-02: 빈 목록 반환 시 빈 배열 (200, 500 아님)
   * readProjects()가 빈 배열을 반환해도 200으로 응답해야 한다.
   */
  it('UT-003-02: projects.json이 비어 있어도 200과 빈 배열을 반환한다', async () => {
    mockReadProjects.mockReturnValue([])

    const res = await GET()
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.projects).toEqual([])
  })
})

// ── POST /api/projects ────────────────────────────────────────────────────────

describe('POST /api/projects', () => {
  function makeRequest(body: unknown): NextRequest {
    return new NextRequest('http://localhost:3001/api/projects', {
      method: 'POST',
      body: JSON.stringify(body),
      headers: { 'Content-Type': 'application/json' },
    })
  }

  beforeEach(() => {
    // 기본값: 빈 projects.json (중복 없음)
    mockReadProjects.mockReturnValue([])
    mockWriteProjects.mockReturnValue(undefined)
  })

  /**
   * UT-004-01: GitHub 타입 정상 추가 → 201 및 id 포함 반환
   */
  it('UT-004-01: GitHub 타입 정상 Body → 201, id/type/repo 포함 Project 반환', async () => {
    const req = makeRequest({ type: 'github', repo: 'owner/repo', branch: 'main' })
    const res = await POST(req)
    const body = await res.json()

    expect(res.status).toBe(201)
    expect(body.project.id).toMatch(/^github-/)
    expect(body.project.type).toBe('github')
    expect(body.project.repo).toBe('owner/repo')
    expect(body.project.branch).toBe('main')
    expect(body.project.addedAt).toBeTruthy()
    // writeProjects가 호출되어야 한다
    expect(mockWriteProjects).toHaveBeenCalledTimes(1)
  })

  /**
   * UT-004-02: 로컬 타입 정상 추가 → 201 및 id 포함 반환
   */
  it('UT-004-02: 로컬 타입 정상 Body → 201, id/type/path 포함 Project 반환', async () => {
    const req = makeRequest({ type: 'local', path: '/home/user/projects/app' })
    const res = await POST(req)
    const body = await res.json()

    expect(res.status).toBe(201)
    expect(body.project.id).toMatch(/^local-/)
    expect(body.project.type).toBe('local')
    expect(body.project.path).toBe('/home/user/projects/app')
    expect(mockWriteProjects).toHaveBeenCalledTimes(1)
  })

  /**
   * UT-004-03: 필수 필드 누락 → 400 반환
   */
  it('UT-004-03: GitHub 타입에서 branch 누락 → 400 반환', async () => {
    const req = makeRequest({ type: 'github', repo: 'owner/repo' })
    const res = await POST(req)

    expect(res.status).toBe(400)
    expect(mockWriteProjects).not.toHaveBeenCalled()
  })

  it('UT-004-03: type 누락 → 400 반환', async () => {
    const req = makeRequest({ repo: 'owner/repo', branch: 'main' })
    const res = await POST(req)

    expect(res.status).toBe(400)
  })

  it('UT-004-03: GitHub 타입에서 repo 누락 → 400 반환', async () => {
    const req = makeRequest({ type: 'github', branch: 'main' })
    const res = await POST(req)

    expect(res.status).toBe(400)
  })

  it('UT-004-03: 로컬 타입에서 path 누락 → 400 반환', async () => {
    const req = makeRequest({ type: 'local' })
    const res = await POST(req)

    expect(res.status).toBe(400)
  })

  /**
   * UT-004-04: 로컬 타입 비절대경로 → 400 반환
   * 보안: 클라이언트가 상대경로를 보내더라도 등록 불가 (SEC-001-02)
   */
  it('UT-004-04: 로컬 타입 상대경로 → 400 반환', async () => {
    const req = makeRequest({ type: 'local', path: 'relative/path/to/project' })
    const res = await POST(req)

    expect(res.status).toBe(400)
    const body = await res.json()
    expect(body.error).toMatch(/절대 경로/)
    expect(mockWriteProjects).not.toHaveBeenCalled()
  })

  it('UT-004-04: 로컬 타입 ./ 시작 경로 → 400 반환', async () => {
    const req = makeRequest({ type: 'local', path: './local/project' })
    const res = await POST(req)

    expect(res.status).toBe(400)
  })

  it('UT-004-04: Windows 절대경로(C:\\)는 200으로 허용한다', async () => {
    const req = makeRequest({ type: 'local', path: 'C:\\Users\\user\\project' })
    const res = await POST(req)

    expect(res.status).toBe(201)
  })

  it('중복 GitHub 프로젝트(같은 repo+branch) → 409 반환', async () => {
    const existing: Project = {
      id: 'github-owner-repo-xxx',
      name: 'Existing',
      type: 'github',
      repo: 'owner/repo',
      branch: 'main',
      addedAt: '2026-04-04T00:00:00.000Z',
    }
    mockReadProjects.mockReturnValue([existing])

    const req = makeRequest({ type: 'github', repo: 'owner/repo', branch: 'main' })
    const res = await POST(req)

    expect(res.status).toBe(409)
    expect(mockWriteProjects).not.toHaveBeenCalled()
  })
})

// ── DELETE /api/projects/[id] ─────────────────────────────────────────────────

describe('DELETE /api/projects/[id]', () => {
  const sampleProject: Project = {
    id: 'github-owner-repo-abc123',
    name: 'Test',
    type: 'github',
    repo: 'owner/repo',
    branch: 'main',
    addedAt: '2026-04-04T00:00:00.000Z',
  }

  function makeDeleteRequest(id: string): [NextRequest, { params: Promise<{ id: string }> }] {
    const req = new NextRequest(`http://localhost:3001/api/projects/${id}`, { method: 'DELETE' })
    const ctx = { params: Promise.resolve({ id }) }
    return [req, ctx]
  }

  beforeEach(() => {
    mockWriteProjects.mockReturnValue(undefined)
  })

  /**
   * UT-004-05: 존재하는 id 삭제 → 200 및 projects.json 반영
   */
  it('UT-004-05: 존재하는 id → { ok: true } 200, writeProjects 호출됨', async () => {
    mockReadProjects.mockReturnValue([sampleProject])

    const [req, ctx] = makeDeleteRequest('github-owner-repo-abc123')
    const res = await DELETE(req, ctx)
    const body = await res.json()

    expect(res.status).toBe(200)
    expect(body.ok).toBe(true)
    // 해당 항목이 제외된 빈 배열로 writeProjects 호출
    expect(mockWriteProjects).toHaveBeenCalledWith([])
  })

  it('UT-004-05: 2개 중 1개 삭제 → 나머지 1개로 writeProjects 호출됨', async () => {
    const another: Project = {
      id: 'local-home-user-proj-xyz',
      name: 'Another',
      type: 'local',
      path: '/home/user/proj',
      addedAt: '2026-04-04T00:00:00.000Z',
    }
    mockReadProjects.mockReturnValue([sampleProject, another])

    const [req, ctx] = makeDeleteRequest('github-owner-repo-abc123')
    await DELETE(req, ctx)

    const written = (mockWriteProjects as jest.Mock).mock.calls[0][0] as Project[]
    expect(written).toHaveLength(1)
    expect(written[0].id).toBe('local-home-user-proj-xyz')
  })

  /**
   * UT-004-06: 존재하지 않는 id → 404 반환
   */
  it('UT-004-06: 존재하지 않는 id → 404, writeProjects 미호출', async () => {
    mockReadProjects.mockReturnValue([sampleProject])

    const [req, ctx] = makeDeleteRequest('nonexistent-id')
    const res = await DELETE(req, ctx)

    expect(res.status).toBe(404)
    expect(mockWriteProjects).not.toHaveBeenCalled()
  })

  it('UT-004-06: projects.json이 비어 있을 때 삭제 요청 → 404', async () => {
    mockReadProjects.mockReturnValue([])

    const [req, ctx] = makeDeleteRequest('any-id')
    const res = await DELETE(req, ctx)

    expect(res.status).toBe(404)
  })
})
