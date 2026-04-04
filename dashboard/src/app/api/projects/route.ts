/**
 * @file api/projects/route.ts
 * @description GET /api/projects, POST /api/projects API Route
 *
 * GET: projects.json 목록 조회 → { projects: Project[] }
 * POST: 프로젝트 추가 → { project: Project } (201)
 *
 * name은 session.json의 project 필드에서 자동 결정한다.
 * session.json 읽기 실패 시 fallback: repo명(GitHub) 또는 폴더명(로컬)
 *
 * 보안:
 * - GITHUB_TOKEN은 클라이언트에 절대 반환하지 않는다 (REQ-009-02, SEC-001-01)
 * - 로컬 path는 projects.json에서 id 기반으로만 조회 (SEC-001-02)
 * - Atomic Write로 파일 손상 방지 (req-data-design.md §5-1)
 *
 * @see docs/02-design/req-001-004-design.md §GET /api/projects, §POST /api/projects
 */

import { NextRequest, NextResponse } from 'next/server'
import { nanoid } from 'nanoid'
import { readProjects, writeProjects } from '@/lib/projects'
import { createDataSource } from '@/lib/datasource'
import { Project, DataSourceError } from '@/lib/types'

/** projects.json 읽어 전체 목록 반환. 파일 오류 시 빈 배열로 폴백 (UT-003-01, UT-003-02) */
export function GET(): NextResponse {
  const projects = readProjects()
  return NextResponse.json({ projects })
}

/**
 * 요청 Body에서 프로젝트 추가.
 * GitHub 타입: { type, repo, branch }
 * 로컬 타입: { type, path }
 *
 * name은 session.json의 project 필드에서 자동 결정한다.
 * session.json 읽기 실패 시 fallback: repo명(GitHub) 또는 폴더명(로컬)
 */
export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: '요청 바디 파싱 실패' }, { status: 400 })
  }

  const parsed = parseAddProjectBody(body)
  if ('error' in parsed) {
    return NextResponse.json({ error: parsed.error }, { status: 400 })
  }

  // session.json에서 프로젝트 이름을 자동 결정
  const name = await resolveProjectName(parsed.value)
  const newProject = buildProject({ ...parsed.value, name })

  const existing = readProjects()

  // 중복 등록 방지 (req-data-design.md §6)
  const duplicate = findDuplicate(existing, newProject)
  if (duplicate) {
    return NextResponse.json({ error: '이미 등록된 프로젝트입니다' }, { status: 409 })
  }

  writeProjects([...existing, newProject])

  return NextResponse.json({ project: newProject }, { status: 201 })
}

// ── 내부 헬퍼 ────────────────────────────────────────────────────────────────

type ParseResult<T> = { value: T } | { error: string }

type AddProjectInput =
  | { type: 'github'; repo: string; branch: string }
  | { type: 'local'; path: string }

type AddProjectBody =
  | { type: 'github'; name: string; repo: string; branch: string }
  | { type: 'local'; name: string; path: string }

/** 요청 바디를 검증하여 AddProjectInput을 반환한다. (name 불필요) */
function parseAddProjectBody(body: unknown): ParseResult<AddProjectInput> {
  if (typeof body !== 'object' || body === null) {
    return { error: '요청 바디가 객체가 아닙니다' }
  }

  const b = body as Record<string, unknown>

  if (b.type === 'github') {
    return parseGitHubBody(b)
  }

  if (b.type === 'local') {
    return parseLocalBody(b)
  }

  return { error: 'type은 "github" 또는 "local" 이어야 합니다' }
}

function parseGitHubBody(b: Record<string, unknown>): ParseResult<AddProjectInput> {
  if (typeof b.repo !== 'string' || b.repo.trim() === '') {
    return { error: 'GitHub 타입: repo 필드가 누락되었거나 비어 있습니다' }
  }
  if (!/^[^/]+\/[^/]+$/.test(b.repo)) {
    return { error: 'GitHub 타입: repo는 "owner/repo" 형식이어야 합니다' }
  }
  if (typeof b.branch !== 'string' || b.branch.trim() === '') {
    return { error: 'GitHub 타입: branch 필드가 누락되었거나 비어 있습니다' }
  }
  return {
    value: {
      type: 'github',
      repo: b.repo.trim(),
      branch: b.branch.trim(),
    },
  }
}

function parseLocalBody(b: Record<string, unknown>): ParseResult<AddProjectInput> {
  if (typeof b.path !== 'string' || b.path.trim() === '') {
    return { error: '로컬 타입: path 필드가 누락되었거나 비어 있습니다' }
  }
  // 절대경로 검증: Unix(/로 시작) 또는 Windows(드라이브 문자 C:\)
  if (!isAbsolutePath(b.path)) {
    return { error: '로컬 타입: path는 절대 경로여야 합니다' }
  }
  return {
    value: {
      type: 'local',
      path: b.path.trim(),
    },
  }
}

/** OS 무관 절대경로 판별 (Unix: / 시작, Windows: 드라이브 문자 시작) */
function isAbsolutePath(p: string): boolean {
  return p.startsWith('/') || /^[A-Za-z]:[\\/]/.test(p)
}

/**
 * session.json의 project 필드에서 프로젝트 이름을 결정한다.
 * 읽기 실패 시 fallback: repo명(GitHub) 또는 폴더명(로컬)
 */
async function resolveProjectName(input: AddProjectInput): Promise<string> {
  // fallback 이름 미리 결정
  const fallback = input.type === 'github'
    ? input.repo.split('/').pop() ?? input.repo
    : input.path.replace(/\\/g, '/').split('/').filter(Boolean).pop() ?? input.path

  try {
    // 임시 Project 객체를 만들어 DataSource로 session.json을 읽는다
    const tempProject: Project = input.type === 'github'
      ? { id: '', name: '', type: 'github', repo: input.repo, branch: input.branch, addedAt: '' }
      : { id: '', name: '', type: 'local', path: input.path, addedAt: '' }

    const ds = createDataSource(tempProject)
    const session = await ds.getSession()
    if (session?.project) {
      return session.project
    }
  } catch (err) {
    // DataSourceError 등 — fallback 사용
    if (err instanceof DataSourceError) {
      console.warn('[resolveProjectName] session.json 읽기 실패, fallback 사용:', err.message)
    }
  }

  return fallback
}

/** AddProjectBody로 Project 객체를 생성한다. ID는 타입+식별자 slug로 결정적 생성 후 nanoid suffix 추가 */
function buildProject(body: AddProjectBody): Project {
  const addedAt = new Date().toISOString()

  if (body.type === 'github') {
    const slug = body.repo.replace('/', '-')
    return {
      id: `github-${slug}-${nanoid(6)}`,
      name: body.name,
      type: 'github',
      repo: body.repo,
      branch: body.branch,
      addedAt,
    }
  }

  // 로컬: 경로 구분자 → '-', 앞 세그먼트 최대 4개 (req-data-design.md §6)
  const segments = body.path.replace(/\\/g, '/').split('/').filter(Boolean).slice(-4)
  const slug = segments.join('-').replace(/[^a-zA-Z0-9-]/g, '-')
  return {
    id: `local-${slug}-${nanoid(6)}`,
    name: body.name,
    type: 'local',
    path: body.path,
    addedAt,
  }
}

/** 동일 repo(GitHub) 또는 동일 path(로컬)가 이미 존재하는지 확인한다. */
function findDuplicate(existing: Project[], newProject: Project): Project | undefined {
  return existing.find((p) => {
    if (p.type !== newProject.type) return false
    if (p.type === 'github' && newProject.type === 'github') {
      return p.repo === newProject.repo && p.branch === newProject.branch
    }
    if (p.type === 'local' && newProject.type === 'local') {
      return p.path === newProject.path
    }
    return false
  })
}
