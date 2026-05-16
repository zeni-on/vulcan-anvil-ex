import fs from 'fs'
import path from 'path'
import { NextResponse } from 'next/server'
import { readProjects } from '@/lib/projects'

interface RouteContext {
  params: Promise<{ id: string; path: string[] }>
}

const IMAGE_CONTENT_TYPES: Record<string, string> = {
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  webp: 'image/webp',
  gif: 'image/gif',
}

function contentTypeFor(filePath: string): string | null {
  const ext = filePath.split('.').pop()?.toLowerCase() ?? ''
  return IMAGE_CONTENT_TYPES[ext] ?? null
}

function isUnsafeSegment(segment: string): boolean {
  return segment === '..' || segment === '.' || segment.includes('\0')
}

function fallbackEvidencePath(target: string): string | null {
  const dir = path.dirname(target)
  const requestedName = path.basename(target)
  const idMatch = requestedName.match(/^(UI-\d{3})[-_]/i)
  if (!idMatch || !fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) return null

  const prefix = idMatch[1].toLowerCase()
  const fallback = fs
    .readdirSync(dir)
    .find((name) =>
      name.toLowerCase().startsWith(`${prefix}_`) &&
      contentTypeFor(name) !== null,
    )
  return fallback ? path.join(dir, fallback) : null
}

export async function GET(_req: Request, ctx: RouteContext) {
  const { id, path: segments } = await ctx.params
  const projects = readProjects()
  const project = projects.find((p) => p.id === id)

  if (!project) {
    return NextResponse.json({ error: 'Project not found' }, { status: 404 })
  }
  if (segments.length === 0 || segments.some(isUnsafeSegment) || segments[0] !== 'docs') {
    return NextResponse.json({ error: 'Invalid file path' }, { status: 400 })
  }

  const relPath = segments.join('/')
  const contentType = contentTypeFor(relPath)
  if (!contentType) {
    return NextResponse.json({ error: 'Unsupported file type' }, { status: 400 })
  }

  if (project.type === 'local') {
    const projectRoot = path.resolve(project.path)
    const target = path.resolve(projectRoot, relPath)
    const rootWithSep = projectRoot.endsWith(path.sep) ? projectRoot : projectRoot + path.sep

    if (target !== projectRoot && !target.startsWith(rootWithSep)) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 })
    }
    const resolvedTarget = fs.existsSync(target) && fs.statSync(target).isFile()
      ? target
      : fallbackEvidencePath(target)

    if (!resolvedTarget) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 })
    }

    const bytes = fs.readFileSync(resolvedTarget)
    return new NextResponse(bytes, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'no-store',
      },
    })
  }

  const token = process.env.GITHUB_TOKEN ?? ''
  if (!token) {
    return NextResponse.json({ error: 'GITHUB_TOKEN is not configured' }, { status: 503 })
  }

  const url = `https://api.github.com/repos/${project.repo}/contents/${relPath}?ref=${project.branch}`
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    cache: 'no-store',
  })
  if (!res.ok) {
    return NextResponse.json({ error: 'File not found' }, { status: res.status === 404 ? 404 : 503 })
  }

  const data = (await res.json()) as { content?: string; encoding?: string }
  if (!data.content || data.encoding !== 'base64') {
    return NextResponse.json({ error: 'Invalid file response' }, { status: 503 })
  }

  const bytes = Buffer.from(data.content.replace(/\n/g, ''), 'base64')
  return new NextResponse(bytes, {
    headers: {
      'Content-Type': contentType,
      'Cache-Control': 'no-store',
    },
  })
}
