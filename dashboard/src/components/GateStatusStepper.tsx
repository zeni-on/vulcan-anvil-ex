/**
 * @file components/GateStatusStepper.tsx
 * @description Gate 1~5 단계 진행 인디케이터 (REQ-005-01)
 *
 * GateProgress.tsx의 스텝 바 방식을 기반으로 하되,
 * SessionData 타입을 직접 받고 blocked 상태(빨간색 원 + "!" 아이콘)를 추가한다.
 * 기존 GateProgress.tsx는 Session(legacy) 타입을 사용하므로 별도 컴포넌트로 분리한다.
 *
 * @see docs/02-design/req-005-009-design.md §GateProgressChart
 * @see docs/02-design/ui-design.md §GateStepIndicator
 */

import { SessionData, GateStatusKey, GateStatus } from '@/lib/types'

/** Gate 메타데이터 — 순서와 레이블 정의 */
const GATES: Array<{ key: GateStatusKey; label: string; sub: string }> = [
  { key: 'gate1', label: 'Gate 1', sub: '요구사항' },
  { key: 'gate2', label: 'Gate 2', sub: '설계' },
  { key: 'gate3', label: 'Gate 3', sub: '테스트 플랜' },
  { key: 'impl',  label: '구현',   sub: 'FE + BE' },
  { key: 'gate4', label: 'Gate 4', sub: 'QA 검토' },
  { key: 'gate5', label: 'Gate 5', sub: '최종 승인' },
]

/** Gate 상태별 원 스타일 — ui-design.md 색상 토큰 기준 */
function getCircleClass(status: GateStatus, isCurrent: boolean): string {
  if (status === 'done') return 'bg-green-500 text-white'
  if (status === 'blocked') return 'bg-red-500 text-white'
  if (isCurrent) return 'bg-blue-500 text-white ring-2 ring-blue-400 ring-offset-2 ring-offset-gray-950'
  return 'bg-gray-800 text-gray-500'
}

/** Gate 상태별 레이블 색상 */
function getLabelClass(status: GateStatus, isCurrent: boolean): string {
  if (status === 'done') return 'text-green-400'
  if (status === 'blocked') return 'text-red-400'
  if (isCurrent) return 'text-blue-400'
  return 'text-gray-500'
}

/** 연결선 색상 — done 완료 시에만 초록색 */
function getConnectorClass(status: GateStatus): string {
  return status === 'done' ? 'bg-green-500' : 'bg-gray-800'
}

/** Gate 상태별 원 내부 아이콘 */
function GateIcon({ status, index }: { status: GateStatus; index: number }) {
  if (status === 'done') return <span aria-hidden="true">✓</span>
  if (status === 'blocked') return <span aria-hidden="true">!</span>
  return <span aria-hidden="true">{index + 1}</span>
}

/** Gate 상태 한국어 레이블 */
function getStatusLabel(status: GateStatus): string {
  switch (status) {
    case 'done': return '완료'
    case 'in-progress': return '진행중'
    case 'pending': return '대기'
    case 'blocked': return '블로커'
  }
}

interface GateStatusStepperProps {
  session: SessionData
}

/**
 * Gate 1~5 진행 현황을 수평 스텝 인디케이터로 렌더링한다.
 * blocked 상태는 빨간색으로 강조하여 즉각적인 시각적 피드백을 제공한다.
 * current_gate가 'completed'이면 모든 Gate를 완료(초록색)로 표시한다.
 */
export default function GateStatusStepper({ session }: GateStatusStepperProps) {
  const isAllCompleted = session.current_gate === 'completed'

  const doneCount = isAllCompleted
    ? GATES.length
    : GATES.filter((g) => session.gate_status[g.key] === 'done').length
  const progressPct = Math.round((doneCount / GATES.length) * 100)

  return (
    <div data-testid="gate-status-stepper">
      {/* 스텝 인디케이터 — pt-2로 ring 클리핑 방지 */}
      <div
        role="list"
        aria-label="Gate 진행 현황"
        className="flex items-start overflow-x-auto pt-2 pb-2
          [&::-webkit-scrollbar]:h-1
          [&::-webkit-scrollbar-track]:bg-transparent
          [&::-webkit-scrollbar-thumb]:bg-zinc-700
          [&::-webkit-scrollbar-thumb]:rounded-full
          hover:[&::-webkit-scrollbar-thumb]:bg-zinc-500"
      >
        {GATES.map((gate, i) => {
          const status: GateStatus = isAllCompleted ? 'done' : session.gate_status[gate.key]
          const isCurrent = !isAllCompleted && session.current_gate === gate.key

          return (
            <div key={gate.key} className="flex items-start" role="listitem">
              <div className="flex flex-col items-center gap-2 min-w-[64px]">
                {/* 원 — 진행중이면 ping 애니메이션 */}
                <div className="relative">
                  {isCurrent && (
                    <span
                      aria-hidden="true"
                      className="absolute inset-0 rounded-full bg-blue-400 opacity-40 animate-ping"
                    />
                  )}
                  <div
                    className={`relative w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${getCircleClass(status, isCurrent)}`}
                    aria-label={`${gate.label}: ${getStatusLabel(status)}`}
                  >
                    <GateIcon status={status} index={i} />
                  </div>
                </div>
                <div className="text-center">
                  <div className={`text-xs font-medium ${getLabelClass(status, isCurrent)}`}>
                    {gate.label}
                  </div>
                  <div className="text-xs text-gray-600">{gate.sub}</div>
                  <div className={`text-[10px] mt-0.5 ${getLabelClass(status, isCurrent)}`}>
                    {getStatusLabel(status)}
                  </div>
                </div>
              </div>

              {i < GATES.length - 1 && (
                <div
                  aria-hidden="true"
                  className={`h-0.5 w-8 mt-5 mx-1 flex-shrink-0 ${getConnectorClass(status)}`}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* 진행률 텍스트 */}
      <p className="text-xs text-gray-500 mt-1">
        진행률{' '}
        <span className="font-semibold text-gray-300">{progressPct}%</span>
        <span className="ml-1 text-gray-600">({doneCount}/{GATES.length} Gate 완료)</span>
      </p>
    </div>
  )
}
