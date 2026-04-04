/**
 * @file __tests__/components/ProjectDetailPage.test.tsx
 * @description projects/[id]/page.tsx 통계 섹션 조건부 렌더링 테스트
 *
 * 커버 항목:
 * - UT-011-18: session.stats가 undefined이면 통계 섹션 미렌더링
 * - UT-011-19: session.stats가 있으면 StatsCards와 CurrentGatePanel 모두 렌더링
 *
 * 구현 전략:
 * page.tsx의 전체 렌더링 대신, 통계 섹션의 조건부 렌더링 로직을
 * 동일한 패턴을 따르는 인라인 컴포넌트로 검증한다.
 * (SWR 훅, useParams 등의 복잡한 의존성을 격리하기 위함)
 *
 * @see docs/02-design/req-011-design.md §8
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { SessionData, ProjectStats, DocEntry, DocNode } from '@/lib/types'
import StatsCards from '@/components/StatsCards'
import CurrentGatePanel from '@/components/CurrentGatePanel'

// ── 공통 픽스처 ──────────────────────────────────────────────────────────────

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

const baseSession: SessionData = {
  project: 'Vulcan-Dev',
  vulcan_version: '1.0.0',
  current_gate: 'impl',
  gate_status: {
    gate1: 'done',
    gate2: 'done',
    gate3: 'done',
    impl:  'in-progress',
    gate4: 'pending',
    gate5: 'pending',
  },
  started: '2026-04-01',
  completed: [],
  pending: [],
  blocked: [],
}

const mockDocs: DocEntry[] = []

// ── 통계 섹션 조건부 렌더링 로직을 추출한 테스트용 컴포넌트 ──────────────────
// page.tsx에서 통계 섹션을 담당하는 조건부 렌더링과 동일한 패턴:
// {session?.stats && (
//   <div data-testid="stats-section">
//     <CurrentGatePanel session={session} stats={session.stats} docs={docs} onDocSelect={...} />
//     <StatsCards stats={session.stats} />
//   </div>
// )}

interface TestPageProps {
  session: SessionData | null
  docs: DocEntry[]
  onDocSelect?: (doc: DocNode) => void
}

/**
 * page.tsx의 통계 섹션 조건부 렌더링을 재현한 테스트용 컴포넌트.
 * 실제 page.tsx와 동일한 렌더링 조건(session?.stats)을 사용한다.
 */
function StatsSectionUnderTest({ session, docs, onDocSelect }: TestPageProps) {
  return (
    <div>
      {session?.stats && (
        <div data-testid="stats-section">
          <CurrentGatePanel
            session={session}
            stats={session.stats}
            docs={docs}
            onDocSelect={onDocSelect}
          />
          <StatsCards stats={session.stats} />
        </div>
      )}
    </div>
  )
}

// ── UT-011-18: stats 없으면 통계 섹션 미렌더링 ──────────────────────────────

describe('UT-011-18: session.stats가 undefined이면 통계 섹션 미렌더링', () => {
  it('data-testid="stats-section"이 렌더링되지 않는다', () => {
    // stats가 없는 세션 (baseSession에는 stats 필드 없음)
    render(<StatsSectionUnderTest session={baseSession} docs={mockDocs} />)
    expect(screen.queryByTestId('stats-section')).not.toBeInTheDocument()
  })

  it('data-testid="stats-cards"가 렌더링되지 않는다', () => {
    render(<StatsSectionUnderTest session={baseSession} docs={mockDocs} />)
    expect(screen.queryByTestId('stats-cards')).not.toBeInTheDocument()
  })

  it('data-testid="current-gate-panel"이 렌더링되지 않는다', () => {
    render(<StatsSectionUnderTest session={baseSession} docs={mockDocs} />)
    expect(screen.queryByTestId('current-gate-panel')).not.toBeInTheDocument()
  })

  it('session이 null일 때도 통계 섹션이 렌더링되지 않는다', () => {
    render(<StatsSectionUnderTest session={null} docs={mockDocs} />)
    expect(screen.queryByTestId('stats-section')).not.toBeInTheDocument()
  })
})

// ── UT-011-19: stats 있으면 통계 섹션 렌더링 ─────────────────────────────────

describe('UT-011-19: session.stats가 있으면 StatsCards와 CurrentGatePanel 렌더링', () => {
  const sessionWithStats: SessionData = { ...baseSession, stats: mockStats }

  it('data-testid="stats-section"이 렌더링된다', () => {
    render(<StatsSectionUnderTest session={sessionWithStats} docs={mockDocs} />)
    expect(screen.getByTestId('stats-section')).toBeInTheDocument()
  })

  it('data-testid="stats-cards"가 렌더링된다', () => {
    render(<StatsSectionUnderTest session={sessionWithStats} docs={mockDocs} />)
    expect(screen.getByTestId('stats-cards')).toBeInTheDocument()
  })

  it('data-testid="current-gate-panel"이 렌더링된다', () => {
    // impl gate는 GATE_META에 있으므로 CurrentGatePanel이 렌더링된다
    render(<StatsSectionUnderTest session={sessionWithStats} docs={mockDocs} />)
    expect(screen.getByTestId('current-gate-panel')).toBeInTheDocument()
  })

  it('StatsCards가 요구사항 현황 섹션을 표시한다', () => {
    render(<StatsSectionUnderTest session={sessionWithStats} docs={mockDocs} />)
    expect(screen.getByText('요구사항 현황')).toBeInTheDocument()
  })

  it('StatsCards가 테스트 현황 섹션을 표시한다', () => {
    render(<StatsSectionUnderTest session={sessionWithStats} docs={mockDocs} />)
    expect(screen.getByText('테스트 현황')).toBeInTheDocument()
  })
})
