/**
 * @file components/LayoutA.tsx
 * @description 3컬럼 레이아웃 템플릿 A (REQ-012-01)
 *
 * fr 단위 기반 3컬럼 구조 (23 / 57 / 20):
 * - 좌측 23%: DocList — 산출물 문서 (기본 20%에서 +15% 확장)
 * - 중앙 57%: GateStatusStepper → CurrentGatePanel → StatsCards
 * - 우측 20%: CommitList — 최근 커밋
 *
 * 모바일에서는 단일 컬럼으로 폴백한다.
 *
 * @see docs/02-design/req-012-design.md §LayoutA
 */

'use client'

import GateStatusStepper from '@/components/GateStatusStepper'
import DocList from '@/components/DocList'
import CommitList from '@/components/CommitList'
import StatsCards from '@/components/StatsCards'
import CurrentGatePanel from '@/components/CurrentGatePanel'
import OpenFolderButton from '@/components/OpenFolderButton'
import { SectionSkeleton, SectionError, SectionLabel } from '@/components/SectionUI'
import { SessionData, DocEntry, CommitEntry, DocNode } from '@/lib/types'

// ── Props 타입 ────────────────────────────────────────────────────────────────

export interface LayoutProps {
  projectId: string
  projectType?: 'local' | 'github'
  session: SessionData | null
  sessionLoading: boolean
  sessionError: unknown
  docs: DocEntry[]
  docsLoading: boolean
  docsError: unknown
  commits: CommitEntry[]
  commitsLoading: boolean
  commitsError: unknown
  onDocSelect: (doc: DocNode) => void
  /** 외부 파일(xlsx/pdf 등) 클릭 핸들러 — local 프로젝트에서만 호출됨 */
  onExternalOpen?: (doc: DocEntry) => void
}

// ── LayoutA 컴포넌트 ──────────────────────────────────────────────────────────

/**
 * 템플릿 A — 3컬럼 레이아웃.
 *
 * 스크롤 구조:
 * - 좌측/우측: 컬럼 div overflow-hidden → section h-full flex-col →
 *   콘텐츠 래퍼 flex-1 min-h-0 overflow-y-auto (박스 안에서만 스크롤)
 * - 중앙: 여러 섹션이 쌓이므로 컬럼 div 자체가 overflow-y-auto
 */
export default function LayoutA({
  projectId,
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
  onDocSelect,
  onExternalOpen,
}: LayoutProps) {
  return (
    <div
      className="grid grid-cols-1 lg:grid-cols-[23fr_57fr_20fr] gap-6 h-full"
      data-testid="layout-a"
    >
      {/* 좌측 (23%): 산출물 문서 — 내부 스크롤 */}
      <div className="h-full overflow-hidden" data-testid="layout-a-docs">
        <section
          aria-labelledby="layout-a-docs-label"
          className="rounded-xl border border-[#374151] bg-[#111827] p-5 h-full flex flex-col"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest">
              <span id="layout-a-docs-label">산출물 문서</span>
            </h2>
            {projectType === 'local' && <OpenFolderButton projectId={projectId} />}
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-zinc-700 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-zinc-500">
            {docsLoading && <SectionSkeleton rows={4} />}
            {Boolean(docsError) && !docsLoading && (
              <SectionError message="문서 목록을 불러오지 못했습니다." />
            )}
            {!docsLoading && !docsError && (
              <DocList
                docs={docs}
                onDocSelect={onDocSelect}
                onExternalOpen={onExternalOpen}
                externalDisabled={projectType === 'github'}
              />
            )}
          </div>
        </section>
      </div>

      {/* 중앙 (57%): Gate 현황 + 통계 — 컬럼 자체 스크롤 */}
      <div
        className="space-y-6 h-full overflow-y-auto pb-2 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-zinc-700 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-zinc-500"
        data-testid="layout-a-center"
      >
        {/* Gate 진행 현황 */}
        <section aria-labelledby="layout-a-gate-label">
          <SectionLabel>
            <span id="layout-a-gate-label">Gate 진행 현황</span>
          </SectionLabel>

          {sessionLoading && <SectionSkeleton rows={2} />}
          {Boolean(sessionError) && !sessionLoading && (
            <SectionError message="Gate 상태를 불러오지 못했습니다." />
          )}
          {session && !sessionLoading && (
            <GateStatusStepper session={session} />
          )}
          {!session && !sessionLoading && !sessionError && (
            <p className="text-sm text-[#6B7280]">session.json을 찾을 수 없습니다.</p>
          )}
        </section>

        {/* CurrentGatePanel + StatsCards — session.stats 있을 때만 렌더링 */}
        {session?.stats && (
          <>
            <CurrentGatePanel
              session={session}
              stats={session.stats}
              docs={docs}
              onDocSelect={onDocSelect}
            />
            <StatsCards stats={session.stats} />
          </>
        )}
      </div>

      {/* 우측 (20%): 최근 커밋 — 내부 스크롤 */}
      <div className="h-full overflow-hidden" data-testid="layout-a-commits">
        <section
          aria-labelledby="layout-a-commits-label"
          className="rounded-xl border border-[#374151] bg-[#111827] p-5 h-full flex flex-col"
        >
          <SectionLabel>
            <span id="layout-a-commits-label">최근 커밋</span>
          </SectionLabel>

          <div className="flex-1 min-h-0 overflow-y-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-zinc-700 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-zinc-500">
            {commitsLoading && <SectionSkeleton rows={5} />}
            {Boolean(commitsError) && !commitsLoading && (
              <SectionError message="커밋 이력을 불러오지 못했습니다." />
            )}
            {!commitsLoading && !commitsError && (
              <CommitList commits={commits} />
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
