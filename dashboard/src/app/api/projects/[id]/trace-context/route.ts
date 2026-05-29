/**
 * @file app/api/projects/[id]/trace-context/route.ts
 * @description 로컬 Vulcan 프로젝트의 trace-context CLI 결과를 반환한다.
 */

import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import { spawnSync } from 'child_process'
import { readProjects } from '@/lib/projects'

interface RouteContext {
  params: Promise<{ id: string }>
}

const TRACE_ID_PATTERN =
  /^(REQ-\d{3}(?:-\d{2})?|NREQ-\d{3}(?:-\d{2})?|AC-\d{3}-\d{2}|FUNC-\d{3}|SCR-\d{3}|UIREF-\d{3}|UICON-\d{3}|API-\d{3}|PGM-\d{3}|IF-\d{3}|MTH-\d{3}|DB-\d{3}|SEC-\d{3}|UT-\d{3}|IT-\d{3}|PT-\d{3}|UI-\d{3}(?:-\d{2})?|EV-[A-Z0-9-]+|FIND-\d{3}|CR-\d{3}|DEC-\d{3}|BL-\d{3}|ISSUE-[A-Z0-9-]+|RUN-\d{3}|RV-\d{3})$/i

function parseDepth(value: string | null): number {
  const parsed = Number.parseInt(value ?? '2', 10)
  if (!Number.isFinite(parsed)) return 2
  return Math.min(4, Math.max(1, parsed))
}

function parseDirection(value: string | null): 'upstream' | 'downstream' | 'both' {
  if (value === 'upstream' || value === 'both') return value
  return 'downstream'
}

export async function GET(req: NextRequest, ctx: RouteContext) {
  const { id } = await ctx.params
  const seed = (req.nextUrl.searchParams.get('id') ?? '').trim().toUpperCase()
  const depth = parseDepth(req.nextUrl.searchParams.get('depth'))
  const direction = parseDirection(req.nextUrl.searchParams.get('direction'))

  if (!TRACE_ID_PATTERN.test(seed)) {
    return NextResponse.json({ error: 'Invalid trace id' }, { status: 400 })
  }

  const project = readProjects().find((item) => item.id === id)
  if (!project) {
    return NextResponse.json({ error: 'Project not found' }, { status: 404 })
  }
  if (project.type !== 'local') {
    return NextResponse.json({ error: 'Trace context is available for local projects only' }, { status: 400 })
  }

  const projectPath = path.resolve(project.path)
  const rootVulcanPath = path.resolve(process.cwd(), '..', 'vulcan.py')
  const projectVulcanPath = path.join(projectPath, 'vulcan.py')
  const vulcanPath = fs.existsSync(rootVulcanPath) ? rootVulcanPath : projectVulcanPath
  if (!fs.existsSync(vulcanPath)) {
    return NextResponse.json({ error: 'vulcan.py not found' }, { status: 404 })
  }

  const result = spawnSync(
    'python',
    [
      vulcanPath,
      'trace-context',
      '--id',
      seed,
      '--depth',
      String(depth),
      '--direction',
      direction,
      '--emit',
      'json',
    ],
    {
      cwd: projectPath,
      encoding: 'utf-8',
      timeout: 10000,
      windowsHide: true,
    },
  )

  if (result.error) {
    return NextResponse.json(
      { error: result.error.message || 'Trace context command failed' },
      { status: 503 },
    )
  }

  if (result.status !== 0) {
    return NextResponse.json(
      {
        error: 'Trace context command failed',
        detail: (result.stderr || result.stdout || '').trim(),
      },
      { status: 500 },
    )
  }

  try {
    return NextResponse.json(JSON.parse(result.stdout))
  } catch {
    return NextResponse.json(
      { error: 'Trace context output was not JSON', detail: result.stdout },
      { status: 500 },
    )
  }
}
