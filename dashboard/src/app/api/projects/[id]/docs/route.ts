/**
 * @file api/projects/[id]/docs/route.ts
 * @description GET /api/projects/[id]/docs API Route
 *
 * projects.json에서 id로 프로젝트를 찾아 DataSource를 통해
 * docs/ 디렉토리의 문서 트리를 DocNode[]로 반환한다.
 *
 * 에러 케이스:
 * - id 미존재 → 404
 * - PathTraversalError → 403 (SEC-002-02)
 * - DataSourceError → 503
 *
 * 보안:
 * - 경로는 항상 projects.json의 등록 항목에서만 참조 (SEC-002-02)
 * - GITHUB_TOKEN은 서버사이드에서만 사용, 응답에 미포함 (SEC-002-01)
 * - DocNode의 path는 절대 경로를 반환하지 않는다 (SEC-002-04)
 *
 * UT-005-04: docs/ 경로 파일 목록 → DocNode[] 반환 (200)
 * UT-005-05: docs/ 비어있을 때 → 빈 배열 200 반환
 *
 * @see docs/02-design/req-005-009-design.md §GET /api/projects/[id]/docs
 */

import { NextRequest, NextResponse } from 'next/server'
import { readProjects } from '@/lib/projects'
import { createDataSource } from '@/lib/datasource'
import {
  DataSourceError,
  DocEntry,
  DocNode,
  PathTraversalError,
  isExternalDocExt,
} from '@/lib/types'

type RouteContext = { params: Promise<{ id: string }> }

/**
 * 폴더 경로 접두사로 DocEntry category를 결정한다.
 * UI가 Gate별 그룹 표시를 하기 위한 분류 기준이다.
 */
function resolveCategory(path: string): DocEntry['category'] {
  const normalizedPath = path.toLowerCase()
  const fileName = normalizedPath.split('/').pop() ?? ''

  if (normalizedPath.includes('docs/artifacts/00-discovery/')) return 'discovery'
  if (normalizedPath.includes('docs/artifacts/01-requirements/')) return 'requirements'
  if (normalizedPath.includes('docs/artifacts/02-traceability/')) return 'traceability'
  if (normalizedPath.includes('docs/artifacts/02-design/')) return 'design'
  if (normalizedPath.includes('docs/artifacts/03-test/')) return 'test-plan'
  if (normalizedPath.includes('docs/artifacts/04-review/')) return 'review'
  if (normalizedPath.includes('docs/artifacts/05-change/')) return 'backlog'
  if (normalizedPath.includes('docs/artifacts/06-security/')) return 'security'
  if (normalizedPath.includes('docs/00-discovery/')) return 'discovery'
  if (normalizedPath.includes('docs/01-requirements/')) return 'requirements'
  if (normalizedPath.includes('docs/02-design/')) return 'design'
  if (normalizedPath.includes('docs/03-test-plan/')) return 'test-plan'
  if (normalizedPath.includes('docs/04-review/')) return 'review'
  if (normalizedPath.includes('docs/05-security/')) return 'security'
  if (normalizedPath.includes('docs/backlog/')) return 'backlog'
  if (normalizedPath.includes('docs/seed-docs/')) return 'standards'
  if (normalizedPath.includes('docs/templates/')) return 'templates'
  if (normalizedPath.includes('docs/adapters/')) return 'agent'
  if (normalizedPath.includes('docs/core/')) return 'reference'
  if (normalizedPath.includes('docs/reference/')) return 'reference'
  if (normalizedPath.includes('docs/runs/')) return 'runs'
  if (fileName === 'traceability.md') return 'traceability'
  return 'other'
}

const HIDDEN_LEGACY_TEMPLATE_PATHS = new Set([
  'docs/00-discovery/changelog.md',
  'docs/00-discovery/discovery-checklist.md',
  'docs/00-discovery/glossary/glossary.md',
  'docs/01-requirements/requirements.md',
  'docs/02-design/req-nnn-design.md',
  'docs/03-test-plan/test-plan.md',
  'docs/04-review/req-nnn-review.md',
  'docs/04-review/ux-review.md',
  'docs/05-security/baseline.md',
  'docs/backlog/process.md',
  'docs/backlog/backlog.md',
  'docs/traceability.md',
])

function shouldExposeDoc(path: string): boolean {
  return !HIDDEN_LEGACY_TEMPLATE_PATHS.has(path.toLowerCase())
}

/**
 * DocNode 트리를 평면 DocEntry[] 목록으로 변환한다.
 * UI(DocList)가 카테고리 그룹화를 위해 평면 구조를 요구하기 때문이다.
 *
 * DataSource 규약: .md 파일은 node.name에서 확장자가 제거되어 있고,
 * 외부 파일(xlsx/pdf 등)은 확장자가 포함된 파일명 그대로 들어있다.
 * 점(`.`) 포함 여부로 두 케이스를 구분한다.
 */
function flattenDocNodes(nodes: DocNode[], parentPath = 'docs'): DocEntry[] {
  const entries: DocEntry[] = []
  for (const node of nodes) {
    if (node.type === 'file') {
      const dotIdx = node.name.lastIndexOf('.')
      if (dotIdx >= 0 && isExternalDocExt(node.name.slice(dotIdx + 1).toLowerCase())) {
        // 외부 파일 — 파일명 그대로 사용
        const ext = node.name.slice(dotIdx + 1).toLowerCase()
        const filePath = `${parentPath}/${node.name}`
        if (!shouldExposeDoc(filePath)) continue
        entries.push({
          name: node.name,
          path: filePath,
          category: resolveCategory(filePath),
          kind: 'external',
          ext,
        })
      } else {
        // 마크다운 — 확장자 복원 필요
        const filePath = `${parentPath}/${node.name}.md`
        if (!shouldExposeDoc(filePath)) continue
        entries.push({
          name: node.name,
          path: filePath,
          category: resolveCategory(filePath),
          kind: 'markdown',
        })
      }
    } else if (node.children) {
      entries.push(...flattenDocNodes(node.children, `${parentPath}/${node.name}`))
    }
  }
  return entries
}

function parseRunMeta(content: string): Pick<DocEntry, 'runGate' | 'runPersona' | 'runStatus'> {
  const meta: Pick<DocEntry, 'runGate' | 'runPersona' | 'runStatus'> = {}
  const yamlMatch = content.match(/```yaml\s*([\s\S]*?)```/)
  const yaml = yamlMatch?.[1] ?? content
  for (const line of yaml.split(/\r?\n/)) {
    const match = line.match(/^\s*(gate|persona|status)\s*:\s*(.+?)\s*$/)
    if (!match) continue
    const value = match[2].replace(/^['"]|['"]$/g, '')
    if (match[1] === 'gate') meta.runGate = value
    if (match[1] === 'persona') meta.runPersona = value
    if (match[1] === 'status') meta.runStatus = value
  }
  return meta
}

async function enrichRunDocs(docs: DocEntry[], dataSource: Awaited<ReturnType<typeof createDataSource>>): Promise<DocEntry[]> {
  return Promise.all(docs.map(async (doc) => {
    if (doc.category !== 'runs' || doc.kind === 'external') return doc
    try {
      const relPath = doc.path.replace(/^docs\//, '')
      const content = await dataSource.readDocFile(relPath)
      return { ...doc, ...parseRunMeta(content) }
    } catch {
      return doc
    }
  }))
}

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
    const tree = await dataSource.getDocTree()
    // DocNode 트리 → DocEntry[] 평면 변환 (절대 경로 미포함, SEC-002-04)
    const docs = await enrichRunDocs(flattenDocNodes(tree), dataSource)
    return NextResponse.json({
      docs,
      fetchedAt: new Date().toISOString(),
      projectType: project.type,
    })
  } catch (err) {
    // PathTraversalError는 403으로 변환 (SEC-002-02, REQ-009-03)
    if (err instanceof PathTraversalError) {
      return NextResponse.json({ error: 'Path Traversal 시도가 감지되었습니다' }, { status: 403 })
    }
    if (err instanceof DataSourceError) {
      return NextResponse.json({ error: err.message }, { status: 503 })
    }
    return NextResponse.json({ error: '문서 목록 조회 실패' }, { status: 500 })
  }
}
