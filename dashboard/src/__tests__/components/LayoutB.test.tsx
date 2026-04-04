/**
 * @file __tests__/components/LayoutB.test.tsx
 * @description LayoutB 컴포넌트 단위 테스트
 *
 * 커버 항목:
 * - UT-012-14: CurrentGatePanel + StatsCards가 상단 풀 width 영역(data-testid="layout-b-stats")에 렌더링됨
 * - UT-012-15: GateStatusStepper + DocList가 하단 좌측 2/3(data-testid="layout-b-left")에 렌더링됨
 * - UT-012-16: CommitList가 하단 우측 1/3(data-testid="layout-b-commits")에 렌더링됨
 * - UT-012-17: session.stats 없을 때 상단 stats 섹션 미렌더링
 *
 * @see docs/02-design/req-012-design.md §LayoutB
 */

import React from 'react'
import { render, screen, within } from '@testing-library/react'
import '@testing-library/jest-dom'
import LayoutB from '@/components/LayoutB'
import { SessionData, DocEntry, CommitEntry, ProjectStats } from '@/lib/types'

// ── 공통 픽스처 ──────────────────────────────────────────────────────────────

const mockStats: ProjectStats = {
  requirements: {
    groups: 2,
    total: 8,
    implemented: 5,
    pending: 3,
    ac_defined: 7,
    ac_missing: 1,
  },
  tests: {
    total: 15,
    passed: 10,
    failed: 2,
    skipped: 1,
    pending: 2,
  },
  docs: {
    requirements: 1,
    design: 2,
    test_plan: 1,
    review: 0,
    total: 4,
  },
  updated_at: '2026-04-04',
}

const baseSession: SessionData = {
  project: 'Vulcan-Dev',
  vulcan_version: '1.0.0',
  current_gate: 'impl',
  gate_status: {
    gate1: 'done',
    gate2: 'done',
    gate3: 'done',
    impl: 'in-progress',
    gate4: 'pending',
    gate5: 'pending',
  },
  started: '2026-04-01',
  completed: [],
  pending: [],
  blocked: [],
}

const sessionWithStats: SessionData = { ...baseSession, stats: mockStats }

const mockDocs: DocEntry[] = [
  { name: 'REQUIREMENTS.md', path: 'docs/01-requirements/REQUIREMENTS.md', category: 'requirements' },
]

const mockCommits: CommitEntry[] = [
  {
    sha: 'abc1234567890',
    message: 'feat: 레이아웃 템플릿 구현',
    author: 'iamsong',
    date: new Date(Date.now() - 3_600_000).toISOString(),
  },
]

const defaultProps = {
  session: sessionWithStats,
  sessionLoading: false,
  sessionError: null,
  docs: mockDocs,
  docsLoading: false,
  docsError: null,
  commits: mockCommits,
  commitsLoading: false,
  commitsError: null,
  onDocSelect: jest.fn(),
}

// ── UT-012-14 ─────────────────────────────────────────────────────────────────

describe('UT-012-14: CurrentGatePanel + StatsCards가 상단 풀 width 영역에 렌더링됨', () => {
  it('session.stats가 있으면 data-testid="layout-b-stats" 컨테이너가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    expect(screen.getByTestId('layout-b-stats')).toBeInTheDocument()
  })

  it('layout-b-stats 안에 CurrentGatePanel이 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    const statsSection = screen.getByTestId('layout-b-stats')
    expect(within(statsSection).getByTestId('current-gate-panel')).toBeInTheDocument()
  })

  it('layout-b-stats 안에 StatsCards가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    const statsSection = screen.getByTestId('layout-b-stats')
    expect(within(statsSection).getByTestId('stats-cards')).toBeInTheDocument()
  })
})

// ── UT-012-15 ─────────────────────────────────────────────────────────────────

describe('UT-012-15: GateStatusStepper + DocList가 하단 좌측 2/3에 렌더링됨', () => {
  it('data-testid="layout-b-left" 컨테이너가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    expect(screen.getByTestId('layout-b-left')).toBeInTheDocument()
  })

  it('layout-b-left 안에 GateStatusStepper가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    const leftSection = screen.getByTestId('layout-b-left')
    expect(within(leftSection).getByTestId('gate-status-stepper')).toBeInTheDocument()
  })

  it('layout-b-left 안에 DocList가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    const leftSection = screen.getByTestId('layout-b-left')
    expect(within(leftSection).getByTestId('doc-list')).toBeInTheDocument()
  })

  it('좌측 섹션에 "Gate 진행 현황" 레이블이 표시된다', () => {
    render(<LayoutB {...defaultProps} />)
    const leftSection = screen.getByTestId('layout-b-left')
    expect(within(leftSection).getByText('Gate 진행 현황')).toBeInTheDocument()
  })

  it('좌측 섹션에 "산출물 문서" 레이블이 표시된다', () => {
    render(<LayoutB {...defaultProps} />)
    const leftSection = screen.getByTestId('layout-b-left')
    expect(within(leftSection).getByText('산출물 문서')).toBeInTheDocument()
  })
})

// ── UT-012-16 ─────────────────────────────────────────────────────────────────

describe('UT-012-16: CommitList가 하단 우측 1/3에 렌더링됨', () => {
  it('data-testid="layout-b-commits" 컨테이너가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    expect(screen.getByTestId('layout-b-commits')).toBeInTheDocument()
  })

  it('layout-b-commits 안에 CommitList(data-testid="commit-list")가 렌더링된다', () => {
    render(<LayoutB {...defaultProps} />)
    const commitsSection = screen.getByTestId('layout-b-commits')
    expect(within(commitsSection).getByTestId('commit-list')).toBeInTheDocument()
  })

  it('우측 섹션에 "최근 커밋" 레이블이 표시된다', () => {
    render(<LayoutB {...defaultProps} />)
    const commitsSection = screen.getByTestId('layout-b-commits')
    expect(within(commitsSection).getByText('최근 커밋')).toBeInTheDocument()
  })
})

// ── UT-012-17 (session.stats 없을 때 stats 섹션 미렌더링) ────────────────────

describe('UT-012-17: session.stats 없을 때 상단 stats 섹션 미렌더링', () => {
  const propsWithoutStats = {
    ...defaultProps,
    session: baseSession, // stats 없음
  }

  it('session.stats가 없으면 data-testid="layout-b-stats"가 렌더링되지 않는다', () => {
    render(<LayoutB {...propsWithoutStats} />)
    expect(screen.queryByTestId('layout-b-stats')).not.toBeInTheDocument()
  })

  it('session.stats가 없으면 CurrentGatePanel이 렌더링되지 않는다', () => {
    render(<LayoutB {...propsWithoutStats} />)
    expect(screen.queryByTestId('current-gate-panel')).not.toBeInTheDocument()
  })

  it('session.stats가 없어도 GateStatusStepper와 DocList는 렌더링된다', () => {
    render(<LayoutB {...propsWithoutStats} />)
    expect(screen.getByTestId('gate-status-stepper')).toBeInTheDocument()
    expect(screen.getByTestId('doc-list')).toBeInTheDocument()
  })
})
