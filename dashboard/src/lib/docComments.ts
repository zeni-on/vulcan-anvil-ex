import fs from 'node:fs'
import path from 'node:path'
import {
  DOC_COMMENT_CATEGORIES,
  DOC_COMMENT_STATUSES,
  type DocComment,
  type DocCommentCategory,
  type DocCommentStatus,
} from './docCommentTypes'
import type { LocalProject } from './types'
import { assertPathInside } from './pathSecurity'

const COMMENTS_RELATIVE_PATH = path.join('.vulcan', 'comments', 'comments.jsonl')

export class InvalidCommentPathError extends Error {
  constructor(documentPath: string) {
    super(`Invalid document path: ${documentPath}`)
    this.name = 'InvalidCommentPathError'
  }
}

export function normalizeCommentDocumentPath(documentPath: string): string {
  const normalized = documentPath.replace(/\\/g, '/').trim()
  if (
    !normalized ||
    normalized.includes('\0') ||
    normalized.startsWith('/') ||
    /^[A-Za-z]:/.test(normalized) ||
    normalized.split('/').some((segment) => segment === '..' || segment === '.')
  ) {
    throw new InvalidCommentPathError(documentPath)
  }
  if (!normalized.toLowerCase().endsWith('.md')) {
    throw new InvalidCommentPathError(documentPath)
  }
  return normalized
}

export function isDocCommentCategory(value: unknown): value is DocCommentCategory {
  return DOC_COMMENT_CATEGORIES.includes(value as DocCommentCategory)
}

export function isDocCommentStatus(value: unknown): value is DocCommentStatus {
  return DOC_COMMENT_STATUSES.includes(value as DocCommentStatus)
}

function normalizeDocCommentStatus(value: unknown): DocCommentStatus {
  if (value === 'closed') return 'closed'
  if (value === 'resolved' || value === 'converted' || value === 'stale') return 'closed'
  return 'open'
}

function commentsFilePath(project: LocalProject): string {
  return assertPathInside(project.path, path.join(project.path, COMMENTS_RELATIVE_PATH))
}

function safeParseComment(line: string): DocComment | null {
  try {
    const parsed = JSON.parse(line) as Partial<DocComment>
    if (
      typeof parsed.comment_id !== 'string' ||
      typeof parsed.document !== 'string' ||
      typeof parsed.body !== 'string' ||
      !isDocCommentCategory(parsed.category) ||
      !parsed.anchor ||
      parsed.anchor.type !== 'line_range' ||
      typeof parsed.anchor.start_line !== 'number' ||
      typeof parsed.anchor.end_line !== 'number' ||
      typeof parsed.anchor.selected_text !== 'string'
    ) {
      return null
    }
    return { ...(parsed as DocComment), status: normalizeDocCommentStatus(parsed.status) }
  } catch {
    return null
  }
}

export function readDocComments(project: LocalProject, documentPath?: string): DocComment[] {
  const filePath = commentsFilePath(project)
  if (!fs.existsSync(filePath)) return []

  const normalizedFilter = documentPath ? normalizeCommentDocumentPath(documentPath) : undefined
  const raw = fs.readFileSync(filePath, 'utf-8')
  return raw
    .split(/\r?\n/)
    .filter(Boolean)
    .map(safeParseComment)
    .filter((comment): comment is DocComment => Boolean(comment))
    .filter((comment) => !normalizedFilter || comment.document === normalizedFilter)
}

export function appendDocComment(project: LocalProject, comment: DocComment): void {
  const filePath = commentsFilePath(project)
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  fs.appendFileSync(filePath, `${JSON.stringify(comment)}\n`, 'utf-8')
}

export function updateDocCommentStatus(
  project: LocalProject,
  commentId: string,
  status: DocCommentStatus,
): DocComment | null {
  const filePath = commentsFilePath(project)
  if (!fs.existsSync(filePath)) return null

  const comments = readDocComments(project)
  let updated: DocComment | null = null
  const now = new Date().toISOString()
  const nextComments = comments.map((comment) => {
    if (comment.comment_id !== commentId) return comment
    updated = { ...comment, status, updated_at: now }
    return updated
  })
  if (!updated) return null

  const tmpPath = `${filePath}.tmp`
  fs.writeFileSync(
    tmpPath,
    nextComments.map((comment) => JSON.stringify(comment)).join('\n') + '\n',
    'utf-8',
  )
  fs.renameSync(tmpPath, filePath)
  return updated
}
