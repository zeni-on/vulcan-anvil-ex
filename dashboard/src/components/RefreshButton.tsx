/**
 * @file components/RefreshButton.tsx
 * @description 수동 새로고침 버튼 컴포넌트 (REQ-005-05, REQ-009-05)
 *
 * 클릭 시 onRefresh()를 호출하여 세 SWR 훅(session, docs, commits)을 동시 mutate한다.
 * 로딩 중에는 RefreshCw 아이콘 회전 애니메이션과 aria-busy="true"로 상태를 표시한다.
 *
 * @see docs/02-design/req-005-009-design.md §RefreshButton
 * @see docs/02-design/ui-design.md §RefreshButton
 */

'use client'

import { useState } from 'react'
import { RefreshCw } from 'lucide-react'

interface RefreshButtonProps {
  /** 세 SWR 훅의 mutate를 동시 호출하는 핸들러 */
  onRefresh: () => Promise<void>
  /** ISO 8601 — "마지막 갱신: N초 전" 표시용 */
  lastFetchedAt?: string
}

/** ISO 8601 → "N초 전" / "N분 전" 형식 변환 */
function formatLastFetched(isoDate?: string): string {
  if (!isoDate) return ''
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const seconds = Math.floor(diffMs / 1_000)
  if (seconds < 60) return `${seconds}초 전`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}분 전`
}

/**
 * 수동 새로고침 버튼.
 * 진행 중에는 isLoading 상태로 버튼을 비활성화하고 아이콘을 회전시킨다.
 */
export default function RefreshButton({ onRefresh, lastFetchedAt }: RefreshButtonProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleClick = async () => {
    if (isLoading) return
    setIsLoading(true)
    try {
      await onRefresh()
    } finally {
      setIsLoading(false)
    }
  }

  const lastFetchedLabel = formatLastFetched(lastFetchedAt)

  return (
    <div className="flex items-center gap-2">
      {/* 마지막 갱신 시각 */}
      {lastFetchedLabel && (
        <span className="text-xs text-[#4B5563] hidden sm:inline">
          갱신: {lastFetchedLabel}
        </span>
      )}

      <button
        type="button"
        onClick={handleClick}
        disabled={isLoading}
        aria-label="데이터 새로고침"
        aria-busy={isLoading}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs text-[#9CA3AF] hover:text-[#F9FAFB] hover:bg-[#1F2937] transition-colors disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950"
        data-testid="refresh-button"
      >
        <RefreshCw
          className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`}
          aria-hidden="true"
        />
        <span className="hidden sm:inline">새로고침</span>
      </button>
    </div>
  )
}
