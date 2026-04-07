/**
 * @file api/projects/[id]/open-folder/route.ts
 * @description POST /api/projects/[id]/open-folder
 *
 * projects.json에 등록된 local 프로젝트의 docs/ 폴더를 OS 기본 파일 탐색기로 연다.
 * - WSL 환경: wslpath -w로 Linux 경로를 Windows 경로로 변환 후 explorer.exe 실행
 * - 순수 Linux: xdg-open
 * - macOS: open
 * - Windows (네이티브 Node): start
 *
 * 보안:
 * - 등록된 프로젝트 ID로만 동작 (경로를 클라이언트에서 받지 않음)
 * - github 프로젝트는 405 반환
 * - 경로는 항상 등록된 path + 'docs/'로 고정
 */

import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import os from 'os'
import path from 'path'
import { readProjects } from '@/lib/projects'
import { isWSL, openInOS } from '@/lib/openInOS'

type RouteContext = { params: Promise<{ id: string }> }

export async function POST(
  _req: NextRequest,
  { params }: RouteContext,
): Promise<NextResponse> {
  const { id } = await params
  const projects = readProjects()
  const project = projects.find((p) => p.id === id)

  if (!project) {
    return NextResponse.json({ error: '프로젝트를 찾을 수 없습니다' }, { status: 404 })
  }

  if (project.type !== 'local') {
    return NextResponse.json(
      { error: 'GitHub 프로젝트는 로컬 폴더 열기가 지원되지 않습니다' },
      { status: 405 },
    )
  }

  // docs/ 하위만 노출 — 경로는 등록된 project.path 기반으로 고정
  const docsPath = path.join(project.path, 'docs')

  // docs 폴더가 없으면 프로젝트 루트로 폴백
  const target = fs.existsSync(docsPath) ? docsPath : project.path
  if (!fs.existsSync(target)) {
    return NextResponse.json({ error: '경로가 존재하지 않습니다' }, { status: 404 })
  }

  const result = openInOS(target)
  if (!result.ok) {
    return NextResponse.json({ error: `폴더 열기 실패: ${result.error}` }, { status: 500 })
  }

  return NextResponse.json({ ok: true, opened: target, platform: isWSL() ? 'wsl' : os.platform() })
}
