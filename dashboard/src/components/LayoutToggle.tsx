/**
 * @file components/LayoutToggle.tsx
 * @description 레이아웃 템플릿 전환 버튼 (REQ-012-03)
 *
 * 현재 활성 템플릿에 따라 다른 아이콘과 텍스트를 표시하고,
 * 클릭 시 onToggle 콜백을 호출하여 레이아웃을 전환한다.
 *
 * 아이콘 규칙 (설계 §LayoutToggle):
 * - template === 'A' → Columns 아이콘 표시 (3컬럼 활성 상태를 시각화)
 * - template === 'B' → LayoutGrid 아이콘 표시 (상단+하단 활성 상태를 시각화)
 *
 * @see docs/02-design/req-012-design.md §LayoutToggle
 */

'use client'

import { LayoutGrid, Columns } from 'lucide-react'
import { LayoutTemplate } from '@/hooks/useLayoutTemplate'

interface LayoutToggleProps {
  /** 현재 활성 레이아웃 템플릿 */
  template: LayoutTemplate
  /** 레이아웃 전환 콜백 */
  onToggle: () => void
}

/**
 * 레이아웃 템플릿 전환 버튼.
 * RefreshButton과 동일한 아이콘 버튼 스타일을 사용한다.
 */
export default function LayoutToggle({ template, onToggle }: LayoutToggleProps) {
  const isA = template === 'A'

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label="레이아웃 전환"
      aria-pressed={isA}
      className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs text-[#9CA3AF] hover:text-[#F9FAFB] hover:bg-[#1F2937] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950"
      data-testid="layout-toggle"
    >
      {isA ? (
        <Columns className="w-3.5 h-3.5" aria-hidden="true" data-testid="icon-columns" />
      ) : (
        <LayoutGrid className="w-3.5 h-3.5" aria-hidden="true" data-testid="icon-layout-grid" />
      )}
      <span className="hidden sm:inline">
        {isA ? '템플릿 A' : '템플릿 B'}
      </span>
    </button>
  )
}
