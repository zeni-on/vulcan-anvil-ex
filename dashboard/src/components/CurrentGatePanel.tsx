/**
 * @file CurrentGatePanel.tsx
 * @description 현재 Gate 세부 정보 패널 (REQ-011-04)
 *
 * current_gate 값에 따라 gate별로 다른 콘텐츠를 렌더링한다.
 * gate2는 category === 'design'인 DocEntry 목록,
 * gate4는 category === 'review'인 DocEntry 목록을 표시한다.
 *
 * 원본: Vulcan-Anvil/templates/dashboard/src/components/CurrentGatePanel.tsx
 * 변경 사항:
 * - SessionData, ProjectStats, DocEntry, DocNode를 @/lib/types에서 import
 * - DesignDoc[], QAResult[] 대신 docs: DocEntry[]를 category로 필터링하여 재사용
 * - onDocSelect?: (doc: DocNode) => void prop 추가 (DocDrawer 연결용)
 * - 다크 테마 색상 토큰 유지 (bg-[#111827], border-[#374151])
 * - session.current_gate가 GATE_META에 없으면 null 반환 (UT-011-17)
 *
 * @see docs/02-design/req-011-design.md §7
 */

import Link from 'next/link'
import { FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { SessionData, ProjectStats, DocEntry, DocNode } from '@/lib/types'

// ── Gate 메타데이터 ───────────────────────────────────────────────────────────

const GATE_META: Record<string, {
  label: string
  description: string
  borderColor: string
  badgeColor: string
}> = {
  phase0: {
    label: 'Phase 0 - Discovery',
    description: '아이디어, 질문, 범위 후보를 정리하고 Gate 1 또는 Backlog로 넘기는 단계',
    borderColor: 'border-cyan-500',
    badgeColor: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
  },
  gate1: {
    label: 'Gate 1 — 요구사항',
    description: 'PM이 REQ-ID와 AC를 정의하는 단계',
    borderColor: 'border-blue-500',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  },
  gate2: {
    label: 'Gate 2 — 설계',
    description: 'Architect · DBA · UI Designer가 시스템을 설계하는 단계',
    borderColor: 'border-purple-500',
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  },
  gate3: {
    label: 'Gate 3 — 테스트 계획',
    description: 'QA가 E2E/Integration TST-ID를 작성하는 단계',
    borderColor: 'border-yellow-500',
    badgeColor: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  },
  impl: {
    label: '구현',
    description: 'Frontend · Backend Developer가 코드를 작성하는 단계',
    borderColor: 'border-orange-500',
    badgeColor: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  },
  gate4: {
    label: 'Gate 4 — QA 리뷰',
    description: 'QA가 코드 리뷰와 테스트를 실행하는 단계',
    borderColor: 'border-red-500',
    badgeColor: 'bg-red-500/10 text-red-400 border-red-500/30',
  },
  gate5: {
    label: 'Gate 5 — 최종 승인',
    description: '사용자가 최종 확인하는 단계',
    borderColor: 'border-green-500',
    badgeColor: 'bg-green-500/10 text-green-400 border-green-500/30',
  },
}

const GATE_ORDER = ['phase0', 'gate1', 'gate2', 'gate3', 'impl', 'gate4', 'gate5']

// ── CurrentGatePanel 컴포넌트 ─────────────────────────────────────────────────

interface CurrentGatePanelProps {
  session: SessionData
  stats: ProjectStats
  /** useProjectDocs 훅에서 가져온 산출물 문서 목록 */
  docs: DocEntry[]
  /** DocDrawer 연결용 콜백. doc 클릭 시 호출된다. */
  onDocSelect?: (doc: DocNode) => void
}

/**
 * 현재 Gate 세부 정보 패널.
 * session.current_gate가 GATE_META에 없는 값('completed' 등)이면 null을 반환한다 (UT-011-17).
 */
export default function CurrentGatePanel({
  session,
  stats,
  docs,
  onDocSelect,
}: CurrentGatePanelProps) {
  const gate = session.current_gate
  const meta = GATE_META[gate]

  // GATE_META에 없는 gate 값(예: 'completed')이면 미표시 (UT-011-17)
  if (!meta) return null

  return (
    <div
      className={`rounded-xl border-l-4 ${meta.borderColor} bg-[#111827] border border-[#374151] p-6 space-y-4`}
      data-testid="current-gate-panel"
    >
      {/* 헤더 */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${meta.badgeColor}`}>
              진행 중
            </span>
            <h2 className="text-base font-bold text-[#F9FAFB]">{meta.label}</h2>
          </div>
          <p className="text-sm text-[#9CA3AF] mt-1">{meta.description}</p>
        </div>
      </div>

      {/* Gate별 콘텐츠 — 문서 목록이 길어질 경우 박스 안에서 스크롤 */}
      <div className="max-h-48 overflow-y-auto [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-zinc-700 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-zinc-500">
        <GateContent
          gate={gate}
          stats={stats}
          docs={docs}
          onDocSelect={onDocSelect}
        />
      </div>
      <RunStatusSummary gate={gate} docs={docs} onDocSelect={onDocSelect} />
    </div>
  )
}

// ── GateContent 내부 컴포넌트 ─────────────────────────────────────────────────

interface GateContentProps {
  gate: string
  stats: ProjectStats
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
}

/** Gate 값에 따라 다른 콘텐츠를 렌더링하는 내부 컴포넌트 */
function GateContent({ gate, stats, docs, onDocSelect }: GateContentProps) {
  const { requirements: req, tests } = stats

  if (gate === 'phase0') {
    const discoveryDocs = docs.filter(d => d.category === 'discovery' && d.kind !== 'external')
    const backlogDocs = docs.filter(d => d.category === 'backlog' && d.kind !== 'external')
    return (
      <div className="space-y-3" data-testid="gate-content-phase0">
        <Row label="Discovery docs" value={`${discoveryDocs.length} files`} status={discoveryDocs.length > 0 ? 'ok' : 'warn'} />
        <Row label="Backlog docs" value={`${backlogDocs.length} files`} status={backlogDocs.length > 0 ? 'ok' : 'warn'} />
        <ul className="space-y-1.5">
          {[...discoveryDocs, ...backlogDocs].slice(0, 6).map(doc => (
            <li key={doc.path}>
              <DocLink doc={doc} onDocSelect={onDocSelect} iconColor="text-cyan-400" />
            </li>
          ))}
        </ul>
      </div>
    )
  }
  // gate1: REQ/AC 현황 행 (UT-011-14)
  if (gate === 'gate1') {
    return (
      <div className="space-y-3" data-testid="gate-content-gate1">
        <Row label="상위 요구사항" value={`${req.groups}개`} />
        <Row label="상세 요구사항" value={`${req.total}개`} />
        <Row
          label="AC 정의 완료"
          value={`${req.ac_defined} / ${req.total}`}
          status={req.ac_missing === 0 && req.total > 0 ? 'ok' : 'warn'}
        />
      </div>
    )
  }

  // gate2: category === 'design'인 DocEntry 목록 (UT-011-15)
  if (gate === 'gate2') {
    const designDocs = docs.filter(d => d.category === 'design' && d.kind !== 'external')
    return (
      <div className="space-y-2" data-testid="gate-content-gate2">
        <p className="text-xs text-[#6B7280]">생성된 설계 문서</p>
        {designDocs.length === 0 ? (
          <p className="text-sm text-[#4B5563] italic">아직 설계 문서가 없습니다</p>
        ) : (
          <ul className="space-y-1.5">
            {designDocs.map(doc => (
              <li key={doc.path}>
                <DocLink doc={doc} onDocSelect={onDocSelect} iconColor="text-purple-400" />
              </li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  // gate3: TST-ID 전체 수와 미실행 수
  if (gate === 'gate3') {
    return (
      <div className="space-y-3" data-testid="gate-content-gate3">
        <Row label="TST-ID 전체" value={`${tests.total}개`} />
        <Row
          label="작성 완료"
          value={`${tests.total}개`}
          status={tests.total > 0 ? 'ok' : 'warn'}
        />
        {tests.total > 0 && (
          <Row
            label="미실행 (실행 대기)"
            value={`${tests.pending}개`}
            status={tests.pending > 0 ? 'warn' : 'ok'}
          />
        )}
        {tests.total === 0 && (
          <p className="text-sm text-[#4B5563] italic">TEST_PLAN.md에 TST-ID가 없습니다</p>
        )}
      </div>
    )
  }

  // impl: 구현 진행률 바 (UT-011-16)
  if (gate === 'impl') {
    const pct = req.total > 0 ? Math.round((req.implemented / req.total) * 100) : 0
    return (
      <div className="space-y-3" data-testid="gate-content-impl">
        <Row
          label="구현 진행률"
          value={`${req.implemented} / ${req.total} (${pct}%)`}
          status={req.implemented === req.total && req.total > 0 ? 'ok' : 'warn'}
        />
        <div className="w-full bg-[#1F2937] rounded-full h-2" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div
            className={`h-2 rounded-full transition-all ${pct === 100 ? 'bg-green-500' : 'bg-orange-500'}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    )
  }

  // gate4: category === 'review'인 DocEntry 목록 (QA 리뷰 문서)
  if (gate === 'gate4') {
    const reviewDocs = docs.filter(d => d.category === 'review' && d.kind !== 'external')
    return (
      <div className="space-y-3" data-testid="gate-content-gate4">
        {reviewDocs.length === 0 ? (
          <p className="text-sm text-[#4B5563] italic">아직 QA 리뷰 문서가 없습니다</p>
        ) : (
          <ul className="space-y-1.5">
            {reviewDocs.map(doc => (
              <li key={doc.path}>
                <DocLink doc={doc} onDocSelect={onDocSelect} iconColor="text-red-400" />
              </li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  // gate5: 구현 완료 수 + 테스트 통과율 요약
  if (gate === 'gate5') {
    const testPassRate = tests.total > 0
      ? Math.round((tests.passed / tests.total) * 100)
      : 0
    return (
      <div className="space-y-3" data-testid="gate-content-gate5">
        <Row
          label="요구사항 구현 완료"
          value={`${req.implemented} / ${req.total}`}
          status={req.implemented === req.total && req.total > 0 ? 'ok' : 'warn'}
        />
        <Row
          label="테스트 통과율"
          value={`${testPassRate}%`}
          status={testPassRate === 100 && tests.total > 0 ? 'ok' : 'warn'}
        />
      </div>
    )
  }

  return null
}

function RunStatusSummary({
  gate,
  docs,
  onDocSelect,
}: {
  gate: string
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
}) {
  const runDocs = docs.filter(d => d.category === 'runs' && d.kind !== 'external')
  if (runDocs.length === 0) return null

  const currentIdx = GATE_ORDER.indexOf(gate)
  const currentRuns = runDocs.filter(d => d.runGate === gate)
  const upcomingRuns = runDocs.filter((d) => {
    const idx = GATE_ORDER.indexOf(d.runGate ?? '')
    return currentIdx >= 0 && idx > currentIdx
  })
  const otherRuns = runDocs.filter(d => !currentRuns.includes(d) && !upcomingRuns.includes(d))

  return (
    <div className="border-t border-[#374151] pt-3" data-testid="run-status-summary">
      <h3 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest mb-2">
        Run 현황
      </h3>
      <div className="grid gap-2 md:grid-cols-3">
        <RunBucket
          label="현재 Gate Run"
          docs={currentRuns}
          empty="진행 Run 없음"
          onDocSelect={onDocSelect}
          tone="current"
        />
        <RunBucket
          label="준비된 다음 Run"
          docs={upcomingRuns}
          empty="준비 Run 없음"
          onDocSelect={onDocSelect}
          tone="upcoming"
        />
        <RunBucket
          label="기타 Run"
          docs={otherRuns}
          empty="기타 Run 없음"
          onDocSelect={onDocSelect}
          tone="other"
        />
      </div>
    </div>
  )
}

function RunBucket({
  label,
  docs,
  empty,
  onDocSelect,
  tone,
}: {
  label: string
  docs: DocEntry[]
  empty: string
  onDocSelect?: (doc: DocNode) => void
  tone: 'current' | 'upcoming' | 'other'
}) {
  const toneClass = {
    current: 'text-cyan-300',
    upcoming: 'text-blue-300',
    other: 'text-[#9CA3AF]',
  }[tone]

  return (
    <div className="rounded-lg border border-[#374151] bg-[#0B1220] px-3 py-2">
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="text-xs text-[#9CA3AF]">{label}</span>
        <span className={`text-xs font-semibold ${toneClass}`}>{docs.length}</span>
      </div>
      {docs.length === 0 ? (
        <p className="text-xs text-[#4B5563]">{empty}</p>
      ) : (
        <ul className="space-y-1">
          {docs.slice(0, 3).map(doc => (
            <li key={doc.path}>
              <DocLink doc={doc} onDocSelect={onDocSelect} iconColor={toneClass} />
              <p className="ml-8 text-[11px] text-[#6B7280]">
                {doc.runGate ?? '-'} · {doc.runPersona ?? '-'} · {doc.runStatus ?? '-'}
              </p>
            </li>
          ))}
          {docs.length > 3 && (
            <li className="text-xs text-[#6B7280]">+{docs.length - 3}개 더 있음</li>
          )}
        </ul>
      )}
    </div>
  )
}

// ── Row 헬퍼 컴포넌트 ─────────────────────────────────────────────────────────

function Row({
  label,
  value,
  status,
}: {
  label: string
  value: string
  status?: 'ok' | 'warn'
}) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-[#9CA3AF]">{label}</span>
      <span
        className={`font-medium flex items-center gap-1.5 ${
          status === 'ok'
            ? 'text-green-400'
            : status === 'warn'
            ? 'text-yellow-400'
            : 'text-[#F9FAFB]'
        }`}
      >
        {status === 'ok' && <CheckCircle className="w-3.5 h-3.5" aria-hidden="true" />}
        {status === 'warn' && <AlertCircle className="w-3.5 h-3.5" aria-hidden="true" />}
        {value}
      </span>
    </div>
  )
}

// ── DocLink 헬퍼 컴포넌트 ─────────────────────────────────────────────────────

/**
 * DocEntry를 링크 또는 버튼으로 렌더링한다.
 * onDocSelect가 있으면 버튼으로, 없으면 Next.js Link로 렌더링한다.
 */
function DocLink({
  doc,
  onDocSelect,
  iconColor,
}: {
  doc: DocEntry
  onDocSelect?: (doc: DocNode) => void
  iconColor: string
}) {
  const commonClass =
    'flex items-center gap-2 text-sm text-[#D1D5DB] hover:text-[#F9FAFB] hover:bg-[#1F2937] rounded px-2 py-1.5 transition-colors w-full text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500'

  // DocEntry → DocNode 변환 (name + slug 필요)
  const toDocNode = (entry: DocEntry): DocNode => ({
    name: entry.name,
    slug: entry.path.replace(/\.md$/, '').split('/').filter(Boolean),
    type: 'file',
  })

  if (onDocSelect) {
    return (
      <button
        type="button"
        className={commonClass}
        onClick={() => onDocSelect(toDocNode(doc))}
      >
        <FileText className={`w-4 h-4 flex-shrink-0 ${iconColor}`} aria-hidden="true" />
        {doc.name}
      </button>
    )
  }

  const slug = doc.path.replace(/\.md$/, '').split('/').filter(Boolean)
  return (
    <Link href={`/docs/${slug.join('/')}`} className={commonClass}>
      <FileText className={`w-4 h-4 flex-shrink-0 ${iconColor}`} aria-hidden="true" />
      {doc.name}
    </Link>
  )
}

