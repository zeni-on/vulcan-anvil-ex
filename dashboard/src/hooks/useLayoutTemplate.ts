/**
 * @file hooks/useLayoutTemplate.ts
 * @description 레이아웃 템플릿 선택 상태 훅 (REQ-012-01, REQ-012-04)
 *
 * localStorage 키 "vulcan-dashboard-layout"에 'A' | 'A2' | 'B' 값을 영속화한다.
 * SSR 환경(typeof window === 'undefined')에서는 기본값 'A'를 반환한다.
 *
 * 보안 (SEC-012-01): localStorage 읽기 시 허용된 템플릿 값만 사용하고
 * 그 외 값(null 포함)은 'A'로 강제 폴백하여 주입 공격을 방어한다.
 *
 * @see docs/02-design/req-012-design.md
 */

'use client'

import { useState, useEffect } from 'react'

/** 지원하는 레이아웃 템플릿 값 */
export type LayoutTemplate = 'A' | 'A2' | 'B'

/** localStorage 저장 키 */
const STORAGE_KEY = 'vulcan-dashboard-layout'

/**
 * localStorage에서 레이아웃 템플릿을 읽어 검증한다.
 * 허용된 값 외에는 기본값 'A'로 폴백한다 (SEC-012-01).
 */
function readStoredTemplate(): LayoutTemplate {
  if (typeof window === 'undefined') return 'A'
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'A' || stored === 'A2' || stored === 'B') return stored
  return 'A'
}

/**
 * 레이아웃 템플릿 선택 상태를 관리하는 커스텀 훅.
 *
 * - SSR 초기값: 'A' (hydration mismatch 방지)
 * - 클라이언트 마운트 후: localStorage 값으로 동기화
 * - toggle(): 'A' → 'A2' → 'B' → 'A' 순환 + localStorage 즉시 저장
 *
 * @returns {{ template: LayoutTemplate; toggle: () => void }}
 */
export function useLayoutTemplate(): { template: LayoutTemplate; toggle: () => void } {
  // SSR 안전: 초기값은 항상 'A'로 설정하여 서버/클라이언트 hydration mismatch 방지
  const [template, setTemplate] = useState<LayoutTemplate>('A')

  // 클라이언트 마운트 후 localStorage 값으로 동기화
  useEffect(() => {
    setTemplate(readStoredTemplate())
  }, [])

  /**
   * 템플릿을 A → A2 → B → A 순서로 전환하고 localStorage에 저장한다.
   */
  function toggle() {
    setTemplate((prev) => {
      const next: LayoutTemplate = prev === 'A' ? 'A2' : prev === 'A2' ? 'B' : 'A'
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, next)
      }
      return next
    })
  }

  return { template, toggle }
}
