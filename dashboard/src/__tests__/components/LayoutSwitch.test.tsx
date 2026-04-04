/**
 * @file __tests__/components/LayoutSwitch.test.tsx
 * @description page.tsx의 레이아웃 조건부 전환 로직 테스트 (REQ-012)
 *
 * 커버 항목:
 * - UT-012-17: template='A'일 때 LayoutA가 렌더링되고 LayoutB는 렌더링되지 않음
 * - UT-012-18: template='B'일 때 LayoutB가 렌더링되고 LayoutA는 렌더링되지 않음
 *
 * 구현 전략:
 * page.tsx는 useParams, SWR 훅 등 복잡한 의존성을 포함하므로,
 * 레이아웃 조건부 렌더링 로직을 동일 패턴으로 재현한 테스트용 컴포넌트를 사용한다.
 * LayoutA, LayoutB의 data-testid로 렌더링 여부를 검증한다.
 *
 * @see docs/02-design/req-012-design.md §page.tsx 변경
 */

import React, { useState } from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import LayoutA from '@/components/LayoutA'
import LayoutB from '@/components/LayoutB'
import LayoutToggle from '@/components/LayoutToggle'
import { LayoutTemplate } from '@/hooks/useLayoutTemplate'
import { SessionData, DocEntry, CommitEntry } from '@/lib/types'

// ── 공통 픽스처 ──────────────────────────────────────────────────────────────

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

const mockDocs: DocEntry[] = []
const mockCommits: CommitEntry[] = []

const layoutProps = {
  session: baseSession,
  sessionLoading: false,
  sessionError: null,
  docs: mockDocs,
  docsLoading: false,
  docsError: null,
  commits: mockCommits,
  commitsLoading: false,
  commitsError: null,
  onDocSelect: () => {},
}

// ── page.tsx의 레이아웃 조건부 렌더링 로직을 재현한 테스트용 컴포넌트 ──────────

/**
 * page.tsx의 레이아웃 전환 조건부 렌더링 패턴을 재현한 컴포넌트.
 * template 값에 따라 LayoutA 또는 LayoutB를 렌더링한다.
 */
function LayoutSwitchUnderTest({ initialTemplate }: { initialTemplate: LayoutTemplate }) {
  const [template, setTemplate] = useState<LayoutTemplate>(initialTemplate)

  function toggle() {
    setTemplate(prev => prev === 'A' ? 'B' : 'A')
  }

  return (
    <div>
      <LayoutToggle template={template} onToggle={toggle} />
      {template === 'A' ? (
        <LayoutA {...layoutProps} />
      ) : (
        <LayoutB {...layoutProps} />
      )}
    </div>
  )
}

// ── UT-012-17 ─────────────────────────────────────────────────────────────────

describe('UT-012-17: template=A일 때 LayoutA 렌더링, LayoutB 미렌더링', () => {
  it('template=A이면 data-testid="layout-a"가 렌더링된다', () => {
    render(<LayoutSwitchUnderTest initialTemplate="A" />)
    expect(screen.getByTestId('layout-a')).toBeInTheDocument()
  })

  it('template=A이면 data-testid="layout-b"가 렌더링되지 않는다', () => {
    render(<LayoutSwitchUnderTest initialTemplate="A" />)
    expect(screen.queryByTestId('layout-b')).not.toBeInTheDocument()
  })
})

// ── UT-012-18 ─────────────────────────────────────────────────────────────────

describe('UT-012-18: template=B일 때 LayoutB 렌더링, LayoutA 미렌더링', () => {
  it('template=B이면 data-testid="layout-b"가 렌더링된다', () => {
    render(<LayoutSwitchUnderTest initialTemplate="B" />)
    expect(screen.getByTestId('layout-b')).toBeInTheDocument()
  })

  it('template=B이면 data-testid="layout-a"가 렌더링되지 않는다', () => {
    render(<LayoutSwitchUnderTest initialTemplate="B" />)
    expect(screen.queryByTestId('layout-a')).not.toBeInTheDocument()
  })
})

// ── UT-012-19: LayoutToggle 클릭 후 레이아웃 즉시 전환 ────────────────────────

describe('UT-012-19: LayoutToggle 클릭 후 레이아웃 즉시 전환 (페이지 리로드 없음)', () => {
  it('A에서 LayoutToggle 클릭 후 layout-b가 렌더링된다 (페이지 리로드 없음)', () => {
    render(<LayoutSwitchUnderTest initialTemplate="A" />)

    // 초기 상태: LayoutA 렌더링
    expect(screen.getByTestId('layout-a')).toBeInTheDocument()

    // LayoutToggle 클릭
    fireEvent.click(screen.getByTestId('layout-toggle'))

    // 전환 후: LayoutB 렌더링, LayoutA 미렌더링
    expect(screen.getByTestId('layout-b')).toBeInTheDocument()
    expect(screen.queryByTestId('layout-a')).not.toBeInTheDocument()
  })

  it('B에서 LayoutToggle 클릭 후 layout-a가 렌더링된다 (페이지 리로드 없음)', () => {
    render(<LayoutSwitchUnderTest initialTemplate="B" />)

    // 초기 상태: LayoutB 렌더링
    expect(screen.getByTestId('layout-b')).toBeInTheDocument()

    // LayoutToggle 클릭
    fireEvent.click(screen.getByTestId('layout-toggle'))

    // 전환 후: LayoutA 렌더링, LayoutB 미렌더링
    expect(screen.getByTestId('layout-a')).toBeInTheDocument()
    expect(screen.queryByTestId('layout-b')).not.toBeInTheDocument()
  })
})
