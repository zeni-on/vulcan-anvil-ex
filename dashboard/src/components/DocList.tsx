/**
 * @file components/DocList.tsx
 * @description 산출물 문서 목록 컴포넌트 (REQ-005-02)
 *
 * DocEntry[]를 카테고리(Gate 그룹)별로 분류하여 탭 없이 섹션 그룹으로 렌더링한다.
 * 파일명은 클릭 불가한 단순 목록으로 표시한다 (설계 §DocList).
 * 절대 경로는 표시하지 않아 서버 내부 경로 노출을 방지한다 (SEC-002-04).
 *
 * @see docs/02-design/req-005-009-design.md §DocList
 * @see docs/02-design/ui-design.md §DocList
 */

'use client'

import { useState } from 'react'
import { DocEntry, DocNode } from '@/lib/types'
import {
  ChevronDown,
  ChevronRight,
  ExternalLink,
  FileSpreadsheet,
  FileText,
  FileType,
  Presentation,
} from 'lucide-react'

/** 카테고리 한국어 레이블 */
const CATEGORY_LABEL: Record<DocEntry['category'], string> = {
  discovery:    '상위설계',
  requirements: '요구사항',
  design:       '설계',
  'test-plan':  '테스트 계획',
  review:       '리뷰',
  other:        '기타',
}

/** 카테고리 표시 순서 */
const CATEGORY_ORDER: DocEntry['category'][] = [
  'discovery',
  'requirements',
  'design',
  'test-plan',
  'review',
  'other',
]

/** 카테고리별 docs/ 루트 접두사 — 하위폴더 추출 시 제거할 베이스 경로 */
const CATEGORY_PREFIX: Partial<Record<DocEntry['category'], string>> = {
  discovery: 'docs/00-discovery/',
}

/**
 * 카테고리 prefix를 제거한 후 파일명을 빼고 남은 하위폴더 경로를 반환한다.
 * 루트 직속 파일은 빈 문자열을 반환한다.
 * 예: 'docs/00-discovery/glossary/glossary.md' → 'glossary'
 *     'docs/00-discovery/DISCOVERY-CHECKLIST.md' → ''
 */
function extractSubPath(entry: DocEntry, prefix: string): string {
  if (!entry.path.startsWith(prefix)) return ''
  const rest = entry.path.slice(prefix.length)
  const segments = rest.split('/')
  segments.pop() // 파일명 제거
  return segments.join('/')
}

interface DocListProps {
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
  /** 외부 파일(xlsx/pdf 등) 클릭 시 호출 — 로컬 프로젝트에서만 의미 있음 */
  onExternalOpen?: (doc: DocEntry) => void
  /** github 프로젝트는 외부 파일을 OS 앱으로 못 여므로 비활성 표시 */
  externalDisabled?: boolean
}

/** 확장자별 아이콘 선택 */
function ExtensionIcon({ ext, className }: { ext: string; className?: string }) {
  const cn = className ?? 'w-3.5 h-3.5 flex-shrink-0'
  switch (ext) {
    case 'xlsx':
    case 'xls':
      return <FileSpreadsheet className={`${cn} text-emerald-500`} aria-hidden="true" />
    case 'pptx':
    case 'ppt':
      return <Presentation className={`${cn} text-orange-500`} aria-hidden="true" />
    case 'pdf':
      return <FileType className={`${cn} text-red-500`} aria-hidden="true" />
    case 'docx':
    case 'doc':
      return <FileText className={`${cn} text-blue-500`} aria-hidden="true" />
    case 'hwp':
    case 'hwpx':
      return <FileText className={`${cn} text-sky-500`} aria-hidden="true" />
    default:
      return <FileText className={`${cn} text-gray-500`} aria-hidden="true" />
  }
}

/**
 * DocEntry.path → DocNode 변환.
 * path = "docs/01-requirements/REQUIREMENTS.md" → slug = ['docs', '01-requirements', 'REQUIREMENTS']
 * useDocContent이 slug.slice(1).join('/')로 API 경로를 구성하므로 .md는 제거한다.
 */
function toDocNode(entry: DocEntry): DocNode {
  const withoutExt = entry.path.replace(/\.md$/, '')
  const slug = withoutExt.split('/')
  return {
    name: entry.name,
    slug,
    type: 'file',
  }
}

/**
 * 단일 문서 항목.
 * - markdown: onDocSelect → Drawer로 렌더
 * - external: onExternalOpen → 서버가 OS 기본 앱으로 실행 (github 프로젝트면 비활성)
 */
function DocItem({
  doc,
  onDocSelect,
  onExternalOpen,
  externalDisabled,
}: {
  doc: DocEntry
  onDocSelect?: (doc: DocNode) => void
  onExternalOpen?: (doc: DocEntry) => void
  externalDisabled?: boolean
}) {
  const isExternal = doc.kind === 'external'

  // 외부파일인데 비활성 모드면 클릭 불가
  const isDisabled = isExternal && externalDisabled
  const isClickable =
    !isDisabled && (isExternal ? Boolean(onExternalOpen) : Boolean(onDocSelect))

  const handleSelect = () => {
    if (isDisabled) return
    if (isExternal) {
      onExternalOpen?.(doc)
    } else {
      onDocSelect?.(toDocNode(doc))
    }
  }

  const title = isDisabled
    ? 'GitHub 프로젝트는 외부 파일 열기를 지원하지 않습니다'
    : isExternal
      ? 'OS 기본 앱으로 열기'
      : undefined

  return (
    <li
      className={`flex items-center gap-2 py-1.5 text-sm rounded px-1 -mx-1 ${
        isClickable
          ? 'cursor-pointer hover:bg-zinc-700/60 transition-colors'
          : isDisabled
            ? 'opacity-50 cursor-not-allowed'
            : ''
      }`}
      data-testid="doc-item"
      title={title}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onClick={isClickable ? handleSelect : undefined}
      onKeyDown={isClickable ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSelect() } } : undefined}
      aria-disabled={isDisabled || undefined}
    >
      {isExternal ? (
        <ExtensionIcon ext={doc.ext ?? ''} />
      ) : (
        <FileText className="w-3.5 h-3.5 text-gray-600 flex-shrink-0" aria-hidden="true" />
      )}
      <span className="text-[#9CA3AF] truncate font-mono text-xs">{doc.name}</span>
      {isExternal && (
        <ExternalLink
          className="w-3 h-3 text-[#4B5563] flex-shrink-0 ml-auto"
          aria-hidden="true"
        />
      )}
    </li>
  )
}

/**
 * 하위폴더 토글이 가능한 카테고리 섹션. (discovery 등 prefix가 정의된 카테고리)
 * 각 하위폴더는 chevron 버튼으로 접고 펼칠 수 있다. 기본은 모두 펼쳐진 상태.
 * 루트 직속 파일은 헤더 없이 항상 보여준다.
 */
function CollapsibleSubfolderGroup({
  category,
  sortedKeys,
  subGroups,
  onDocSelect,
  onExternalOpen,
  externalDisabled,
}: {
  category: DocEntry['category']
  sortedKeys: string[]
  subGroups: Map<string, DocEntry[]>
  onDocSelect?: (doc: DocNode) => void
  onExternalOpen?: (doc: DocEntry) => void
  externalDisabled?: boolean
}) {
  // 접힌 폴더의 subPath 집합. 비어있으면 모두 펼침.
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set())

  const toggle = (subPath: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev)
      if (next.has(subPath)) next.delete(subPath)
      else next.add(subPath)
      return next
    })
  }

  return (
    <div data-testid={`doc-category-${category}`}>
      <p className="text-[11px] font-semibold text-[#9CA3AF] uppercase tracking-widest mb-1">
        {CATEGORY_LABEL[category]}
      </p>
      <div className="mb-4">
        {sortedKeys.map((subPath) => {
          const isRoot = subPath === ''
          const isOpen = !collapsed.has(subPath)
          const items = subGroups.get(subPath)!

          if (isRoot) {
            return (
              <ul key="__root__" className="space-y-0.5">
                {items.map((doc) => (
                  <DocItem
                    key={doc.path}
                    doc={doc}
                    onDocSelect={onDocSelect}
                    onExternalOpen={onExternalOpen}
                    externalDisabled={externalDisabled}
                  />
                ))}
              </ul>
            )
          }

          return (
            <div key={subPath} className="mt-2">
              <button
                type="button"
                onClick={() => toggle(subPath)}
                aria-expanded={isOpen}
                data-testid={`doc-subfolder-toggle-${subPath}`}
                className="flex items-center gap-1 w-full text-left text-xs font-semibold text-[#E5E7EB] font-mono mb-1 pl-0.5 py-1 rounded hover:bg-zinc-700/50 hover:text-white transition-colors"
              >
                {isOpen ? (
                  <ChevronDown className="w-3.5 h-3.5 flex-shrink-0 text-[#9CA3AF]" aria-hidden="true" />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-[#9CA3AF]" aria-hidden="true" />
                )}
                <span data-testid={`doc-subfolder-${subPath}`}>{subPath}/</span>
                <span className="ml-1 text-[#6B7280] font-normal">({items.length})</span>
              </button>
              {isOpen && (
                <ul className="space-y-0.5 pl-3">
                  {items.map((doc) => (
                    <DocItem
                      key={doc.path}
                      doc={doc}
                      onDocSelect={onDocSelect}
                      onExternalOpen={onExternalOpen}
                      externalDisabled={externalDisabled}
                    />
                  ))}
                </ul>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

/**
 * 카테고리 섹션 — 그룹 헤더 + 해당 카테고리 문서 목록.
 */
function CategorySection({
  category,
  docs,
  onDocSelect,
  onExternalOpen,
  externalDisabled,
}: {
  category: DocEntry['category']
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
  onExternalOpen?: (doc: DocEntry) => void
  externalDisabled?: boolean
}) {
  if (docs.length === 0) return null

  // 하위폴더 그룹화가 정의된 카테고리(예: discovery)는 subPath별로 묶어서 렌더
  const prefix = CATEGORY_PREFIX[category]
  if (prefix) {
    const subGroups = new Map<string, DocEntry[]>()
    for (const doc of docs) {
      const subPath = extractSubPath(doc, prefix)
      const arr = subGroups.get(subPath) ?? []
      arr.push(doc)
      subGroups.set(subPath, arr)
    }
    // 루트 직속 파일을 먼저, 그 뒤 하위폴더는 알파벳순
    const sortedKeys = Array.from(subGroups.keys()).sort((a, b) => {
      if (a === '') return -1
      if (b === '') return 1
      return a.localeCompare(b)
    })

    return (
      <CollapsibleSubfolderGroup
        category={category}
        sortedKeys={sortedKeys}
        subGroups={subGroups}
        onDocSelect={onDocSelect}
        onExternalOpen={onExternalOpen}
        externalDisabled={externalDisabled}
      />
    )
  }

  return (
    <div data-testid={`doc-category-${category}`}>
      <p className="text-[11px] font-semibold text-[#9CA3AF] uppercase tracking-widest mb-1">
        {CATEGORY_LABEL[category]}
      </p>
      <ul className="space-y-0.5 mb-4">
        {docs.map((doc) => (
          <DocItem
            key={doc.path}
            doc={doc}
            onDocSelect={onDocSelect}
            onExternalOpen={onExternalOpen}
            externalDisabled={externalDisabled}
          />
        ))}
      </ul>
    </div>
  )
}

/**
 * 산출물 문서를 Gate 그룹별로 분류하여 목록으로 렌더링한다.
 * 문서가 없으면 안내 메시지를 표시한다.
 */
export default function DocList({
  docs,
  onDocSelect,
  onExternalOpen,
  externalDisabled,
}: DocListProps) {
  // 카테고리별 그룹화
  const grouped = CATEGORY_ORDER.reduce<Record<DocEntry['category'], DocEntry[]>>(
    (acc, cat) => {
      acc[cat] = docs.filter((d) => d.category === cat)
      return acc
    },
    { discovery: [], requirements: [], design: [], 'test-plan': [], review: [], other: [] },
  )

  const hasAny = docs.length > 0

  return (
    <div
      data-testid="doc-list"
      className="overflow-x-hidden"
    >
      {hasAny ? (
        CATEGORY_ORDER.map((cat) => (
          <CategorySection
            key={cat}
            category={cat}
            docs={grouped[cat]}
            onDocSelect={onDocSelect}
            onExternalOpen={onExternalOpen}
            externalDisabled={externalDisabled}
          />
        ))
      ) : (
        <p className="text-sm text-[#6B7280] py-2">산출물 문서가 없습니다.</p>
      )}
    </div>
  )
}
