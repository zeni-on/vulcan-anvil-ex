import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import QaWorkspaceNotice from '@/components/QaWorkspaceNotice'
import type { SessionData } from '@/lib/types'

const baseSession: SessionData = {
  project: 'QA Blocked Project',
  vulcan_version: '0.4.8',
  current_gate: 'gate4',
  gate_status: {
    gate1: 'done',
    gate2: 'done',
    gate3: 'done',
    impl: 'done',
    gate4: 'in-progress',
    gate5: 'pending',
  },
  started: '2026-06-25',
  completed: [],
  pending: [],
  blocked: [],
}

describe('QaWorkspaceNotice', () => {
  it('environment_blocked QA workspace에 후속 조치 안내를 표시한다', () => {
    render(
      <QaWorkspaceNotice
        session={{
          ...baseSession,
          qa_execution: {
            gate4_workspace: {
              path: 'C:\\Users\\user\\Documents\\antig-workspace\\sample\\.vulcan\\worktrees\\QA-GATE4',
              status: 'environment_blocked',
              last_stage: 'QA-000',
            },
          },
        }}
      />,
    )

    expect(screen.getByTestId('qa-workspace-blocked-notice')).toBeInTheDocument()
    expect(screen.getByText('QA 환경 차단')).toBeInTheDocument()
    expect(screen.getByText('environment_blocked')).toBeInTheDocument()
    expect(screen.getByText(/doctor JSON/)).toBeInTheDocument()
    expect(screen.getByText(/ISSUE\/environment_blocked/)).toBeInTheDocument()
    expect(screen.getByText(/qa-fix-loop/)).toBeInTheDocument()
  })

  it('active QA workspace에는 표시하지 않는다', () => {
    const { container } = render(
      <QaWorkspaceNotice
        session={{
          ...baseSession,
          qa_execution: {
            gate4_workspace: {
              path: 'C:\\workspace\\QA-GATE4',
              status: 'active',
            },
          },
        }}
      />,
    )

    expect(container).toBeEmptyDOMElement()
  })
})
