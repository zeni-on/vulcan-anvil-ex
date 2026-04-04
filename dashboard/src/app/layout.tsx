/**
 * @file app/layout.tsx
 * @description 전역 레이아웃
 *
 * 기존 단일 프로젝트 Sidebar를 제거하고 멀티 프로젝트 홈화면 기반 레이아웃으로 전환한다.
 * Sidebar는 프로젝트 상세 페이지(REQ-005)에서 별도 처리한다.
 *
 * @see docs/02-design/req-001-004-design.md §라우팅 구조
 */

import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Anvil Dashboard',
  description: 'Vulcan-Claude-Anvil Project Dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="bg-[#030712] text-[#F9FAFB] antialiased">
        {children}
      </body>
    </html>
  )
}
