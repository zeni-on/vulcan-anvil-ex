/**
 * @file __tests__/api/read-projects.test.ts
 * @description readProjects() 함수 직접 단위 테스트
 *
 * 커버 UT-ID:
 * - UT-001-01: projects.json 정상 파싱 → Project[] 반환
 * - UT-001-02: 파일 부재 시 빈 배열 반환
 * - UT-001-03: 스키마 오류 항목 제외 후 정상 항목만 반환
 *
 * 전략:
 * - fs 모듈을 jest.mock으로 대체하여 실제 파일 접근 없이 테스트
 *
 * @see docs/02-design/req-001-004-design.md §projects.json 스키마 모듈
 * @see docs/03-test-plan/TEST_PLAN.md UT-001-01~03
 */

import fs from 'fs'

jest.mock('fs')

const mockFs = fs as jest.Mocked<typeof fs>

// process.cwd()는 dashboard/ 디렉토리를 가리킨다고 가정
// readProjects 임포트 전에 모킹이 완료되어야 한다
import { readProjects } from '../../lib/projects'

const VALID_GITHUB_PROJECT = {
  id: 'github-owner-repo',
  name: 'Test Repo',
  type: 'github',
  repo: 'owner/repo',
  branch: 'main',
  addedAt: '2026-04-04T00:00:00.000Z',
}

const VALID_LOCAL_PROJECT = {
  id: 'local-home-user-app',
  name: 'Local App',
  type: 'local',
  path: '/home/user/app',
  addedAt: '2026-04-04T00:00:00.000Z',
}

beforeEach(() => {
  jest.clearAllMocks()
})

/**
 * UT-001-01: projects.json 정상 파싱 → Project[] 반환
 */
describe('UT-001-01: readProjects() 정상 파싱', () => {
  it('유효한 GitHub 프로젝트를 파싱하여 반환한다', () => {
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(JSON.stringify([VALID_GITHUB_PROJECT]))

    const result = readProjects()

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('github-owner-repo')
    expect(result[0].type).toBe('github')
  })

  it('유효한 로컬 프로젝트를 파싱하여 반환한다', () => {
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(JSON.stringify([VALID_LOCAL_PROJECT]))

    const result = readProjects()

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('local-home-user-app')
    expect(result[0].type).toBe('local')
  })

  it('GitHub과 로컬 혼합 목록을 모두 파싱하여 반환한다', () => {
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(
      JSON.stringify([VALID_GITHUB_PROJECT, VALID_LOCAL_PROJECT])
    )

    const result = readProjects()

    expect(result).toHaveLength(2)
  })
})

/**
 * UT-001-02: 파일 부재 시 빈 배열 반환 (REQ-009-06)
 * 500 응답이 아닌 빈 배열로 폴백하여 앱 크래시를 방지한다.
 */
describe('UT-001-02: readProjects() 파일 부재 처리', () => {
  it('projects.json이 없으면 빈 배열을 반환한다', () => {
    mockFs.existsSync.mockReturnValue(false)

    const result = readProjects()

    expect(result).toEqual([])
  })

  it('JSON 파싱 실패 시 빈 배열을 반환한다', () => {
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue('{ invalid json }')

    const result = readProjects()

    expect(result).toEqual([])
  })

  it('최상위 구조가 배열이 아니면 빈 배열을 반환한다', () => {
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(JSON.stringify({ projects: [] }))

    const result = readProjects()

    expect(result).toEqual([])
  })
})

/**
 * UT-001-03: 스키마 오류 항목 제외 후 정상 항목만 반환 (REQ-009-06)
 * 손상된 항목이 있어도 정상 항목은 계속 반환해야 한다.
 */
describe('UT-001-03: readProjects() 스키마 오류 항목 필터링', () => {
  it('type 필드 누락 항목을 제외하고 정상 항목만 반환한다', () => {
    const invalid = { id: 'bad-id', name: 'Bad', addedAt: '2026-04-04T00:00:00.000Z' }
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(
      JSON.stringify([VALID_GITHUB_PROJECT, invalid])
    )

    const result = readProjects()

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('github-owner-repo')
  })

  it('name 필드 빈 문자열 항목을 제외한다', () => {
    const invalid = { ...VALID_GITHUB_PROJECT, id: 'bad-id', name: '' }
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(
      JSON.stringify([VALID_GITHUB_PROJECT, invalid])
    )

    const result = readProjects()

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('github-owner-repo')
  })

  it('addedAt 형식 오류 항목(datetime 아님)을 제외한다', () => {
    const invalid = { ...VALID_LOCAL_PROJECT, id: 'bad-local', addedAt: 'not-a-date' }
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(
      JSON.stringify([VALID_GITHUB_PROJECT, invalid])
    )

    const result = readProjects()

    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('github-owner-repo')
  })

  it('모든 항목이 스키마 오류면 빈 배열을 반환한다', () => {
    const invalid1 = { id: 'x', name: '' }
    const invalid2 = { type: 'unknown', name: 'Bad' }
    mockFs.existsSync.mockReturnValue(true)
    mockFs.readFileSync.mockReturnValue(JSON.stringify([invalid1, invalid2]))

    const result = readProjects()

    expect(result).toEqual([])
  })
})
