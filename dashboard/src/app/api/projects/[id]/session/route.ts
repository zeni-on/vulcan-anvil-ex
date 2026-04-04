/**
 * @file api/projects/[id]/session/route.ts
 * @description GET /api/projects/[id]/session API Route
 *
 * projects.json에서 id로 프로젝트를 찾아 DataSource를 통해
 * Gate 상태(session.json)를 읽어 SessionData로 반환한다.
 *
 * 에러 케이스:
 * - id 미존재 → 404
 * - PathTraversalError → 403 (SEC-002-02)
 * - DataSourceError (GITHUB_TOKEN 미설정 등) → 503
 *
 * 보안:
 * - 경로는 항상 projects.json의 등록 항목에서만 참조 (SEC-002-02)
 * - GITHUB_TOKEN은 서버사이드에서만 사용, 응답에 미포함 (SEC-002-01)
 *
 * UT-005-01: 존재하는 id → SessionData 반환 (200)
 * UT-005-02: 존재하지 않는 id → 404
 * UT-005-03: session.json 없음(로컬) → session: null 200 반환
 *
 * @see docs/02-design/req-005-009-design.md §GET /api/projects/[id]/session
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
    const session = await dataSource.getSession()
    return NextResponse.json({ session, fetchedAt: new Date().toISOString() })
  } catch (err) {
    // PathTraversalError는 403으로 변환 (SEC-002-02, REQ-009-03)
    if (err instanceof PathTraversalError) {
      return NextResponse.json({ error: 'Path Traversal 시도가 감지되었습니다' }, { status: 403 })
    }
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '세션 데이터 조회 실패' }, { status: 500 })
  }
}
