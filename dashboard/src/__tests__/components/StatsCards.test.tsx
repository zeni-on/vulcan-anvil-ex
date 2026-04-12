/**
 * @file __tests__/components/StatsCards.test.tsx
 * @description StatsCards 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - UT-011-12: stats.requirements.total이 0일 때 AC 커버리지 0% 표시 (나누기 0 방어)
 * - UT-011-13: stats.requirements.ac_missing > 0이면 경고 색상 표시
 *
 * @see docs/02-design/req-011-design.md §6
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import StatsCards from '@/components/StatsCards'
import { ProjectStats } from '@/lib/types'

// ── 공통 픽스처 ──────────────────────────────────────────────────────────────

function makeStats(overrides?: Partial<ProjectStats['requirements']>): ProjectStats {
  return {
    requirements: {
      groups:      3,
      total:       10,
      implemented: 7,
      pending:     3,
      ac_defined:  8,
      ac_missing:  2,
      ...overrides,
    },
    tests: {
      total:   20,
      passed:  15,
      failed:  2,
      skipped: 1,
      pending: 2,
    },
    docs: {
      requirements: 1,
      design:       3,
      test_plan:    1,
      review:       1,
      total:        6,
    },
    updated_at: '2026-04-04',
  }
}

// ── UT-011-12: total === 0일 때 AC 커버리지 0% ───────────────────────────────

describe('UT-011-12: requirements.total === 0일 때 나누기 0 방어', () => {
  it('AC 커버리지를 0%로 표시한다', () => {
    const stats = makeStats({ total: 0, ac_defined: 0, ac_missing: 0 })
    render(<StatsCards stats={stats} />)
    expect(screen.getByText('0%')).toBeInTheDocument()
  })

  it('data-testid="stats-cards" 컨테이너가 렌더링된다', () => {
    const stats = makeStats({ total: 0, ac_defined: 0, ac_missing: 0 })
    render(<StatsCards stats={stats} />)
    expect(screen.getByTestId('stats-cards')).toBeInTheDocument()
  })
})

// ── UT-011-13: ac_missing > 0이면 경고 표시 ─────────────────────────────────

describe('UT-011-13: ac_missing > 0이면 경고 색상 표시', () => {
  it('ac_missing > 0일 때 경고 아이콘(data-testid="ac-missing-warning")이 렌더링된다', () => {
    const stats = makeStats({ ac_missing: 3 })
    render(<StatsCards stats={stats} />)
    expect(screen.getByTestId('ac-missing-warning')).toBeInTheDocument()
  })

  it('ac_missing > 0일 때 미정의 건수 텍스트가 표시된다', () => {
    const stats = makeStats({ ac_missing: 3 })
    render(<StatsCards stats={stats} />)
    expect(screen.getByText('미정의 3건')).toBeInTheDocument()
  })

  it('ac_missing === 0일 때 경고 아이콘이 렌더링되지 않는다', () => {
    const stats = makeStats({ ac_missing: 0, ac_defined: 10, total: 10 })
    render(<StatsCards stats={stats} />)
    expect(screen.queryByTestId('ac-missing-warning')).not.toBeInTheDocument()
  })

  it('ac_missing === 0일 때 "완전 커버" 텍스트가 표시된다', () => {
    const stats = makeStats({ ac_missing: 0, ac_defined: 10, total: 10 })
    render(<StatsCards stats={stats} />)
    expect(screen.getByText('완전 커버')).toBeInTheDocument()
  })
})

// ── 추가: 기본 렌더링 검증 ────────────────────────────────────────────────────

describe('StatsCards 기본 렌더링', () => {
  it('요구사항 현황 섹션 헤더를 표시한다', () => {
    render(<StatsCards stats={makeStats()} />)
    expect(screen.getByText('요구사항 현황')).toBeInTheDocument()
  })

  it('테스트 현황 섹션 헤더를 표시한다', () => {
    render(<StatsCards stats={makeStats()} />)
    expect(screen.getByText('테스트 현황')).toBeInTheDocument()
  })

  it('테스트 통과율을 계산하여 표시한다 (15/20 = 75%)', () => {
    render(<StatsCards stats={makeStats()} />)
    expect(screen.getByText('75%')).toBeInTheDocument()
  })
})

// ── 백로그 통계 렌더링 ──────────────────────────────────────────────────────

describe('StatsCards 백로그 현황', () => {
  const statsWithBacklog = (): ProjectStats => ({
    ...makeStats(),
    backlog: {
      active:   4,
      done:     1,
      rejected: 0,
      by_level:    { trivial: 3, small: 1, major: 0 },
      by_priority: { p0: 1, p1: 1, p2: 2, p3: 0 },
    },
  })

  it('backlog가 있으면 백로그 현황 섹션을 표시한다', () => {
    render(<StatsCards stats={statsWithBacklog()} />)
    expect(screen.getByTestId('backlog-stats')).toBeInTheDocument()
    expect(screen.getByText('백로그 현황')).toBeInTheDocument()
  })

  it('backlog가 없으면 백로그 현황 섹션을 표시하지 않는다', () => {
    render(<StatsCards stats={makeStats()} />)
    expect(screen.queryByTestId('backlog-stats')).not.toBeInTheDocument()
  })

  it('Active/Done/Rejected 건수를 표시한다', () => {
    render(<StatsCards stats={statsWithBacklog()} />)
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Done')).toBeInTheDocument()
    expect(screen.getByText('Rejected')).toBeInTheDocument()
  })

  it('P0 건수가 있으면 보조 텍스트로 표시한다', () => {
    render(<StatsCards stats={statsWithBacklog()} />)
    expect(screen.getByText('P0 1건')).toBeInTheDocument()
  })
})
