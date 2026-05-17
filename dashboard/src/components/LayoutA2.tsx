/**
 * @file components/LayoutA2.tsx
 * @description 템플릿 A 개선안 A2
 *
 * 기존 LayoutA를 직접 고치지 않고 비교 가능한 실험 레이아웃으로 둔다.
 * A2는 문서 트리를 더 넓게 보고, 중앙 작업 영역을 Gate 중심으로 정리하며,
 * 우측에는 최근 커밋과 통계를 얇게 쌓아 보여준다.
 */

'use client'

import { useState } from 'react'
import GateStatusStepper from '@/components/GateStatusStepper'
import DocList from '@/components/DocList'
import CommitList from '@/components/CommitList'
import OpenFolderButton from '@/components/OpenFolderButton'
import { SectionSkeleton, SectionError, SectionLabel } from '@/components/SectionUI'
import { LayoutProps } from '@/components/LayoutA'
import { CommitEntry, DocEntry, DocNode, ProjectStats } from '@/lib/types'
import { BookOpen, CheckCircle, FileText, FlaskConical, GitCommit, Layers } from 'lucide-react'

type CompactStatTone = 'blue' | 'green' | 'yellow' | 'default'

interface CompactStatProps {
  icon: React.ReactNode
  label: string
  value: string | number
  sub?: string
  tone?: CompactStatTone
}

function CompactStat({ icon, label, value, sub, tone = 'default' }: CompactStatProps) {
  const valueColor = {
    blue: 'text-sky-300',
    green: 'text-emerald-300',
    yellow: 'text-amber-300',
    default: 'text-slate-100',
  }[tone]

  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-700/80 bg-slate-950/35 px-3 py-2">
      <div className="shrink-0 text-slate-500">{icon}</div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-[11px] font-medium text-slate-400">{label}</div>
        {sub && <div className="truncate text-[11px] text-slate-500">{sub}</div>}
      </div>
      <div className={`shrink-0 text-base font-bold tabular-nums ${valueColor}`}>
        {value}
      </div>
    </div>
  )
}

function CompactStats({ stats }: { stats: ProjectStats }) {
  const { requirements: req, tests, docs, backlog } = stats
  const acCoverage = req.total > 0 ? Math.round((req.ac_defined / req.total) * 100) : 0
  const testPassRate = tests.total > 0 ? Math.round((tests.passed / tests.total) * 100) : 0

  return (
    <div className="space-y-4" data-testid="compact-stats">
      <div>
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          요구사항
        </h3>
        <div className="space-y-2">
          <CompactStat
            icon={<Layers className="h-4 w-4" />}
            label="상위 / 상세"
            value={`${req.groups}/${req.total}`}
            sub="REQ"
            tone="blue"
          />
          <CompactStat
            icon={<CheckCircle className="h-4 w-4" />}
            label="구현 완료"
            value={`${req.implemented}/${req.total}`}
            tone={req.implemented === req.total && req.total > 0 ? 'green' : 'yellow'}
          />
          <CompactStat
            icon={<CheckCircle className="h-4 w-4" />}
            label="AC 커버리지"
            value={`${acCoverage}%`}
            sub={req.ac_missing > 0 ? `미정의 ${req.ac_missing}건` : '완전 커버'}
            tone={req.ac_missing === 0 && req.total > 0 ? 'green' : 'yellow'}
          />
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          테스트
        </h3>
        <div className="space-y-2">
          <CompactStat
            icon={<FlaskConical className="h-4 w-4" />}
            label="전체 / 통과"
            value={`${tests.total}/${tests.passed}`}
            sub={tests.total > 0 ? `통과율 ${testPassRate}%` : undefined}
            tone={tests.failed > 0 ? 'yellow' : 'green'}
          />
          <CompactStat
            icon={<CheckCircle className="h-4 w-4" />}
            label="미실행"
            value={tests.pending}
            sub={tests.skipped > 0 ? `Skip ${tests.skipped}건` : undefined}
            tone={tests.pending > 0 ? 'yellow' : 'default'}
          />
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          문서
        </h3>
        <div className="space-y-2">
          <CompactStat
            icon={<FileText className="h-4 w-4" />}
            label="Discovery / Release"
            value={`${docs.discovery ?? 0}/${docs.release ?? 0}`}
            tone="blue"
          />
          <CompactStat
            icon={<BookOpen className="h-4 w-4" />}
            label="Backlog / Run"
            value={`${docs.backlog ?? 0}/${docs.runs ?? 0}`}
            tone={(docs.runs ?? 0) > 0 ? 'green' : 'default'}
          />
        </div>
      </div>

      {backlog && (
        <div>
          <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
            백로그
          </h3>
          <div className="space-y-2">
            <CompactStat
              icon={<BookOpen className="h-4 w-4" />}
              label="Active / Done"
              value={`${backlog.active}/${backlog.done}`}
              tone={backlog.active > 0 ? 'yellow' : 'green'}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function emptyGateLabel(gate: string) {
  if (gate === 'phase0') return 'Phase 0'
  if (gate === 'impl') return '구현'
  return gate.replace(/^gate/i, 'Gate ')
}

function A2GateEmptyPanel({ gate }: { gate: string }) {
  const label = emptyGateLabel(gate)

  return (
    <section
      className="rounded-xl border border-slate-700 bg-[#111827] p-4"
      data-testid="layout-a2-gate-empty"
    >
      <div className="space-y-3">
        <div>
          <span className="rounded border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 text-xs font-semibold text-cyan-300">
            {label}
          </span>
          <h2 className="mt-2 text-base font-bold text-[#F9FAFB]">
            {gate === 'phase0' ? 'Discovery 준비 중' : '진행 통계 준비 중'}
          </h2>
          <p className="mt-1 text-sm leading-6 text-[#9CA3AF]">
            아직 진행 통계가 생성되지 않아 현재 Gate 요약이 비어 있습니다. 왼쪽 산출물을 채우고 검증을 실행하면 요구사항, 문서, Run 통계가 이 영역에 표시됩니다.
          </p>
        </div>

        <div className="grid gap-2 sm:grid-cols-2">
          <CompactStat
            icon={<FileText className="h-4 w-4" />}
            label="먼저 채울 문서"
            value="4"
            sub="Project Brief, Scope, As-Is/To-Be, Risk"
            tone="blue"
          />
          <CompactStat
            icon={<CheckCircle className="h-4 w-4" />}
            label="통계 갱신"
            value="check"
            sub="python vulcan.py check-trace"
            tone="default"
          />
        </div>
      </div>
    </section>
  )
}

function A2StatsEmptyPanel() {
  return (
    <div
      className="rounded-lg border border-slate-700/80 bg-slate-950/35 px-3 py-3"
      data-testid="layout-a2-stats-empty"
    >
      <h3 className="text-sm font-semibold text-slate-200">통계 대기 중</h3>
      <p className="mt-1 text-xs leading-5 text-slate-500">
        Phase 0 산출물을 작성하고 검증을 실행하면 진행 통계가 표시됩니다.
      </p>
    </div>
  )
}

function waveLabel(status: string, isCurrent: boolean) {
  if (['Implemented', 'Verified', 'Completed', 'Done'].includes(status)) return '완료'
  if (['In Progress', 'Running', 'Review Requested'].includes(status) || isCurrent) return '진행중'
  if (status === 'Blocked') return '차단'
  return '대기'
}

function waveClass(label: string) {
  if (label === '완료') return 'border-emerald-500/45 bg-emerald-500/10 text-emerald-100'
  if (label === '진행중') return 'border-cyan-500/55 bg-cyan-500/10 text-cyan-100'
  if (label === '차단') return 'border-red-500/55 bg-red-500/10 text-red-100'
  return 'border-slate-700 bg-slate-950/35 text-slate-300'
}

function A2ImplementationPanel({ stats }: { stats: ProjectStats }) {
  const implReq = stats.implementation?.requirements
  const waves = stats.implementation?.waves
  const reqTotal = implReq?.total ?? stats.requirements.total
  const reqImplemented = implReq?.implemented ?? stats.requirements.implemented
  const reqPct = reqTotal > 0 ? Math.round((reqImplemented / reqTotal) * 100) : 0
  const wavePct = waves && waves.total > 0 ? Math.round((waves.completed / waves.total) * 100) : 0

  return (
    <section
      className="rounded-xl border-l-4 border-orange-500 bg-[#111827] border border-[#374151] p-4 space-y-3"
      data-testid="layout-a2-impl-panel"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded border border-orange-500/30 bg-orange-500/10 px-2 py-0.5 text-xs font-semibold text-orange-300">
              진행 중
            </span>
            <h2 className="text-base font-bold text-[#F9FAFB]">구현</h2>
          </div>
          <p className="mt-0.5 text-sm text-[#9CA3AF]">
            요구사항 구현률과 현재 Build Wave를 중심으로 확인합니다.
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-[#9CA3AF]">요구사항 구현률</span>
          <span className="font-medium text-green-400">{reqImplemented} / {reqTotal} ({reqPct}%)</span>
        </div>
        <div className="h-2 rounded-full bg-[#1F2937]" role="progressbar" aria-label="요구사항 구현률" aria-valuenow={reqPct} aria-valuemin={0} aria-valuemax={100}>
          <div className="h-2 rounded-full bg-green-500 transition-all" style={{ width: `${reqPct}%` }} />
        </div>
      </div>

      {waves && (
        <div className="space-y-2" data-testid="layout-a2-wave-progress">
          <div className="flex items-center justify-between text-sm">
            <span className="text-[#9CA3AF]">Build Wave</span>
            <span className="font-medium text-cyan-300">{waves.completed} / {waves.total} ({wavePct}%)</span>
          </div>
          <div className="h-2 rounded-full bg-[#1F2937]" role="progressbar" aria-label="Build Wave 진행률" aria-valuenow={wavePct} aria-valuemin={0} aria-valuemax={100}>
            <div className="h-2 rounded-full bg-cyan-500 transition-all" style={{ width: `${wavePct}%` }} />
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {waves.items.map((item) => {
              const label = waveLabel(item.status, item.id === waves.current)
              return (
                <div
                  key={item.id}
                  className={`flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs ${waveClass(label)}`}
                >
                  <span className="h-2.5 w-2.5 shrink-0 rounded-full bg-current opacity-75" aria-hidden="true" />
                  <span className="min-w-0 flex-1 font-semibold">{item.id}</span>
                  <span className="shrink-0">{label}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}

const A2_GATE_META: Record<string, { label: string; description: string; color: string; badge: string }> = {
  phase0: {
    label: 'Phase 0 — Discovery',
    description: '아이디어, 질문, 범위 후보를 정리하는 단계',
    color: 'border-cyan-500',
    badge: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300',
  },
  gate1: {
    label: 'Gate 1 — 요구사항',
    description: 'REQ-ID와 인수기준을 확정하는 단계',
    color: 'border-blue-500',
    badge: 'border-blue-500/30 bg-blue-500/10 text-blue-300',
  },
  gate2: {
    label: 'Gate 2 — 설계',
    description: '아키텍처, 화면, API, DB, 보안 설계를 정리하는 단계',
    color: 'border-purple-500',
    badge: 'border-purple-500/30 bg-purple-500/10 text-purple-300',
  },
  gate3: {
    label: 'Gate 3 — 테스트 플랜',
    description: '통합 테스트와 검증 기준을 준비하는 단계',
    color: 'border-yellow-500',
    badge: 'border-yellow-500/30 bg-yellow-500/10 text-yellow-300',
  },
  gate4: {
    label: 'Gate 4 — QA 검토',
    description: 'QA 결과, Finding, 증적을 검수하는 단계',
    color: 'border-red-500',
    badge: 'border-red-500/30 bg-red-500/10 text-red-300',
  },
  gate5: {
    label: 'Gate 5 — 최종 승인',
    description: '사용자가 최종 승인 여부를 확인하는 단계',
    color: 'border-green-500',
    badge: 'border-green-500/30 bg-green-500/10 text-green-300',
  },
}

function A2GateSummaryPanel({
  gate,
  stats,
  docs,
}: {
  gate: string
  stats: ProjectStats
  docs: DocEntry[]
}) {
  const meta = A2_GATE_META[gate]
  if (!meta) return null

  const req = stats.requirements
  const tests = stats.tests
  const designDocs = docs.filter(doc => doc.category === 'design' && doc.kind !== 'external').length
  const reviewDocs = docs.filter(doc => doc.category === 'review' && doc.kind !== 'external').length
  const discoveryDocs = docs.filter(doc => doc.category === 'discovery' && doc.kind !== 'external').length
  const testPassRate = tests.total > 0 ? Math.round((tests.passed / tests.total) * 100) : 0
  const acCoverage = req.total > 0 ? Math.round((req.ac_defined / req.total) * 100) : 0

  const rows = {
    phase0: [
      ['Discovery 문서', discoveryDocs, 'blue'],
      ['Backlog/CR 문서', stats.docs.backlog ?? 0, 'yellow'],
    ],
    gate1: [
      ['상위 / 상세 요구사항', `${req.groups} / ${req.total}`, 'blue'],
      ['AC 커버리지', `${acCoverage}%`, acCoverage === 100 ? 'green' : 'yellow'],
    ],
    gate2: [
      ['설계 문서', designDocs, 'blue'],
      ['AC 커버리지', `${acCoverage}%`, acCoverage === 100 ? 'green' : 'yellow'],
    ],
    gate3: [
      ['테스트 케이스', tests.total, 'blue'],
      ['미실행', tests.pending, tests.pending > 0 ? 'yellow' : 'green'],
    ],
    gate4: [
      ['테스트 통과율', `${testPassRate}%`, testPassRate === 100 ? 'green' : 'yellow'],
      ['QA/리뷰 문서', reviewDocs, 'blue'],
    ],
    gate5: [
      ['요구사항 구현 완료', `${req.implemented} / ${req.total}`, req.implemented === req.total ? 'green' : 'yellow'],
      ['테스트 통과율', `${testPassRate}%`, testPassRate === 100 ? 'green' : 'yellow'],
    ],
  }[gate] ?? []

  return (
    <section
      className={`rounded-xl border-l-4 ${meta.color} bg-[#111827] border border-[#374151] p-4 space-y-3`}
      data-testid="layout-a2-gate-summary"
    >
      <div>
        <div className="flex items-center gap-2">
          <span className={`rounded border px-2 py-0.5 text-xs font-semibold ${meta.badge}`}>
            진행 중
          </span>
          <h2 className="text-base font-bold text-[#F9FAFB]">{meta.label}</h2>
        </div>
        <p className="mt-0.5 text-sm text-[#9CA3AF]">{meta.description}</p>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {rows.map(([label, value, tone]) => (
          <CompactStat
            key={String(label)}
            icon={<CheckCircle className="h-4 w-4" />}
            label={String(label)}
            value={value as string | number}
            tone={tone as CompactStatTone}
          />
        ))}
      </div>
    </section>
  )
}

function runNumber(doc: DocEntry) {
  const match = doc.name.match(/^RUN-(\d+)/i)
  return match ? Number(match[1]) : 0
}

function A2RecentActivity({
  docs,
  commits,
  onDocSelect,
}: {
  docs: DocEntry[]
  commits: CommitEntry[]
  onDocSelect: (doc: DocNode) => void
}) {
  const recentRuns = docs
    .filter(doc => doc.category === 'runs' && doc.kind !== 'external')
    .sort((a, b) => runNumber(b) - runNumber(a))
    .slice(0, 3)
  const recentCommits = commits.slice(0, 2)

  if (recentRuns.length === 0 && recentCommits.length === 0) return null

  return (
    <section
      className="grid gap-2 lg:grid-cols-2"
      data-testid="layout-a2-recent-activity"
    >
      <div className="rounded-lg border border-[#334155] bg-[#0F172A] px-3 py-2.5">
        <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-[#9CA3AF]">
          최근 Run
        </h3>
        {recentRuns.length === 0 ? (
          <p className="text-xs text-slate-500">최근 Run 문서가 없습니다.</p>
        ) : (
          <ul className="space-y-1">
            {recentRuns.slice(0, 2).map(doc => (
              <li key={doc.path}>
                <button
                  type="button"
                  onClick={() => onDocSelect({
                    name: doc.name,
                    slug: doc.path.replace(/\.md$/, '').split('/').filter(Boolean),
                    type: 'file',
                  })}
                  className="flex w-full items-center gap-2 rounded-md px-1.5 py-1 text-left hover:bg-cyan-500/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500"
                >
                  <FileText className="h-3.5 w-3.5 shrink-0 text-cyan-300" />
                  <span className="min-w-0 flex-1 truncate text-xs font-medium text-slate-200">
                    {doc.name}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-lg border border-[#334155] bg-[#0F172A] px-3 py-2.5">
        <h3 className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-[#9CA3AF]">
          최근 커밋
        </h3>
        {recentCommits.length === 0 ? (
          <p className="text-xs text-slate-500">커밋 이력이 없습니다.</p>
        ) : (
          <ul className="space-y-1">
            {recentCommits.map(commit => (
              <li
                key={commit.sha}
                className="rounded-md px-1.5 py-1"
              >
                <p className="truncate text-xs font-medium text-slate-200">
                  <GitCommit className="mr-1.5 inline h-3.5 w-3.5 text-emerald-300" />
                  {commit.message}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}

/**
 * 템플릿 A2 — A를 대체하지 않는 비교용 레이아웃.
 *
 * 데스크탑:
 * - 좌측 28%: 산출물 문서, 폴더 계층 확인 우선
 * - 중앙 50%: Gate 진행 현황과 현재 Gate 패널
 * - 우측 22%: 통계와 최근 커밋
 */
export default function LayoutA2({
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
  const [sideView, setSideView] = useState<'stats' | 'commits'>('stats')

  return (
    <div
      className="grid grid-cols-1 xl:grid-cols-[28fr_50fr_22fr] gap-5 h-full"
      data-testid="layout-a2"
    >
      <section
        aria-labelledby="layout-a2-docs-label"
        className="min-h-0 rounded-xl border border-[#475569] bg-[#0B1220] p-5 flex flex-col shadow-[0_0_0_1px_rgba(148,163,184,0.05)]"
        data-testid="layout-a2-docs"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-[11px] font-semibold text-cyan-300 uppercase tracking-widest">
              Template A2
            </p>
            <h2 className="mt-1 text-sm font-semibold text-[#F8FAFC]">
              <span id="layout-a2-docs-label">산출물 문서</span>
            </h2>
          </div>
          {projectType === 'local' && <OpenFolderButton projectId={projectId} />}
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto pr-1 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-600 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-slate-400">
          {docsLoading && <SectionSkeleton rows={5} />}
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

      <div
        className="min-h-0 overflow-y-auto space-y-3 pr-1 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-700 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-slate-500"
        data-testid="layout-a2-center"
      >
        <section
          aria-labelledby="layout-a2-gate-label"
          className="rounded-xl border border-[#1D4ED8]/60 bg-[#08111F] p-4"
        >
          <SectionLabel>
            <span id="layout-a2-gate-label">Gate 진행 현황</span>
          </SectionLabel>

          {sessionLoading && <SectionSkeleton rows={2} />}
          {Boolean(sessionError) && !sessionLoading && (
            <SectionError message="Gate 상태를 불러오지 못했습니다." />
          )}
          {session && !sessionLoading && <GateStatusStepper session={session} />}
          {!session && !sessionLoading && !sessionError && (
            <p className="text-sm text-[#94A3B8]">session.json을 찾을 수 없습니다.</p>
          )}
        </section>

        {session?.stats ? (
          <>
            {session.current_gate === 'impl' ? (
              <A2ImplementationPanel stats={session.stats} />
            ) : (
              <A2GateSummaryPanel
                gate={session.current_gate}
                stats={session.stats}
                docs={docs}
              />
            )}
            <A2RecentActivity
              docs={docs}
              commits={commits}
              onDocSelect={onDocSelect}
            />
          </>
        ) : (
          session && !sessionLoading && !sessionError && (
            <A2GateEmptyPanel gate={session.current_gate} />
          )
        )}
      </div>

      <aside
        className="min-h-0 overflow-hidden"
        data-testid="layout-a2-side"
      >
        <section
          aria-labelledby="layout-a2-side-label"
          className="flex h-full min-h-0 flex-col rounded-xl border border-[#334155] bg-[#0F172A] p-4"
        >
          <div className="mb-4 flex items-center justify-between gap-2">
            <h2
              id="layout-a2-side-label"
              className="text-xs font-semibold uppercase tracking-widest text-[#9CA3AF]"
            >
              {sideView === 'stats' ? '진행 통계' : '최근 커밋'}
            </h2>
            <div className="grid grid-cols-2 rounded-lg border border-slate-700 bg-slate-950/40 p-0.5 text-[11px]">
              <button
                type="button"
                onClick={() => setSideView('stats')}
                className={`rounded-md px-2 py-1 transition-colors ${sideView === 'stats' ? 'bg-cyan-500/20 text-cyan-200' : 'text-slate-500 hover:text-slate-200'}`}
              >
                통계
              </button>
              <button
                type="button"
                onClick={() => setSideView('commits')}
                className={`rounded-md px-2 py-1 transition-colors ${sideView === 'commits' ? 'bg-cyan-500/20 text-cyan-200' : 'text-slate-500 hover:text-slate-200'}`}
              >
                커밋
              </button>
            </div>
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto pr-1 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-slate-700 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-slate-500">
            {sideView === 'stats' && (
              session?.stats ? <CompactStats stats={session.stats} /> : <A2StatsEmptyPanel />
            )}
            {sideView === 'commits' && (
              <>
                {commitsLoading && <SectionSkeleton rows={5} />}
                {Boolean(commitsError) && !commitsLoading && (
                  <SectionError message="커밋 이력을 불러오지 못했습니다." />
                )}
                {!commitsLoading && !commitsError && <CommitList commits={commits} />}
              </>
            )}
          </div>
        </section>
      </aside>
    </div>
  )
}
