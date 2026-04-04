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
import { DataSourceError, DocEntry, DocNode, PathTraversalError } from '@/lib/types'

type RouteContext = { params: Promise<{ id: string }> }

/**
 * 폴더 경로 접두사로 DocEntry category를 결정한다.
 * UI가 Gate별 그룹 표시를 하기 위한 분류 기준이다.
 */
function resolveCategory(path: string): DocEntry['category'] {
  if (path.includes('01-requirements')) return 'requirements'
  if (path.includes('02-design')) return 'design'
  if (path.includes('03-test-plan')) return 'test-plan'
  if (path.includes('04-review')) return 'review'
  return 'other'
}

/**
 * DocNode 트리를 평면 DocEntry[] 목록으로 변환한다.
 * UI(DocList)가 카테고리 그룹화를 위해 평면 구조를 요구하기 때문이다.
 */
function flattenDocNodes(nodes: DocNode[], parentPath = 'docs'): DocEntry[] {
  const entries: DocEntry[] = []
  for (const node of nodes) {
    if (node.type === 'file') {
      const path = `${parentPath}/${node.name}.md`
      entries.push({ name: node.name, path, category: resolveCategory(path) })
    } else if (node.children) {
      entries.push(...flattenDocNodes(node.children, `${parentPath}/${node.name}`))
    }
  }
  return entries
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
    const docs = flattenDocNodes(tree)
    return NextResponse.json({ docs, fetchedAt: new Date().toISOString() })
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
