import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import AgentPanel from '@/components/AgentPanel'
import { ProjectRuntime } from '@/lib/types'

const runtime: ProjectRuntime = {
  primary: 'codex-cli',
  available_runners: [
    { name: 'codex-cli', model: 'gpt-5.5', effort: 'high' },
  ],
  capabilities: {
    same_runner_independent_review: true,
    cross_model_validation: false,
    parallel_cross_runner_work: false,
  },
  active_executions: [
    {
      target_type: 'review',
      target_id: 'RV-001',
      runner: 'codex-cli',
      status: 'running',
      phase: 'reviewing',
      current_task: 'Gate2 설계 검토 중',
      current_message: '프로그램 계약과 API 정의를 비교 중',
      last_update_age_seconds: 15,
      thread_id: '019e-test-thread',
      log: 'docs/runs/_exec/RV-001_codex-exec.jsonl',
      events: [
        {
          at: '2026-05-22T19:20:00',
          phase: 'started',
          status: 'running',
          message: 'RV-001 독립 검수 시작',
        },
        {
          at: '2026-05-22T19:21:00',
          phase: 'reviewing',
          status: 'running',
          message: '프로그램 계약과 API 정의를 비교 중',
        },
      ],
    },
  ],
  worktrees: [],
}

describe('AgentPanel worker activity drawer', () => {
  it('진행 중 worker 클릭 시 최근 이벤트 레이어를 표시한다', () => {
    render(<AgentPanel runtime={runtime} />)

    fireEvent.click(screen.getByTestId('agent-worker-line'))

    expect(screen.getByRole('dialog', { name: 'worker activity detail' })).toBeInTheDocument()
    expect(screen.getByText('Codex · Review RV-001')).toBeInTheDocument()
    expect(screen.getByText('RV-001 독립 검수 시작')).toBeInTheDocument()
    expect(screen.getAllByText('프로그램 계약과 API 정의를 비교 중').length).toBeGreaterThan(0)
    expect(screen.getByText('019e-test-thread')).toBeInTheDocument()
  })
})
