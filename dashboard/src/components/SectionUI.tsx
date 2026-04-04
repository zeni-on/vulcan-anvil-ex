/**
 * @file components/SectionUI.tsx
 * @description 페이지 섹션 공통 UI 컴포넌트 (REQ-012)
 *
 * page.tsx에서 인라인 정의하던 SectionSkeleton, SectionError, SectionLabel을
 * LayoutA, LayoutB 등 레이아웃 컴포넌트에서도 재사용할 수 있도록 분리한다.
 *
 * @see docs/02-design/req-012-design.md
 */

import React from 'react'
import { AlertCircle } from 'lucide-react'

// ── SectionSkeleton ───────────────────────────────────────────────────────────

interface SectionSkeletonProps {
  /** 스켈레톤 행 수 (기본값: 3) */
  rows?: number
}

/**
 * 로딩 중 스켈레톤 플레이스홀더.
 * 각 행의 너비를 약간씩 달리하여 자연스러운 로딩 느낌을 제공한다.
 */
export function SectionSkeleton({ rows = 3 }: SectionSkeletonProps) {
  return (
    <div className="animate-pulse space-y-2" aria-busy="true" aria-label="데이터 불러오는 중">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-4 rounded bg-[#1F2937]"
          style={{ width: `${70 + (i % 3) * 10}%` }}
        />
      ))}
    </div>
  )
}

// ── SectionError ──────────────────────────────────────────────────────────────

interface SectionErrorProps {
  /** 표시할 에러 메시지 */
  message: string
}

/**
 * 섹션 에러 알림 카드.
 * role="alert"로 스크린 리더에 즉시 알린다.
 */
export function SectionError({ message }: SectionErrorProps) {
  return (
    <div
      role="alert"
      className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400"
    >
      <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
      {message}
    </div>
  )
}

// ── SectionLabel ──────────────────────────────────────────────────────────────

interface SectionLabelProps {
  children: React.ReactNode
}

/**
 * 섹션 헤더 레이블.
 * 소문자 → 대문자 변환(uppercase)과 자간(tracking-widest)으로 시각적 계층을 표현한다.
 */
export function SectionLabel({ children }: SectionLabelProps) {
  return (
    <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest mb-4">
      {children}
    </h2>
  )
}
