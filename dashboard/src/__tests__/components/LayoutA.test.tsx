/**
 * @file __tests__/components/LayoutA.test.tsx
 * @description LayoutA 컴포넌트 단위 테스트
 *
 * 커버 항목:
 * - UT-012-10: DocList가 좌측 1/4 컬럼(data-testid="layout-a-docs")에 렌더링됨
 * - UT-012-11: GateStatusStepper, CurrentGatePanel, StatsCards가 중앙 2/4 컬럼에 순서대로 렌더링됨
 * - UT-012-12: CommitList가 우측 1/4 컬럼(data-testid="layout-a-commits")에 렌더링됨
 * - UT-012-13: session.stats 없을 때 CurrentGatePanel, StatsCards 미렌더링
 *
 * @see docs/02-design/req-012-design.md §LayoutA
 */

import React from 'react'
import { render, screen, within } from '@testing-library/react'
import '@testing-library/jest-dom'
import LayoutA from '@/components/LayoutA'
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

// ── UT-012-10 ─────────────────────────────────────────────────────────────────

describe('UT-012-10: DocList가 좌측 1/4 컬럼에 렌더링됨', () => {
  it('data-testid="layout-a-docs" 컨테이너가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    expect(screen.getByTestId('layout-a-docs')).toBeInTheDocument()
  })

  it('layout-a-docs 컨테이너 안에 data-testid="doc-list"가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    const docsContainer = screen.getByTestId('layout-a-docs')
    expect(within(docsContainer).getByTestId('doc-list')).toBeInTheDocument()
  })

  it('DocList 섹션에 "산출물 문서" 레이블이 표시된다', () => {
    render(<LayoutA {...defaultProps} />)
    const docsContainer = screen.getByTestId('layout-a-docs')
    expect(within(docsContainer).getByText('산출물 문서')).toBeInTheDocument()
  })
})

// ── UT-012-11 ─────────────────────────────────────────────────────────────────

describe('UT-012-11: GateStatusStepper, CurrentGatePanel, StatsCards가 중앙 컬럼에 렌더링됨', () => {
  it('data-testid="layout-a-center" 컨테이너가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    expect(screen.getByTestId('layout-a-center')).toBeInTheDocument()
  })

  it('중앙 컬럼에 GateStatusStepper(data-testid="gate-status-stepper")가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    const center = screen.getByTestId('layout-a-center')
    expect(within(center).getByTestId('gate-status-stepper')).toBeInTheDocument()
  })

  it('session.stats가 있으면 중앙 컬럼에 CurrentGatePanel이 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    const center = screen.getByTestId('layout-a-center')
    expect(within(center).getByTestId('current-gate-panel')).toBeInTheDocument()
  })

  it('session.stats가 있으면 중앙 컬럼에 StatsCards가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    const center = screen.getByTestId('layout-a-center')
    expect(within(center).getByTestId('stats-cards')).toBeInTheDocument()
  })
})

// ── UT-012-12 ─────────────────────────────────────────────────────────────────

describe('UT-012-12: CommitList가 우측 1/4 컬럼에 렌더링됨', () => {
  it('data-testid="layout-a-commits" 컨테이너가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    expect(screen.getByTestId('layout-a-commits')).toBeInTheDocument()
  })

  it('layout-a-commits 컨테이너 안에 data-testid="commit-list"가 렌더링된다', () => {
    render(<LayoutA {...defaultProps} />)
    const commitsContainer = screen.getByTestId('layout-a-commits')
    expect(within(commitsContainer).getByTestId('commit-list')).toBeInTheDocument()
  })

  it('CommitList 섹션에 "최근 커밋" 레이블이 표시된다', () => {
    render(<LayoutA {...defaultProps} />)
    const commitsContainer = screen.getByTestId('layout-a-commits')
    expect(within(commitsContainer).getByText('최근 커밋')).toBeInTheDocument()
  })
})

// ── UT-012-13 ─────────────────────────────────────────────────────────────────

describe('UT-012-13: session.stats 없을 때 CurrentGatePanel, StatsCards 미렌더링', () => {
  const propsWithoutStats = {
    ...defaultProps,
    session: baseSession, // stats 없음
  }

  it('session.stats가 없으면 CurrentGatePanel이 렌더링되지 않는다', () => {
    render(<LayoutA {...propsWithoutStats} />)
    expect(screen.queryByTestId('current-gate-panel')).not.toBeInTheDocument()
  })

  it('session.stats가 없으면 StatsCards가 렌더링되지 않는다', () => {
    render(<LayoutA {...propsWithoutStats} />)
    expect(screen.queryByTestId('stats-cards')).not.toBeInTheDocument()
  })

  it('session.stats가 없어도 GateStatusStepper는 렌더링된다', () => {
    render(<LayoutA {...propsWithoutStats} />)
    expect(screen.getByTestId('gate-status-stepper')).toBeInTheDocument()
  })
})
