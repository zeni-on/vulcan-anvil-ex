/**
 * @file components/GateProgressChart.tsx
 * @description Gate 완료율 Recharts BarChart (REQ-005-04)
 *
 * Recharts는 SSR 환경에서 window 접근 불가 — 이 파일은 "use client" 선언과
 * dynamic({ ssr: false }) 래핑을 함께 사용하여 클라이언트 전용으로 렌더링한다.
 * (REQ-009-01: Recharts dynamic import로 초기 HTML 렌더링 차단 방지)
 *
 * UT-005-10: done/in-progress/pending/blocked 상태별 색상 매핑
 *
 * @see docs/02-design/req-005-009-design.md §GateProgressChart
 * @see docs/02-design/ui-design.md §GateProgressChart (Recharts)
 */

'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from 'recharts'
import { SessionData, GateKey, GateStatusKey, GateStatus } from '@/lib/types'

/** Gate 상태별 색상 — ui-design.md 디자인 토큰 기준 */
const STATUS_COLOR: Record<GateStatus, string> = {
  done:          '#10B981', // gate-done
  'in-progress': '#3B82F6', // gate-in-progress
  pending:       '#374151', // gate-pending
  blocked:       '#EF4444', // gate-blocked
}

/** X축 한국어 약칭 매핑 — 차트에 표시할 6개 Gate만 포함한다 */
const GATE_LABEL: Record<GateStatusKey, string> = {
  gate1: 'Gate1',
  gate2: 'Gate2',
  gate3: 'Gate3',
  impl:  '구현',
  gate4: 'Gate4',
  gate5: 'Gate5',
}

const GATE_ORDER: GateStatusKey[] = ['gate1', 'gate2', 'gate3', 'impl', 'gate4', 'gate5']

interface GateProgressChartProps {
  session: SessionData
}

interface ChartDatum {
  key: GateStatusKey
  label: string
  value: number  // done=1, in-progress=0.5, pending=0, blocked=1 (강조)
  status: GateStatus
}

/**
 * Gate 상태를 Y축 값으로 변환한다.
 * done=1.0, in-progress=0.6, pending=0.2, blocked=1.0(빨간색 1.0으로 강조)
 */
function statusToValue(status: GateStatus): number {
  switch (status) {
    case 'done': return 1.0
    case 'in-progress': return 0.6
    case 'blocked': return 1.0
    case 'pending': return 0.2
  }
}

/** Recharts 툴팁 커스텀 — Gate 상태를 한국어로 표시 */
function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean
  payload?: Array<{ payload: ChartDatum }>
}) {
  if (!active || !payload?.length) return null
  const datum = payload[0].payload

  const statusLabel: Record<GateStatus, string> = {
    done: '완료',
    'in-progress': '진행중',
    pending: '대기',
    blocked: '블로커',
  }

  return (
    <div className="rounded-lg border border-[#374151] bg-[#1F2937] px-3 py-2 text-xs">
      <p className="font-semibold text-[#F9FAFB] mb-1">{datum.label}</p>
      <p style={{ color: STATUS_COLOR[datum.status] }}>{statusLabel[datum.status]}</p>
    </div>
  )
}

/**
 * Gate 완료율을 BarChart로 시각화하는 클라이언트 컴포넌트.
 * GateStatusStepper의 스텝 바와 병렬 제공하여 전체 완료율 비교를 지원한다.
 */
export default function GateProgressChart({ session }: GateProgressChartProps) {
  const data: ChartDatum[] = GATE_ORDER.map((key) => ({
    key,
    label: GATE_LABEL[key] ?? key,
    value: statusToValue(session.gate_status[key]),
    status: session.gate_status[key],
  }))

  return (
    <div data-testid="gate-progress-chart" className="w-full h-[160px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
          <XAxis
            dataKey="label"
            tick={{ fill: '#6B7280', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 1]}
            tick={false}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.key}
                fill={STATUS_COLOR[entry.status]}
                data-testid={`bar-${entry.key}-${entry.status}`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
