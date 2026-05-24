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
import { AlertTriangle, ArrowLeft, CheckCircle2, GitBranch } from 'lucide-react'
import AnvilIcon from '@/components/AnvilIcon'
import DocDrawer from '@/components/DocDrawer'
import RefreshButton from '@/components/RefreshButton'
import LayoutToggle from '@/components/LayoutToggle'
import LayoutA from '@/components/LayoutA'
import LayoutA2 from '@/components/LayoutA2'
import LayoutB from '@/components/LayoutB'
import { useProjectSession } from '@/hooks/useProjectSession'
import { useProjectRuntime } from '@/hooks/useProjectRuntime'
import { useProjectDocs } from '@/hooks/useProjectDocs'
import { useProjectCommits } from '@/hooks/useProjectCommits'
import { useLayoutTemplate } from '@/hooks/useLayoutTemplate'
import { DocEntry, DocNode, ProjectRuntime, SessionData } from '@/lib/types'

function branchRoleLabel(branch: string | null | undefined, runtime: ProjectRuntime | null | undefined, session: SessionData | null | undefined): string {
  const workflow = runtime?.workflow
  const branchState = session?.branch_state
  const main = workflow?.main_branch ?? branchState?.main_branch ?? 'main'
  const integration = workflow?.integration_branch ?? branchState?.integration_branch ?? 'dev'
  if (!branch) return 'unknown'
  if (branch === main) return 'baseline'
  if (branch === integration) return 'integration'
  return branchState?.current_role ?? 'worktree'
}

function needsIntegrationBranch(session: SessionData | null | undefined, runtime: ProjectRuntime | null | undefined): boolean {
  const gate = session?.current_gate
  if (gate !== 'impl' && gate !== 'gate4') return false
  return runtime?.workflow?.impl_uses_integration_branch !== false
}

function BranchWorkspaceBanner({
  session,
  runtime,
  isLoading,
}: {
  session: SessionData | null | undefined
  runtime: ProjectRuntime | null | undefined
  isLoading?: boolean
}) {
  const branch = runtime?.current_branch ?? session?.branch_state?.current_branch ?? null
  const workflow = runtime?.workflow
  const integration = workflow?.integration_branch ?? session?.branch_state?.integration_branch ?? 'dev'
  const mode = workflow?.branch_mode ?? 'single'
  const role = branchRoleLabel(branch, runtime, session)
  const mismatch = needsIntegrationBranch(session, runtime) && Boolean(branch) && branch !== integration

  if (isLoading && !branch && !workflow) {
    return (
      <div className="mt-3 h-7 w-72 animate-pulse rounded-md bg-slate-800/70" />
    )
  }

  if (!branch && !workflow && !session?.branch_state) return null

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
      <span className={`inline-flex max-w-full items-center gap-1.5 rounded-md border px-2 py-1 ${
        mismatch
          ? 'border-amber-500/50 bg-amber-500/10 text-amber-200'
          : 'border-slate-700 bg-slate-900/70 text-slate-300'
      }`}>
        <GitBranch className="h-3.5 w-3.5 flex-none" aria-hidden="true" />
        <span className="font-medium">{branch ?? 'branch unknown'}</span>
        <span className="text-slate-500">/</span>
        <span>{role}</span>
      </span>
      <span className="inline-flex items-center gap-1 rounded-md border border-slate-700 bg-slate-900/60 px-2 py-1 text-slate-400">
        workflow: {mode}
      </span>
      {mismatch ? (
        <span className="inline-flex min-w-0 items-center gap-1.5 rounded-md border border-amber-500/40 bg-amber-500/10 px-2 py-1 text-amber-200">
          <AlertTriangle className="h-3.5 w-3.5 flex-none" aria-hidden="true" />
          <span className="truncate">impl/Gate4는 {integration} 브랜치에서 진행</span>
        </span>
      ) : branch ? (
        <span className="inline-flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-emerald-200">
          <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
          작업공간 확인됨
        </span>
      ) : null}
    </div>
  )
}

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
    runtime,
    isLoading: runtimeLoading,
    error: runtimeError,
    mutate: mutateRuntime,
  } = useProjectRuntime(id)

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
    await Promise.all([mutateSession(), mutateRuntime(), mutateDocs(), mutateCommits()])
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
    runtime,
    runtimeLoading,
    runtimeError,
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
              <BranchWorkspaceBanner
                session={session}
                runtime={runtime}
                isLoading={runtimeLoading}
              />
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
