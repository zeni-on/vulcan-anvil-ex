/**
 * @file components/LayoutB.tsx
 * @description 상단+하단 레이아웃 템플릿 B (REQ-012-02)
 *
 * 구조:
 * - 상단 풀 width: CurrentGatePanel + StatsCards (session.stats 있을 때만)
 * - 하단 grid-cols-3:
 *   - 좌측 col-span-2 (2/3): GateStatusStepper + DocList
 *   - 우측 col-span-1 (1/3): CommitList
 *
 * 기존 page.tsx의 레이아웃을 컴포넌트로 분리한 것으로,
 * 기존 사용자 경험을 유지하는 대안 레이아웃이다.
 *
 * @see docs/02-design/req-012-design.md §LayoutB
 */

'use client'

import GateStatusStepper from '@/components/GateStatusStepper'
import DocList from '@/components/DocList'
import CommitList from '@/components/CommitList'
import StatsCards from '@/components/StatsCards'
import CurrentGatePanel from '@/components/CurrentGatePanel'
import OpenFolderButton from '@/components/OpenFolderButton'
import { SectionSkeleton, SectionError, SectionLabel } from '@/components/SectionUI'
import { LayoutProps } from '@/components/LayoutA'

/**
 * 템플릿 B — 상단 stats + 하단 2컬럼 레이아웃.
 *
 * 기존 page.tsx의 인라인 레이아웃을 컴포넌트로 추출한 것이다.
 * CurrentGatePanel과 StatsCards를 상단에 풀 width로 배치하여
 * 프로젝트 진행 현황을 우선적으로 보여준다.
 */
export default function LayoutB({
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
    <div data-testid="layout-b" className="h-full flex flex-col overflow-hidden">
      {/* 상단 풀 width — session.stats 있을 때만 렌더링 */}
      {session?.stats && (
        <div className="space-y-6 mb-8 flex-shrink-0" data-testid="layout-b-stats">
          <CurrentGatePanel
            session={session}
            stats={session.stats}
            docs={docs}
            onDocSelect={onDocSelect}
          />
          <StatsCards stats={session.stats} />
        </div>
      )}

      {/* 하단 — 모바일 단일 컬럼, 데스크탑 3컬럼 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 overflow-hidden">
        {/* 좌측 (col-span-2): Gate 현황 + 산출물 문서 */}
        <div className="lg:col-span-2 space-y-8 h-full overflow-y-auto" data-testid="layout-b-left">
          {/* Gate 진행 현황 섹션 */}
          <section aria-labelledby="layout-b-gate-label">
            <SectionLabel>
              <span id="layout-b-gate-label">Gate 진행 현황</span>
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

          {/* 산출물 문서 섹션 */}
          <section
            aria-labelledby="layout-b-docs-label"
            className="rounded-xl border border-[#374151] bg-[#111827] p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest">
                <span id="layout-b-docs-label">산출물 문서</span>
              </h2>
              {projectType === 'local' && <OpenFolderButton projectId={projectId} />}
            </div>

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
          </section>
        </div>

        {/* 우측 (col-span-1): 최근 커밋 이력 */}
        <div className="lg:col-span-1 h-full overflow-y-auto" data-testid="layout-b-commits">
          <section
            aria-labelledby="layout-b-commits-label"
            className="rounded-xl border border-[#374151] bg-[#111827] p-5"
          >
            <SectionLabel>
              <span id="layout-b-commits-label">최근 커밋</span>
            </SectionLabel>

            {commitsLoading && <SectionSkeleton rows={5} />}
            {Boolean(commitsError) && !commitsLoading && (
              <SectionError message="커밋 이력을 불러오지 못했습니다." />
            )}
            {!commitsLoading && !commitsError && (
              <CommitList commits={commits} />
            )}
          </section>
        </div>
      </div>
    </div>
  )
}
