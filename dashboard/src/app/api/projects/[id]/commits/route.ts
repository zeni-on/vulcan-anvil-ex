/**
 * @file api/projects/[id]/commits/route.ts
 * @description GET /api/projects/[id]/commits API Route
 *
 * projects.json에서 id로 프로젝트를 찾아 DataSource를 통해
 * 최근 커밋 이력(최대 10개)을 CommitEntry[]로 반환한다.
 *
 * git log 실패(비 git 폴더 등) 시 빈 배열 200 반환 — 커밋 없음은 에러가 아니다.
 *
 * 에러 케이스:
 * - id 미존재 → 404
 * - PathTraversalError → 403 (SEC-002-02)
 * - DataSourceError (GITHUB_TOKEN 미설정 등) → 503
 * - git log 실패 → 빈 배열 200 (UT-005-07)
 *
 * UT-005-06: 로컬 git log 정상 → CommitEntry[] 반환 (200)
 * UT-005-07: git log 실패(비git 폴더) → 빈 배열 200 반환
 * UT-005-08: GitHub 모드 → API 호출로 CommitEntry[] 반환
 *
 * @see docs/02-design/req-005-009-design.md §GET /api/projects/[id]/commits
 */

import { NextRequest, NextResponse } from 'next/server'
import { readProjects } from '@/lib/projects'
import { createDataSource } from '@/lib/datasource'
import { DataSourceError, PathTraversalError } from '@/lib/types'

type RouteContext = { params: Promise<{ id: string }> }

export async function GET(
  _req: NextRequest,
  { params }: RouteContext,
): Promise<NextResponse> {
  const { id } = await params
  const projects = readProjects()

  const project = projects.find((p) => p.id === id)
  if (!project) {
    return NextResponse.json({ error: '프로젝트를 찾을 수 없습니다' }, { status: 404 })
  }

  let dataSource
  try {
    // DataSourceError: GITHUB_TOKEN 미설정 시 throw (REQ-009-02)
    dataSource = createDataSource(project)
  } catch (err) {
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '데이터 소스 초기화 실패' }, { status: 500 })
  }

  try {
    // LocalDataSource는 git log 실패 시 내부에서 빈 배열 반환 — 에러 아님 (UT-005-07)
    const commits = await dataSource.getCommits(10)
    return NextResponse.json({ commits, fetchedAt: new Date().toISOString() })
  } catch (err) {
    // PathTraversalError는 403으로 변환 (SEC-002-02, REQ-009-03)
    if (err instanceof PathTraversalError) {
      return NextResponse.json({ error: 'Path Traversal 시도가 감지되었습니다' }, { status: 403 })
    }
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '커밋 이력 조회 실패' }, { status: 500 })
  }
}
