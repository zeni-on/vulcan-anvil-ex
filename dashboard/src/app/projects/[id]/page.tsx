'use client'

/**
 * @file app/projects/[id]/page.tsx
 * @description 프로젝트 상세 대시보드 (REQ-005, REQ-012)
 *
 * REQ-012: useLayoutTemplate 훅으로 레이아웃 템플릿(A/B)을 관리하고,
 * LayoutToggle 버튼으로 전환한다. 콘텐츠 영역은 template 값에 따라
 * LayoutA 또는 LayoutB 컴포넌트를 조건부 렌더링한다.
 *
 * @see docs/02-design/req-005-009-design.md §프로젝트 상세 페이지
 * @see docs/02-design/req-012-design.md
 */

import { useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import AnvilIcon from '@/components/AnvilIcon'
import DocDrawer from '@/components/DocDrawer'
import RefreshButton from '@/components/RefreshButton'
import LayoutToggle from '@/components/LayoutToggle'
import LayoutA from '@/components/LayoutA'
import LayoutA2 from '@/components/LayoutA2'
import LayoutB from '@/components/LayoutB'
import { useProjectSession } from '@/hooks/useProjectSession'
import { useProjectDocs } from '@/hooks/useProjectDocs'
import { useProjectCommits } from '@/hooks/useProjectCommits'
import { useLayoutTemplate } from '@/hooks/useLayoutTemplate'
import { DocEntry, DocNode } from '@/lib/types'

// ── 메인 페이지 컴포넌트 ─────────────────────────────────────────────────────

/**
 * 프로젝트 상세 대시보드 페이지.
 * useParams()로 id를 추출하고 세 SWR 훅으로 Gate 상태, 문서 목록, 커밋 이력을 독립 패치한다.
 * useLayoutTemplate 훅으로 레이아웃 템플릿(A/B)을 관리한다 (REQ-012).
 */
export default function ProjectDetailPage() {
  const params = useParams()
  const id = typeof params.id === 'string' ? params.id : String(params.id ?? '')

  const [selectedDoc, setSelectedDoc] = useState<DocNode | null>(null)

  // 레이아웃 템플릿 상태 (REQ-012-01, REQ-012-04)
  const { template, toggle } = useLayoutTemplate()

  const {
    session,
    fetchedAt: sessionFetchedAt,
    isLoading: sessionLoading,
    error: sessionError,
    mutate: mutateSession,
  } = useProjectSession(id)

  const {
    docs,
    projectType,
    isLoading: docsLoading,
    error: docsError,
    mutate: mutateDocs,
  } = useProjectDocs(id)

  const {
    commits,
    isLoading: commitsLoading,
    error: commitsError,
    mutate: mutateCommits,
  } = useProjectCommits(id)

  /** 세 SWR 훅을 동시 재검증한다 — RefreshButton에 전달 */
  const handleRefresh = async () => {
    await Promise.all([mutateSession(), mutateDocs(), mutateCommits()])
  }

  /**
   * 외부 파일(xlsx/pdf/hwp 등) 클릭 핸들러.
   * 서버가 등록된 project.path 기반으로 OS 기본 앱을 실행한다 (REQ-014).
   */
  const handleExternalOpen = async (doc: DocEntry) => {
    try {
      const res = await fetch(`/api/projects/${id}/open-file`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ path: doc.path }),
      })
      if (!res.ok) {
        const body = (await res.json().catch(() => ({}))) as { error?: string }
        // alert이 부담스럽지만 콘솔만으론 사용자가 모를 수 있어 임시 알림 사용
        // (TODO: 토스트 컴포넌트가 도입되면 교체)
        alert(body.error ?? `파일 열기 실패 (${res.status})`)
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : String(e))
    }
  }

  /** 공통 레이아웃 props — LayoutA, LayoutB 모두 동일하게 전달 */
  const layoutProps = {
    projectId: id,
    projectType,
    session,
    sessionLoading,
    sessionError,
    docs,
    docsLoading,
    docsError,
    commits,
    commitsLoading,
    commitsError,
    onDocSelect: (doc: DocNode) => setSelectedDoc(doc),
    onExternalOpen: handleExternalOpen,
  }

  return (
    <div className="min-h-screen bg-[#030712]">
      {/* 헤더 */}
      <header className="sticky top-0 z-10 border-b border-[#374151] bg-[#030712]/90 backdrop-blur-sm">
        <div className="max-w-[92vw] mx-auto px-6 h-14 flex items-center gap-2.5">
          <AnvilIcon className="w-6 h-6 text-blue-400" />
          <span className="text-sm font-semibold text-[#F9FAFB] tracking-tight">
            Vulcan Anvil
          </span>
        </div>
      </header>

      <main className="max-w-[92vw] mx-auto px-6 py-6 h-[calc(100vh-56px)] flex flex-col overflow-hidden">
        {/* 브레드크럼 + LayoutToggle + 새로고침 버튼 (REQ-012-03) */}
        <div className="flex items-center justify-between mb-6 flex-shrink-0">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-[#9CA3AF] hover:text-[#F9FAFB] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
            data-testid="back-link"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            홈으로
          </Link>

          <div className="flex items-center gap-2">
            {/* 레이아웃 전환 버튼 — RefreshButton 좌측에 배치 (REQ-012-03) */}
            <LayoutToggle template={template} onToggle={toggle} />

            <RefreshButton
              onRefresh={handleRefresh}
              lastFetchedAt={sessionFetchedAt}
            />
          </div>
        </div>

        {/* 프로젝트 헤더 정보 */}
        <div className="mb-8 flex-shrink-0">
          {session ? (
            <>
              <h1 className="text-2xl font-bold text-[#F9FAFB] mb-1">
                {session.project}
              </h1>
              {session.feature && (
                <p className="text-sm text-[#9CA3AF] mb-1">{session.feature}</p>
              )}
              {session.started && (
                <p className="text-xs text-[#6B7280]">시작일: {session.started}</p>
              )}
            </>
          ) : !sessionLoading && (
            <h1 className="text-2xl font-bold text-[#F9FAFB] mb-1">
              프로젝트 ID: {id}
            </h1>
          )}
        </div>

        {/* 콘텐츠 영역 — template 값에 따라 LayoutA, LayoutA2 또는 LayoutB 조건부 렌더링 (REQ-012) */}
        <div className="flex-1 overflow-hidden">
          {template === 'A' ? (
            <LayoutA {...layoutProps} />
          ) : template === 'A2' ? (
            <LayoutA2 {...layoutProps} />
          ) : (
            <LayoutB {...layoutProps} />
          )}
        </div>
      </main>

      {/* 문서 뷰어 Drawer — fixed 포지셔닝이므로 페이지 레이아웃에 영향 없음 (REQ-010-02) */}
      <DocDrawer
        projectId={id}
        doc={selectedDoc}
        onClose={() => setSelectedDoc(null)}
      />
    </div>
  )
}
