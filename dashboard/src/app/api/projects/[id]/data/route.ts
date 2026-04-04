/**
 * @file api/projects/[id]/data/route.ts
 * @description GET /api/projects/[id]/data API Route
 *
 * projects.json에서 id로 프로젝트를 찾아 DataSource를 통해
 * session, docs, commits를 병렬 패치하여 ProjectData로 반환한다.
 *
 * 에러 케이스:
 * - id 미존재 → 404
 * - DataSourceError (GITHUB_TOKEN 미설정 등) → 503
 * - PathTraversalError → 403
 *
 * 보안:
 * - 경로는 항상 projects.json의 등록 항목에서만 참조 (SEC-001-02)
 * - GITHUB_TOKEN은 서버사이드에서만 사용, 응답에 미포함 (SEC-001-01)
 *
 * UT-004-07: 존재하는 프로젝트 → ProjectData 반환 (200)
 * UT-004-08: 존재하지 않는 id → 404
 * UT-004-09: GITHUB_TOKEN 미설정 GitHub 프로젝트 → 503
 *
 * @see docs/02-design/req-001-004-design.md §GET /api/projects/[id]/data
 */

import { NextRequest, NextResponse } from 'next/server'
import { readProjects } from '@/lib/projects'
import { createDataSource } from '@/lib/datasource'
import { DataSourceError, PathTraversalError, ProjectData } from '@/lib/types'

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
    // DataSourceError: GITHUB_TOKEN 미설정 시 throw (UT-004-09)
    dataSource = createDataSource(project)
  } catch (err) {
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '데이터 소스 초기화 실패' }, { status: 500 })
  }

  // 세 가지 데이터를 병렬 패치 — 하나 실패해도 나머지는 반환 (설계 §5-4)
  const [sessionResult, docsResult, commitsResult] = await Promise.allSettled([
    dataSource.getSession(),
    dataSource.getDocTree(),
    dataSource.getCommits(10),
  ])

  // PathTraversalError는 403으로 변환
  const traversalError = [sessionResult, docsResult, commitsResult].find(
    (r) => r.status === 'rejected' && r.reason instanceof PathTraversalError,
  )
  if (traversalError) {
    return NextResponse.json({ error: 'Path Traversal 시도가 감지되었습니다' }, { status: 403 })
  }

  // DataSourceError (GitHub API 오류 등)는 503으로 변환
  const sourceError = [sessionResult, docsResult, commitsResult].find(
    (r) => r.status === 'rejected' && r.reason instanceof DataSourceError,
  )
  if (sourceError && sourceError.status === 'rejected') {
    return NextResponse.json({ error: sourceError.reason.message }, { status: 503 })
  }

  const projectData: ProjectData = {
    session: sessionResult.status === 'fulfilled' ? sessionResult.value : null,
    docs: docsResult.status === 'fulfilled' ? docsResult.value : [],
    commits: commitsResult.status === 'fulfilled' ? commitsResult.value : [],
    fetchedAt: new Date().toISOString(),
  }

  return NextResponse.json(projectData)
}
