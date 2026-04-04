/**
 * @file api/projects/[id]/route.ts
 * @description DELETE /api/projects/[id] API Route
 *
 * 존재하는 id: projects.json에서 제거 → { ok: true } (200)
 * 존재하지 않는 id: 404 반환
 *
 * 보안:
 * - id를 클라이언트에서 받지만 projects.json의 id 목록과만 대조한다.
 *   경로 조작 불가 (SEC-001-02, REQ-009-03)
 * - Atomic Write로 파일 손상 방지
 *
 * UT-004-05: 존재하는 id → 200, projects.json 반영
 * UT-004-06: 존재하지 않는 id → 404
 *
 * @see docs/02-design/req-001-004-design.md §DELETE /api/projects/[id]
 */

import { NextRequest, NextResponse } from 'next/server'
import { readProjects, writeProjects } from '@/lib/projects'

type RouteContext = { params: Promise<{ id: string }> }

/** id에 해당하는 프로젝트를 projects.json에서 제거한다. */
export async function DELETE(
  _req: NextRequest,
  { params }: RouteContext,
): Promise<NextResponse> {
  const { id } = await params
  const projects = readProjects()

  const index = projects.findIndex((p) => p.id === id)
  if (index === -1) {
    return NextResponse.json({ error: '프로젝트를 찾을 수 없습니다' }, { status: 404 })
  }

  const updated = projects.filter((p) => p.id !== id)
  writeProjects(updated)

  return NextResponse.json({ ok: true })
}
