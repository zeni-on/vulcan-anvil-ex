/**
 * @file __tests__/datasource/github.test.ts
 * @description GitHubDataSource 단위 테스트
 *
 * 커버 UT-ID:
 * - UT-002-01: 정상 응답 Base64 디코드 및 JSON 파싱
 * - UT-002-02: GitHub API 404 응답 시 DataSourceError throw
 * - UT-002-03: limit 파라미터가 per_page 쿼리로 전달됨
 * - UT-002-08: type='github' → GitHubDataSource 인스턴스 반환
 * - UT-002-09: type='local' → LocalDataSource 인스턴스 반환
 *
 * @see docs/02-design/req-001-004-design.md §GitHubDataSource
 * @see docs/03-test-plan/TEST_PLAN.md UT-002-01~03, UT-002-08~09
 */

import { GitHubDataSource } from '../../lib/datasource/github'
import { LocalDataSource } from '../../lib/datasource/local'
import { createDataSource } from '../../lib/datasource/index'
import { DataSourceError } from '../../lib/types'
import type { GitHubProject, LocalProject } from '../../lib/types'

// ── fetch 모킹 ────────────────────────────────────────────────────────────────

const mockFetch = jest.fn()
global.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockReset()
})

// ── 테스트 픽스처 ─────────────────────────────────────────────────────────────

const VALID_SESSION = {
  project: 'TestProject',
  vulcan_version: '1.0.0',
  current_gate: 'gate2',
  gate_status: {
    gate1: 'done',
    gate2: 'pending',
    gate3: 'pending',
    impl: 'pending',
    gate4: 'pending',
    gate5: 'pending',
  },
  feature: '테스트 기능',
  started: '2026-04-04',
  completed: ['Gate 1 완료'],
  pending: [],
  blocked: [],
}

/** Base64 인코딩 헬퍼 */
function toBase64(obj: unknown): string {
  return Buffer.from(JSON.stringify(obj)).toString('base64')
}

/** 성공 fetch 응답 생성 헬퍼 */
function mockSuccess(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    json: () => Promise.resolve(body),
  } as Response
}

/** 실패 fetch 응답 생성 헬퍼 */
function mockFailure(status: number, statusText: string): Response {
  return {
    ok: false,
    status,
    statusText,
    json: () => Promise.resolve({ message: statusText }),
  } as Response
}

// ── GitHubDataSource 생성자 ───────────────────────────────────────────────────

describe('GitHubDataSource 생성자', () => {
  it('token이 비어 있으면 DataSourceError를 throw한다', () => {
    expect(() => {
      new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: '' })
    }).toThrow(DataSourceError)
  })

  it('유효한 config로 생성 시 인스턴스가 반환된다', () => {
    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'tok' })
    expect(ds).toBeInstanceOf(GitHubDataSource)
  })
})

// ── UT-002-01: 정상 응답 Base64 디코드 및 JSON 파싱 ──────────────────────────

describe('UT-002-01: GitHubDataSource.getSession() — 정상 Base64 디코드 및 JSON 파싱', () => {
  it('GitHub API 정상 응답을 Base64 디코드하여 SessionData로 반환한다', async () => {
    const encoded = toBase64(VALID_SESSION)
    mockFetch.mockResolvedValueOnce(
      mockSuccess({ content: encoded, encoding: 'base64' })
    )

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'test-token' })
    const result = await ds.getSession()

    expect(result).not.toBeNull()
    expect(result?.project).toBe('TestProject')
    expect(result?.current_gate).toBe('gate2')
    expect(result?.gate_status.gate1).toBe('done')

    // fetch가 올바른 URL로 호출되었는지 확인
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/repos/owner/repo/contents/session.json'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
        }),
      })
    )
  })

  it('branch 파라미터가 ref 쿼리로 전달된다', async () => {
    const encoded = toBase64(VALID_SESSION)
    mockFetch.mockResolvedValueOnce(
      mockSuccess({ content: encoded, encoding: 'base64' })
    )

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'develop', token: 'tok' })
    await ds.getSession()

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('ref=develop'),
      expect.any(Object)
    )
  })
})

// ── UT-002-02: GitHub API 404 응답 시 DataSourceError throw ──────────────────

describe('UT-002-02: GitHubDataSource.getSession() — GitHub API 404 시 DataSourceError', () => {
  it('GitHub API가 404를 반환하면 DataSourceError를 throw한다', async () => {
    mockFetch.mockResolvedValueOnce(mockFailure(404, 'Not Found'))

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'tok' })

    await expect(ds.getSession()).rejects.toThrow(DataSourceError)
  })

  it('GitHub API가 500을 반환하면 DataSourceError를 throw한다', async () => {
    mockFetch.mockResolvedValueOnce(mockFailure(500, 'Internal Server Error'))

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'tok' })

    await expect(ds.getSession()).rejects.toThrow(DataSourceError)
  })

  it('DataSourceError 메시지에 HTTP 상태 코드가 포함된다', async () => {
    mockFetch.mockResolvedValueOnce(mockFailure(404, 'Not Found'))

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'tok' })

    try {
      await ds.getSession()
      fail('DataSourceError가 throw되어야 함')
    } catch (err) {
      expect(err).toBeInstanceOf(DataSourceError)
      expect((err as DataSourceError).message).toContain('404')
    }
  })
})

// ── UT-002-03: limit 파라미터가 per_page 쿼리로 전달됨 ───────────────────────

describe('UT-002-03: GitHubDataSource.getCommits() — limit이 per_page로 전달됨', () => {
  it('limit=10이면 per_page=10 쿼리가 GitHub API URL에 포함된다', async () => {
    mockFetch.mockResolvedValueOnce(mockSuccess([
      {
        sha: 'abc123',
        commit: {
          message: 'feat: 테스트 커밋',
          author: { name: 'testuser', date: '2026-04-04T00:00:00Z' },
        },
      },
    ]))

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'tok' })
    const commits = await ds.getCommits(10)

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('per_page=10'),
      expect.any(Object)
    )
    expect(commits).toHaveLength(1)
    expect(commits[0].sha).toBe('abc123')
    expect(commits[0].message).toBe('feat: 테스트 커밋')
    expect(commits[0].author).toBe('testuser')
  })

  it('limit=5이면 per_page=5 쿼리가 GitHub API URL에 포함된다', async () => {
    mockFetch.mockResolvedValueOnce(mockSuccess([]))

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'main', token: 'tok' })
    await ds.getCommits(5)

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('per_page=5'),
      expect.any(Object)
    )
  })

  it('sha 파라미터에 branch 값이 포함된다', async () => {
    mockFetch.mockResolvedValueOnce(mockSuccess([]))

    const ds = new GitHubDataSource({ repo: 'owner/repo', branch: 'develop', token: 'tok' })
    await ds.getCommits(10)

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('sha=develop'),
      expect.any(Object)
    )
  })
})

// ── UT-002-08: createDataSource — type='github' → GitHubDataSource 반환 ──────

describe('UT-002-08: createDataSource() — type=github 시 GitHubDataSource 반환', () => {
  it('type=github인 Project를 전달하면 GitHubDataSource 인스턴스를 반환한다', () => {
    // GITHUB_TOKEN 환경변수 설정
    const original = process.env.GITHUB_TOKEN
    process.env.GITHUB_TOKEN = 'test-token'

    const project: GitHubProject = {
      id: 'github-owner-repo',
      name: 'TestProject',
      type: 'github',
      repo: 'owner/repo',
      branch: 'main',
      addedAt: '2026-04-04T00:00:00.000Z',
    }

    const ds = createDataSource(project)
    expect(ds).toBeInstanceOf(GitHubDataSource)

    process.env.GITHUB_TOKEN = original
  })

  it('GITHUB_TOKEN 미설정 시 DataSourceError를 throw한다', () => {
    const original = process.env.GITHUB_TOKEN
    delete process.env.GITHUB_TOKEN

    const project: GitHubProject = {
      id: 'github-owner-repo',
      name: 'TestProject',
      type: 'github',
      repo: 'owner/repo',
      branch: 'main',
      addedAt: '2026-04-04T00:00:00.000Z',
    }

    expect(() => createDataSource(project)).toThrow(DataSourceError)

    process.env.GITHUB_TOKEN = original
  })
})

// ── UT-002-09: createDataSource — type='local' → LocalDataSource 반환 ────────

describe('UT-002-09: createDataSource() — type=local 시 LocalDataSource 반환', () => {
  it('type=local인 Project를 전달하면 LocalDataSource 인스턴스를 반환한다', () => {
    const project: LocalProject = {
      id: 'local-Users-julyi-projects-my-app',
      name: 'MyLocalProject',
      type: 'local',
      path: '/Users/julyi/projects/my-app',
      addedAt: '2026-04-04T00:00:00.000Z',
    }

    const ds = createDataSource(project)
    expect(ds).toBeInstanceOf(LocalDataSource)
  })
})
