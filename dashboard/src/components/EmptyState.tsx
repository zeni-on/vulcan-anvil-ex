'use client'

/**
 * @file EmptyState.tsx
 * @description 프로젝트가 없을 때 표시하는 온보딩 안내 컴포넌트
 *
 * 등록된 프로젝트가 없을 때 온보딩 안내 텍스트와 프로젝트 추가 CTA 버튼을 표시한다.
 *
 * Props:
 * - onAddProject: () => void — 프로젝트 추가 다이얼로그 열기 콜백
 *
 * @see docs/02-design/ui-design.md §EmptyState
 */

import { FolderOpen, Plus } from 'lucide-react'

interface EmptyStateProps {
  onAddProject: () => void
}

/**
 * 빈 상태 안내 UI.
 * 중앙 정렬, FolderOpen 아이콘 + 제목 + 설명 + CTA 버튼 구조.
 */
export default function EmptyState({ onAddProject }: EmptyStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px] text-center px-6"
      data-testid="empty-state"
    >
      {/* 아이콘 */}
      <div className="w-16 h-16 rounded-2xl bg-[#1F2937] border border-[#374151] flex items-center justify-center mb-6">
        <FolderOpen
          className="w-8 h-8 text-[#4B5563]"
          aria-hidden="true"
        />
      </div>

      {/* 제목 */}
      <h2 className="text-xl font-semibold text-[#F9FAFB] mb-2">
        등록된 프로젝트가 없습니다
      </h2>

      {/* 설명 */}
      <p className="text-sm text-[#9CA3AF] max-w-sm leading-relaxed mb-8">
        Vulcan 프로젝트를 추가하여 Gate 진행 상태를 한눈에 확인하고 관리하세요.
      </p>

      {/* CTA 버튼 */}
      <button
        type="button"
        onClick={onAddProject}
        className={`
          inline-flex items-center gap-2 px-4 py-2.5
          rounded-lg bg-blue-600 hover:bg-blue-500
          text-sm font-medium text-white
          transition-colors duration-150
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950
        `}
        data-testid="empty-state-add-button"
      >
        <Plus className="w-4 h-4" aria-hidden="true" />
        첫 번째 프로젝트 추가
      </button>
    </div>
  )
}
