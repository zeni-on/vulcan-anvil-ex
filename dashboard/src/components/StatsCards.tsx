/**
 * @file StatsCards.tsx
 * @description 프로젝트 요구사항·테스트 통계 카드 그리드 (REQ-011-03)
 *
 * ProjectStats.requirements와 ProjectStats.tests 데이터를 받아
 * 요구사항 현황(5개 카드)과 테스트 현황(4개 카드)을 렌더링한다.
 *
 * 원본: Vulcan-Anvil/templates/dashboard/src/components/StatsCards.tsx
 * 변경 사항:
 * - import를 @/lib/types의 ProjectStats로 교체
 * - ac_missing은 숫자이므로 배지 목록 대신 경고 색상으로 표시
 * - 다크 테마 색상 토큰 유지 (bg-[#111827], border-[#374151])
 *
 * @see docs/02-design/req-011-design.md §6
 */

import { ProjectStats } from '@/lib/types'
import {
  FileText,
  FlaskConical,
  CheckCircle,
  XCircle,
  AlertCircle,
  Layers,
  BookOpen,
} from 'lucide-react'

// ── StatCard 내부 컴포넌트 ────────────────────────────────────────────────────

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  sub?: string
  color?: 'default' | 'green' | 'red' | 'yellow' | 'blue'
}

/**
 * 단일 통계 카드.
 * 아이콘, 라벨, 값, 보조 텍스트를 가로로 배치한다.
 */
function StatCard({ icon, label, value, sub, color = 'default' }: StatCardProps) {
  const valueColor = {
    default: 'text-[#F9FAFB]',
    green:   'text-green-400',
    red:     'text-red-400',
    yellow:  'text-yellow-400',
    blue:    'text-blue-400',
  }[color]

  return (
    <div
      className="bg-[#111827] rounded-lg px-3 py-3 flex items-center gap-3 border border-[#374151]"
      data-testid="stat-card"
    >
      <div className="text-[#4B5563]">{icon}</div>
      <div className="min-w-0">
        <div className="text-xs text-[#6B7280] leading-tight">{label}</div>
        <div className={`text-xl font-bold ${valueColor}`}>{value}</div>
        {sub && <div className="text-xs text-[#6B7280] mt-0.5">{sub}</div>}
      </div>
    </div>
  )
}

// ── StatsCards 컴포넌트 ───────────────────────────────────────────────────────

interface StatsCardsProps {
  stats: ProjectStats
}

/**
 * 요구사항 현황 + 테스트 현황 카드 그리드.
 *
 * - AC 커버리지: ac_defined / total * 100% (total === 0이면 0%로 처리, UT-011-12)
 * - 테스트 통과율: tests.passed / tests.total * 100% (total === 0이면 0%로 처리)
 * - ac_missing > 0이면 AC 커버리지 카드를 경고 색상(yellow)으로 표시 (UT-011-13)
 */
export default function StatsCards({ stats }: StatsCardsProps) {
  const { requirements: req, tests, docs, backlog } = stats
  const backlogTypeSummary = backlog?.by_type
    ? `IDEA ${backlog.by_type.idea} / CR ${backlog.by_type.cr} / ISSUE ${backlog.by_type.issue}`
    : backlog?.by_priority.p0
      ? `P0 ${backlog.by_priority.p0} items`
      : undefined

  // 파생 값 계산 — 나누기 0 방어 (UT-011-12)
  const acCoverage = req.total > 0
    ? Math.round((req.ac_defined / req.total) * 100)
    : 0

  const testPassRate = tests.total > 0
    ? Math.round((tests.passed / tests.total) * 100)
    : 0

  return (
    <div className="space-y-6" data-testid="stats-cards">
      {/* 요구사항 현황 */}
      <div>
        <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest mb-3">
          요구사항 현황
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          <StatCard
            icon={<Layers className="w-5 h-5" />}
            label="REQ 그룹"
            value={req.groups}
            sub="REQ-NNN"
            color="blue"
          />
          <StatCard
            icon={<FileText className="w-5 h-5" />}
            label="상세 요구사항"
            value={req.total}
            sub="REQ-NNN-NN"
          />
          <StatCard
            icon={<CheckCircle className="w-5 h-5" />}
            label="구현완료"
            value={req.implemented}
            sub={`/ ${req.total}건`}
            color={req.implemented === req.total && req.total > 0 ? 'green' : 'yellow'}
          />
          <StatCard
            icon={<CheckCircle className="w-5 h-5" />}
            label="AC 정의 완료"
            value={req.ac_defined}
            sub={`/ ${req.total}건`}
            color={req.ac_missing === 0 && req.total > 0 ? 'green' : 'yellow'}
          />
          {/* ac_missing > 0이면 경고 아이콘과 경고 색상으로 표시 (UT-011-13) */}
          <StatCard
            icon={
              req.ac_missing > 0
                ? <AlertCircle className="w-5 h-5" data-testid="ac-missing-warning" />
                : <CheckCircle className="w-5 h-5" />
            }
            label="AC 커버리지"
            value={`${acCoverage}%`}
            sub={req.ac_missing > 0 ? `미정의 ${req.ac_missing}건` : '완전 커버'}
            color={req.ac_missing === 0 && req.total > 0 ? 'green' : 'yellow'}
          />
        </div>
      </div>

      {/* 테스트 현황 */}
      <div>
        <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest mb-3">
          테스트 현황
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard
            icon={<FlaskConical className="w-5 h-5" />}
            label="전체 테스트"
            value={tests.total}
            sub="TST-ID"
            color="blue"
          />
          <StatCard
            icon={<CheckCircle className="w-5 h-5" />}
            label="통과"
            value={tests.passed}
            sub={tests.total > 0 ? `${testPassRate}%` : '-'}
            color={tests.passed > 0 ? 'green' : 'default'}
          />
          <StatCard
            icon={<XCircle className="w-5 h-5" />}
            label="실패"
            value={tests.failed}
            color={tests.failed > 0 ? 'red' : 'default'}
          />
          <StatCard
            icon={<AlertCircle className="w-5 h-5" />}
            label="미실행"
            value={tests.pending}
            sub={tests.skipped > 0 ? `Skip ${tests.skipped}건` : undefined}
            color="yellow"
          />
        </div>
      </div>

      {/* 백로그 현황 — backlog 데이터가 있을 때만 표시 */}
      <div>
        <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest mb-3">
          Docs
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard
            icon={<FileText className="w-5 h-5" />}
            label="Discovery"
            value={docs.discovery ?? 0}
            color={(docs.discovery ?? 0) > 0 ? 'blue' : 'default'}
          />
          <StatCard
            icon={<FileText className="w-5 h-5" />}
            label="Security"
            value={docs.security ?? 0}
            color={(docs.security ?? 0) > 0 ? 'blue' : 'default'}
          />
          <StatCard
            icon={<BookOpen className="w-5 h-5" />}
            label="Backlog"
            value={docs.backlog ?? 0}
            color={(docs.backlog ?? 0) > 0 ? 'yellow' : 'default'}
          />
          <StatCard
            icon={<Layers className="w-5 h-5" />}
            label="Runs"
            value={docs.runs ?? 0}
            color={(docs.runs ?? 0) > 0 ? 'green' : 'default'}
          />
        </div>
      </div>
      {backlog && (
        <div data-testid="backlog-stats">
          <h2 className="text-xs font-semibold text-[#9CA3AF] uppercase tracking-widest mb-3">
            백로그 현황
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard
              icon={<BookOpen className="w-5 h-5" />}
              label="Active"
              value={backlog.active}
              sub={backlogTypeSummary}
              color={backlog.active > 0 ? 'yellow' : 'default'}
            />
            <StatCard
              icon={<CheckCircle className="w-5 h-5" />}
              label="Done"
              value={backlog.done}
              color={backlog.done > 0 ? 'green' : 'default'}
            />
            <StatCard
              icon={<XCircle className="w-5 h-5" />}
              label="Rejected"
              value={backlog.rejected}
              color="default"
            />
            <StatCard
              icon={<AlertCircle className="w-5 h-5" />}
              label="레벨별"
              value={backlog.active}
              sub={`T ${backlog.by_level.trivial} / S ${backlog.by_level.small} / M ${backlog.by_level.major}`}
              color="default"
            />
          </div>
        </div>
      )}
    </div>
  )
}
