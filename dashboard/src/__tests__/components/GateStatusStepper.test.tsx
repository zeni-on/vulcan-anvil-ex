/**
 * @file __tests__/components/GateStatusStepper.test.tsx
 * @description GateStatusStepper 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - Gate 1~5 + 구현 스텝 렌더링 (6개 스텝)
 * - 각 Gate 상태별 aria-label 확인 (done, in-progress, pending, blocked)
 * - done 상태 → "완료" 레이블
 * - blocked 상태 → "블로커" 레이블
 * - in-progress 상태 → "진행중" 레이블
 * - data-testid="gate-status-stepper" 존재 확인
 * - role="list" 접근성 속성 확인
 *
 * @see docs/02-design/req-005-009-design.md §GateProgressChart
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import GateStatusStepper from '@/components/GateStatusStepper'
import { SessionData } from '@/lib/types'

/** 모든 상태를 포함한 테스트용 SessionData */
const mockSession: SessionData = {
  project: 'Test Project',
  vulcan_version: '1.0.0',
  current_gate: 'gate3',
  gate_status: {
    gate1: 'done',
    gate2: 'done',
    gate3: 'in-progress',
    impl:  'pending',
    gate4: 'pending',
    gate5: 'blocked',
  },
  started: '2026-04-01',
  completed: [],
  pending: [],
  blocked: [],
}

/** gate5 상태만 변경한 헬퍼 */
function renderWithStatus(overrides: Partial<SessionData['gate_status']>) {
  const session: SessionData = {
    ...mockSession,
    gate_status: { ...mockSession.gate_status, ...overrides },
  }
  return render(<GateStatusStepper session={session} />)
}

describe('GateStatusStepper', () => {
  it('data-testid="gate-status-stepper" 컨테이너를 렌더링한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getByTestId('gate-status-stepper')).toBeInTheDocument()
  })

  it('role="list" 접근성 속성을 가진다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getByRole('list', { name: 'Gate 진행 현황' })).toBeInTheDocument()
  })

  it('done 상태 Gate는 "완료" 레이블을 표시한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    // gate1, gate2가 done
    expect(screen.getByLabelText('Gate 1: 완료')).toBeInTheDocument()
    expect(screen.getByLabelText('Gate 2: 완료')).toBeInTheDocument()
  })

  it('in-progress 상태 Gate는 "진행중" 레이블을 표시한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getByLabelText('Gate 3: 진행중')).toBeInTheDocument()
  })

  it('pending 상태 Gate는 "대기" 레이블을 표시한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getByLabelText('구현: 대기')).toBeInTheDocument()
  })

  it('blocked 상태 Gate는 "블로커" 레이블을 표시한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getByLabelText('Gate 5: 블로커')).toBeInTheDocument()
  })

  it('모든 6개 스텝(listitem)을 렌더링한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getAllByRole('listitem')).toHaveLength(6)
  })

  it('gate1 done → 체크 아이콘(✓) 텍스트를 표시한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    // done 상태의 스텝 원 내부에 "✓" 렌더링
    const checkmarks = screen.getAllByText('✓')
    expect(checkmarks.length).toBeGreaterThanOrEqual(1)
  })

  it('blocked 상태 → "!" 아이콘 텍스트를 표시한다', () => {
    render(<GateStatusStepper session={mockSession} />)
    expect(screen.getByText('!')).toBeInTheDocument()
  })

  it('모든 Gate가 pending 상태일 때 정상 렌더링한다', () => {
    renderWithStatus({
      gate1: 'pending',
      gate2: 'pending',
      gate3: 'pending',
      impl:  'pending',
      gate4: 'pending',
      gate5: 'pending',
    })
    expect(screen.getByTestId('gate-status-stepper')).toBeInTheDocument()
    expect(screen.getAllByText('대기')).toHaveLength(6)
  })
})
