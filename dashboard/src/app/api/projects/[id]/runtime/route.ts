/**
 * @file api/projects/[id]/runtime/route.ts
 * @description GET /api/projects/[id]/runtime API Route
 *
 * 프로젝트의 vulcan.config.json runtime.available_runners를 읽어
 * 대시보드가 사용 가능한 Codex/Claude runner 현황을 표시할 수 있게 한다.
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
    dataSource = createDataSource(project)
  } catch (err) {
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '데이터 소스 초기화 실패' }, { status: 500 })
  }

  try {
    const runtime = await dataSource.getRuntime()
    return NextResponse.json({ runtime, fetchedAt: new Date().toISOString() })
  } catch (err) {
    if (err instanceof PathTraversalError) {
      return NextResponse.json({ error: 'Path Traversal 시도가 감지되었습니다' }, { status: 403 })
    }
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '런타임 설정 조회 실패' }, { status: 500 })
  }
}
