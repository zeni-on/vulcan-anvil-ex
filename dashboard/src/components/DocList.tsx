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

import { DocEntry, DocNode } from '@/lib/types'
import { FileText } from 'lucide-react'

/** 카테고리 한국어 레이블 */
const CATEGORY_LABEL: Record<DocEntry['category'], string> = {
  requirements: '요구사항',
  design:       '설계',
  'test-plan':  '테스트 계획',
  review:       '리뷰',
  other:        '기타',
}

/** 카테고리 표시 순서 */
const CATEGORY_ORDER: DocEntry['category'][] = [
  'requirements',
  'design',
  'test-plan',
  'review',
  'other',
]

interface DocListProps {
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
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
 * 단일 문서 항목. onDocSelect가 전달되면 클릭 가능한 인터랙티브 스타일 적용.
 */
function DocItem({ doc, onDocSelect }: { doc: DocEntry; onDocSelect?: (doc: DocNode) => void }) {
  const isClickable = Boolean(onDocSelect)

  const handleSelect = () => {
    if (onDocSelect) onDocSelect(toDocNode(doc))
  }

  return (
    <li
      className={`flex items-center gap-2 py-1.5 text-sm rounded px-1 -mx-1 ${
        isClickable
          ? 'cursor-pointer hover:bg-zinc-700/60 transition-colors'
          : ''
      }`}
      data-testid="doc-item"
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onClick={isClickable ? handleSelect : undefined}
      onKeyDown={isClickable ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSelect() } } : undefined}
    >
      <FileText className="w-3.5 h-3.5 text-gray-600 flex-shrink-0" aria-hidden="true" />
      <span className="text-[#9CA3AF] truncate font-mono text-xs">{doc.name}</span>
    </li>
  )
}

/**
 * 카테고리 섹션 — 그룹 헤더 + 해당 카테고리 문서 목록.
 */
function CategorySection({
  category,
  docs,
  onDocSelect,
}: {
  category: DocEntry['category']
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
}) {
  if (docs.length === 0) return null

  return (
    <div data-testid={`doc-category-${category}`}>
      <p className="text-[11px] font-semibold text-[#9CA3AF] uppercase tracking-widest mb-1">
        {CATEGORY_LABEL[category]}
      </p>
      <ul className="space-y-0.5 mb-4">
        {docs.map((doc) => (
          <DocItem key={doc.path} doc={doc} onDocSelect={onDocSelect} />
        ))}
      </ul>
    </div>
  )
}

/**
 * 산출물 문서를 Gate 그룹별로 분류하여 목록으로 렌더링한다.
 * 문서가 없으면 안내 메시지를 표시한다.
 */
export default function DocList({ docs, onDocSelect }: DocListProps) {
  // 카테고리별 그룹화
  const grouped = CATEGORY_ORDER.reduce<Record<DocEntry['category'], DocEntry[]>>(
    (acc, cat) => {
      acc[cat] = docs.filter((d) => d.category === cat)
      return acc
    },
    { requirements: [], design: [], 'test-plan': [], review: [], other: [] },
  )

  const hasAny = docs.length > 0

  return (
    <div
      data-testid="doc-list"
      className="overflow-x-hidden"
    >
      {hasAny ? (
        CATEGORY_ORDER.map((cat) => (
          <CategorySection key={cat} category={cat} docs={grouped[cat]} onDocSelect={onDocSelect} />
        ))
      ) : (
        <p className="text-sm text-[#6B7280] py-2">산출물 문서가 없습니다.</p>
      )}
    </div>
  )
}
