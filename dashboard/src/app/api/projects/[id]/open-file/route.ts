/**
 * @file api/projects/[id]/open-file/route.ts
 * @description POST /api/projects/[id]/open-file
 *
 * 등록된 local 프로젝트의 docs/ 하위 파일을 OS 기본 연결 프로그램으로 연다.
 * (xlsx → Excel, pdf → 기본 PDF 뷰어, hwp → 한글 등)
 *
 * 요청 바디: { path: string } — 'docs/...' 로 시작하는 프로젝트 내부 상대 경로.
 *
 * 보안:
 * - 등록된 project.path만 베이스로 사용 (절대 경로 입력 거부)
 * - path traversal 검증: resolved 결과가 project.path 하위에 있는지 확인
 * - 허용 확장자만 실행 (EXTERNAL_DOC_EXTENSIONS)
 * - github 프로젝트는 405
 */

import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import { readProjects } from '@/lib/projects'
import { openInOS } from '@/lib/openInOS'
import { isExternalDocExt } from '@/lib/types'

type RouteContext = { params: Promise<{ id: string }> }

export async function POST(
  req: NextRequest,
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
      { error: 'GitHub 프로젝트는 외부 파일 열기가 지원되지 않습니다' },
      { status: 405 },
    )
  }

  let body: { path?: unknown }
  try {
    body = (await req.json()) as { path?: unknown }
  } catch {
    return NextResponse.json({ error: '요청 바디가 올바르지 않습니다' }, { status: 400 })
  }

  const relPath = body.path
  if (typeof relPath !== 'string' || relPath.length === 0) {
    return NextResponse.json({ error: 'path 가 필요합니다' }, { status: 400 })
  }

  // 절대 경로/드라이브 문자/널 바이트 거부
  if (
    path.isAbsolute(relPath) ||
    /^[a-zA-Z]:[\\/]/.test(relPath) ||
    relPath.includes('\0')
  ) {
    return NextResponse.json({ error: '잘못된 경로 형식입니다' }, { status: 400 })
  }

  // 확장자 검증
  const dotIdx = relPath.lastIndexOf('.')
  if (dotIdx < 0) {
    return NextResponse.json({ error: '지원하지 않는 파일 형식입니다' }, { status: 400 })
  }
  const ext = relPath.slice(dotIdx + 1).toLowerCase()
  if (!isExternalDocExt(ext)) {
    return NextResponse.json({ error: '지원하지 않는 파일 형식입니다' }, { status: 400 })
  }

  // path traversal 검증: resolved 경로가 project.path 하위인지 확인
  const projectRoot = path.resolve(project.path)
  const resolvedTarget = path.resolve(projectRoot, relPath)
  const projectRootWithSep = projectRoot.endsWith(path.sep)
    ? projectRoot
    : projectRoot + path.sep

  if (
    resolvedTarget !== projectRoot &&
    !resolvedTarget.startsWith(projectRootWithSep)
  ) {
    return NextResponse.json({ error: '경로가 프로젝트 범위를 벗어났습니다' }, { status: 403 })
  }

  if (!fs.existsSync(resolvedTarget) || !fs.statSync(resolvedTarget).isFile()) {
    return NextResponse.json({ error: '파일을 찾을 수 없습니다' }, { status: 404 })
  }

  const result = openInOS(resolvedTarget)
  if (!result.ok) {
    return NextResponse.json({ error: `파일 열기 실패: ${result.error}` }, { status: 500 })
  }

  return NextResponse.json({ ok: true })
}
