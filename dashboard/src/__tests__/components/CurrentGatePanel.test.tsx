/**
 * @file __tests__/components/CurrentGatePanel.test.tsx
 * @description CurrentGatePanel 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - UT-011-14: current_gate === 'gate1'이면 REQ/AC 현황 행 렌더링
 * - UT-011-15: current_gate === 'gate2'이면 category === 'design'인 DocEntry만 표시
 * - UT-011-16: current_gate === 'impl'이면 구현 진행률 바 렌더링
 * - UT-011-17: current_gate === 'completed'이면 컴포넌트가 null 반환
 *
 * @see docs/02-design/req-011-design.md §7
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import CurrentGatePanel from '@/components/CurrentGatePanel'
import { SessionData, ProjectStats, DocEntry } from '@/lib/types'

// ── 공통 픽스처 ──────────────────────────────────────────────────────────────

const baseGateStatus: SessionData['gate_status'] = {
  gate1: 'done',
  gate2: 'done',
  gate3: 'done',
  impl:  'in-progress',
  gate4: 'pending',
  gate5: 'pending',
}

function makeSession(current_gate: SessionData['current_gate']): SessionData {
  return {
    project: 'Vulcan-Dev',
    vulcan_version: '1.0.0',
    current_gate,
    gate_status: baseGateStatus,
    started: '2026-04-01',
    completed: [],
    pending: [],
    blocked: [],
  }
}

const mockStats: ProjectStats = {
  requirements: {
    groups:      3,
    total:       12,
    implemented: 8,
    pending:     4,
    ac_defined:  10,
    ac_missing:  2,
  },
  tests: {
    total:   20,
    passed:  14,
    failed:  3,
    skipped: 1,
    pending: 2,
  },
  docs: {
    requirements: 1,
    design:       3,
    test_plan:    1,
    review:       2,
    total:        7,
  },
  updated_at: '2026-04-04',
}

const mockDocs: DocEntry[] = [
  { name: 'REQUIREMENTS.md',    path: 'docs/01-requirements/REQUIREMENTS.md',   category: 'requirements' },
  { name: 'req-001-design.md',  path: 'docs/02-design/req-001-design.md',        category: 'design' },
  { name: 'req-011-design.md',  path: 'docs/02-design/req-011-design.md',        category: 'design' },
  { name: 'TEST_PLAN.md',       path: 'docs/03-test-plan/TEST_PLAN.md',          category: 'test-plan' },
  { name: 'req-001-review.md',  path: 'docs/04-review/req-001-review.md',        category: 'review' },
]

const mockDocsWithRuns: DocEntry[] = [
  ...mockDocs,
  {
    name: 'RUN-001_phase0_v0.1',
    path: 'docs/runs/RUN-001_phase0_v0.1.md',
    category: 'runs',
    runGate: 'phase0',
    runPersona: 'discovery',
    runStatus: 'Draft',
  },
  {
    name: 'RUN-002_gate1_v0.1',
    path: 'docs/runs/RUN-002_gate1_v0.1.md',
    category: 'runs',
    runGate: 'gate1',
    runPersona: 'requirements',
    runStatus: 'Draft',
  },
]

// ── UT-011-14: gate1일 때 REQ/AC 현황 행 렌더링 ──────────────────────────────

describe('UT-011-14: current_gate === "gate1"', () => {
  it('data-testid="gate-content-gate1" 영역이 렌더링된다', () => {
    render(<CurrentGatePanel session={makeSession('gate1')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByTestId('gate-content-gate1')).toBeInTheDocument()
  })

  it('상위 요구사항 행이 표시된다', () => {
    render(<CurrentGatePanel session={makeSession('gate1')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByText('상위 요구사항')).toBeInTheDocument()
  })

  it('상세 요구사항 행이 표시된다', () => {
    render(<CurrentGatePanel session={makeSession('gate1')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByText('상세 요구사항')).toBeInTheDocument()
  })

  it('AC 정의 완료 행이 표시된다', () => {
    render(<CurrentGatePanel session={makeSession('gate1')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByText('AC 정의 완료')).toBeInTheDocument()
  })
})

describe('Run 현황 표시', () => {
  it('현재 Gate Run과 준비된 다음 Run을 구분해 표시한다', () => {
    render(<CurrentGatePanel session={makeSession('phase0')} stats={mockStats} docs={mockDocsWithRuns} />)

    expect(screen.getByTestId('run-status-summary')).toBeInTheDocument()
    expect(screen.getByText('현재 Gate Run')).toBeInTheDocument()
    expect(screen.getByText('준비된 다음 Run')).toBeInTheDocument()
    expect(screen.getByText('RUN-001_phase0_v0.1')).toBeInTheDocument()
    expect(screen.getByText('RUN-002_gate1_v0.1')).toBeInTheDocument()
    expect(screen.getByText('phase0 · discovery · Draft')).toBeInTheDocument()
    expect(screen.getByText('gate1 · requirements · Draft')).toBeInTheDocument()
  })
})

// ── UT-011-15: gate2일 때 category === 'design'인 DocEntry만 표시 ─────────────

describe('UT-011-15: current_gate === "gate2"', () => {
  it('data-testid="gate-content-gate2" 영역이 렌더링된다', () => {
    render(<CurrentGatePanel session={makeSession('gate2')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByTestId('gate-content-gate2')).toBeInTheDocument()
  })

  it('category === "design"인 문서 이름이 표시된다', () => {
    render(<CurrentGatePanel session={makeSession('gate2')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByText('req-001-design.md')).toBeInTheDocument()
    expect(screen.getByText('req-011-design.md')).toBeInTheDocument()
  })

  it('category !== "design"인 문서는 표시되지 않는다', () => {
    render(<CurrentGatePanel session={makeSession('gate2')} stats={mockStats} docs={mockDocs} />)
    expect(screen.queryByText('REQUIREMENTS.md')).not.toBeInTheDocument()
    expect(screen.queryByText('TEST_PLAN.md')).not.toBeInTheDocument()
    expect(screen.queryByText('req-001-review.md')).not.toBeInTheDocument()
  })
})

// ── UT-011-16: impl일 때 구현 진행률 바 렌더링 ───────────────────────────────

describe('UT-011-16: current_gate === "impl"', () => {
  it('data-testid="gate-content-impl" 영역이 렌더링된다', () => {
    render(<CurrentGatePanel session={makeSession('impl')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByTestId('gate-content-impl')).toBeInTheDocument()
  })

  it('role="progressbar"인 요소가 렌더링된다', () => {
    render(<CurrentGatePanel session={makeSession('impl')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('구현 진행률 텍스트(구현 진행률)가 표시된다', () => {
    render(<CurrentGatePanel session={makeSession('impl')} stats={mockStats} docs={mockDocs} />)
    expect(screen.getByText('구현 진행률')).toBeInTheDocument()
  })

  it('진행률 값 텍스트(8 / 12)가 표시된다', () => {
    render(<CurrentGatePanel session={makeSession('impl')} stats={mockStats} docs={mockDocs} />)
    // "8 / 12 (67%)" 형태로 출력됨
    expect(screen.getByText(/8 \/ 12/)).toBeInTheDocument()
  })
})

// ── UT-011-17: completed이면 null 반환 ───────────────────────────────────────

describe('UT-011-17: current_gate === "completed"', () => {
  it('컴포넌트가 null을 반환하여 아무것도 렌더링되지 않는다', () => {
    const { container } = render(
      <CurrentGatePanel session={makeSession('completed')} stats={mockStats} docs={mockDocs} />
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('data-testid="current-gate-panel"이 없다', () => {
    render(<CurrentGatePanel session={makeSession('completed')} stats={mockStats} docs={mockDocs} />)
    expect(screen.queryByTestId('current-gate-panel')).not.toBeInTheDocument()
  })
})
