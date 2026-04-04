/**
 * @file app/api/projects/[id]/docs/[...path]/route.ts
 * @description 특정 .md 파일 내용을 raw 텍스트로 반환하는 API Route
 *
 * GET /api/projects/[id]/docs/[...path]
 *
 * 보안 제약 (SEC-010-01, SEC-010-03):
 * - LocalDataSource.readDocFile()이 assertSafePath()로 Path Traversal을 차단한다.
 * - 응답에는 파일 내용만 포함하며 절대 경로를 노출하지 않는다.
 *
 * @see docs/02-design/req-010-design.md §신규 API Route
 */

import { NextResponse } from 'next/server'
import path from 'path'
import { readProjects } from '@/lib/projects'
import { LocalDataSource } from '@/lib/datasource/local'
import { GitHubDataSource } from '@/lib/datasource/github'
import { PathTraversalError, DataSourceError } from '@/lib/types'

interface RouteContext {
  params: Promise<{ id: string; path: string[] }>
}

export async function GET(_req: Request, ctx: RouteContext) {
  const { id, path: segments } = await ctx.params

  // 1. 프로젝트 조회
  const projects = readProjects()
  const project = projects.find((p: { id: string }) => p.id === id)
  if (!project) {
    return NextResponse.json({ error: 'Project not found' }, { status: 404 })
  }

  // 2. 경로 유효성 — '..' 세그먼트 명시적 거부
  if (segments.some((s) => s === '..' || s === '.')) {
    return NextResponse.json({ error: 'Invalid file path' }, { status: 400 })
  }

  // 3. 상대 경로 조합: 마지막 세그먼트에 .md 확장자 추가
  const last = segments[segments.length - 1]
  const normalizedSegments = [
    ...segments.slice(0, -1),
    last.endsWith('.md') ? last : `${last}.md`,
  ]
  const relPath = path.join(...normalizedSegments)

  // 4. DataSource 선택 및 파일 읽기
  try {
    let content: string

    if (project.type === 'local') {
      const ds = new LocalDataSource({ path: project.path })
      content = await ds.readDocFile(relPath)
    } else {
      const token = process.env.GITHUB_TOKEN ?? ''
      const ds = new GitHubDataSource({ repo: project.repo, branch: project.branch, token })
      content = await ds.readDocFile(relPath)
    }

    return NextResponse.json({ content })
  } catch (err) {
    if (err instanceof PathTraversalError) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 })
    }
    if (err instanceof DataSourceError) {
      // GitHub 404 또는 로컬 ENOENT → 파일 미존재
      const msg = err.message.toLowerCase()
      if (msg.includes('404') || msg.includes('enoent') || msg.includes('not found')) {
        return NextResponse.json({ error: 'File not found' }, { status: 404 })
      }
      return NextResponse.json({ error: 'Failed to read file' }, { status: 503 })
    }
    // 로컬 ENOENT (DataSourceError가 아닌 경우)
    const nodeErr = err as NodeJS.ErrnoException
    if (nodeErr.code === 'ENOENT') {
      return NextResponse.json({ error: 'File not found' }, { status: 404 })
    }
    return NextResponse.json({ error: 'Failed to read file' }, { status: 503 })
  }
}
