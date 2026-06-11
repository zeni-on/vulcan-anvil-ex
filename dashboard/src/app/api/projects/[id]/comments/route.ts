import { randomUUID } from 'node:crypto'
import { NextResponse } from 'next/server'
import { readProjects } from '@/lib/projects'
import {
  appendDocComment,
  InvalidCommentPathError,
  isDocCommentCategory,
  isDocCommentStatus,
  normalizeCommentDocumentPath,
  readDocComments,
  updateDocCommentStatus,
} from '@/lib/docComments'
import type { DocComment } from '@/lib/docCommentTypes'

interface RouteContext {
  params: Promise<{ id: string }>
}

function findLocalProject(id: string) {
  const project = readProjects().find((item) => item.id === id)
  if (!project) {
    return { error: NextResponse.json({ error: 'Project not found' }, { status: 404 }) }
  }
  if (project.type !== 'local') {
    return { error: NextResponse.json({ error: 'Comments are supported for local projects only' }, { status: 400 }) }
  }
  return { project }
}

function normalizeLineRange(startLine: unknown, endLine: unknown) {
  const start = Number(startLine)
  const end = Number(endLine ?? startLine)
  if (!Number.isInteger(start) || !Number.isInteger(end) || start < 1 || end < start) {
    return null
  }
  return { start, end }
}

export async function GET(req: Request, ctx: RouteContext) {
  const { id } = await ctx.params
  const lookup = findLocalProject(id)
  if (!lookup.project) return lookup.error

  const url = new URL(req.url)
  const documentPath = url.searchParams.get('document') ?? undefined
  try {
    const comments = readDocComments(lookup.project, documentPath)
    return NextResponse.json({ comments, fetchedAt: new Date().toISOString() })
  } catch (err) {
    if (err instanceof InvalidCommentPathError) {
      return NextResponse.json({ error: 'Invalid document path' }, { status: 400 })
    }
    return NextResponse.json({ error: 'Failed to read comments' }, { status: 503 })
  }
}

export async function POST(req: Request, ctx: RouteContext) {
  const { id } = await ctx.params
  const lookup = findLocalProject(id)
  if (!lookup.project) return lookup.error

  try {
    const payload = (await req.json()) as Record<string, unknown>
    const documentPath = normalizeCommentDocumentPath(String(payload.document ?? ''))
    const lineRange = normalizeLineRange(payload.start_line, payload.end_line)
    const body = String(payload.body ?? '').trim()
    const selectedText = String(payload.selected_text ?? '').slice(0, 1200)
    const category = payload.category

    if (!lineRange) {
      return NextResponse.json({ error: 'Invalid line range' }, { status: 400 })
    }
    if (!isDocCommentCategory(category)) {
      return NextResponse.json({ error: 'Invalid category' }, { status: 400 })
    }
    if (!body || body.length > 4000) {
      return NextResponse.json({ error: 'Invalid comment body' }, { status: 400 })
    }

    const now = new Date().toISOString()
    const comment: DocComment = {
      comment_id: `CMT-${now.slice(0, 10).replace(/-/g, '')}-${randomUUID().slice(0, 8)}`,
      document: documentPath,
      anchor: {
        type: 'line_range',
        start_line: lineRange.start,
        end_line: lineRange.end,
        selected_text: selectedText,
        heading: typeof payload.heading === 'string' ? payload.heading.slice(0, 200) : undefined,
      },
      category,
      body,
      status: 'open',
      created_by: 'user',
      created_at: now,
      updated_at: now,
    }

    appendDocComment(lookup.project, comment)
    return NextResponse.json({ comment }, { status: 201 })
  } catch (err) {
    if (err instanceof InvalidCommentPathError) {
      return NextResponse.json({ error: 'Invalid document path' }, { status: 400 })
    }
    return NextResponse.json({ error: 'Failed to create comment' }, { status: 503 })
  }
}

export async function PATCH(req: Request, ctx: RouteContext) {
  const { id } = await ctx.params
  const lookup = findLocalProject(id)
  if (!lookup.project) return lookup.error

  try {
    const payload = (await req.json()) as Record<string, unknown>
    const commentId = String(payload.comment_id ?? '').trim()
    const status = payload.status
    if (!commentId || !isDocCommentStatus(status)) {
      return NextResponse.json({ error: 'Invalid status update' }, { status: 400 })
    }
    const comment = updateDocCommentStatus(lookup.project, commentId, status)
    if (!comment) {
      return NextResponse.json({ error: 'Comment not found' }, { status: 404 })
    }
    return NextResponse.json({ comment })
  } catch {
    return NextResponse.json({ error: 'Failed to update comment' }, { status: 503 })
  }
}
