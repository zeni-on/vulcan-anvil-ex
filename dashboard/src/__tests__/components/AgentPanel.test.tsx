import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import AgentPanel from '@/components/AgentPanel'
import { ProjectRuntime } from '@/lib/types'

const refreshMock = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    refresh: refreshMock,
  }),
}))

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
      model: 'gpt-5.5',
      reasoning_effort: 'high',
      model_source: 'codex-model-policy:review|compat-fallback:gpt-5.3-codex',
      model_fallback_reason: 'gpt-5.3-codex is not supported; using gpt-5.5',
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
  beforeEach(() => {
    refreshMock.mockClear()
  })

  it('진행 중 worker 클릭 시 최근 이벤트 레이어를 표시한다', () => {
    render(<AgentPanel runtime={runtime} />)

    fireEvent.click(screen.getByTestId('agent-worker-line'))

    expect(screen.getByRole('dialog', { name: 'worker activity detail' })).toBeInTheDocument()
    expect(screen.getByText('Codex · Review RV-001')).toBeInTheDocument()
    expect(screen.getByText('RV-001 독립 검수 시작')).toBeInTheDocument()
    expect(screen.getAllByText('프로그램 계약과 API 정의를 비교 중').length).toBeGreaterThan(0)
    expect(screen.getByText('019e-test-thread')).toBeInTheDocument()
    expect(screen.getAllByText('gpt-5.3-codex is not supported; using gpt-5.5').length).toBeGreaterThan(0)
  })

  it('레이어 새로고침 버튼으로 현재 worker 상태를 다시 요청한다', () => {
    render(<AgentPanel runtime={runtime} />)

    fireEvent.click(screen.getByTestId('agent-worker-line'))
    fireEvent.click(screen.getByRole('button', { name: 'worker 상태 새로고침' }))

    expect(refreshMock).toHaveBeenCalledTimes(1)
  })

  it('완료됐지만 결과 파일이 미갱신된 worker는 진행 작업 목록에서 숨긴다', () => {
    const completedRuntime: ProjectRuntime = {
      ...runtime,
      active_executions: [
        {
          target_type: 'run',
          target_id: 'RUN-016',
          runner: 'antigravity-cli',
          status: 'completed_no_result_change',
          phase: 'completed_no_result_change',
          current_task: 'RUN-016 worker 결과 작성 완료',
          completed_at: '2026-05-31T20:54:17',
          log: 'docs/runs/_exec/RUN-016_antigravity-exec.txt',
        },
      ],
    }

    render(<AgentPanel runtime={completedRuntime} />)

    expect(screen.queryByTestId('agent-worker-line')).not.toBeInTheDocument()
    expect(screen.getByText('실행 중인 worker가 없습니다.')).toBeInTheDocument()
  })

  it('Run 위임 기록이 있으면 실행 경로를 표시한다', () => {
    render(<AgentPanel runtime={{
      ...runtime,
      active_executions: [],
      delegations: [
        {
          run_id: 'RUN-014',
          run_file: 'docs/runs/RUN-014_build.md',
          mode: 'codex-subagent',
          delegate: 'build',
          task: 'Todo API 구현',
          status: 'completed',
          model: 'gpt-5.5',
          reasoning_effort: 'high',
          model_source: 'codex-model-policy:build|compat-fallback:gpt-5.3-codex',
          model_fallback_reason: 'gpt-5.3-codex is not supported; using gpt-5.5',
          source: 'delegation_records',
        },
      ],
    }} />)

    expect(screen.getByText('위임 기록')).toBeInTheDocument()
    expect(screen.getByText('RUN-014')).toBeInTheDocument()
    expect(screen.getByText('Codex subagent')).toBeInTheDocument()
    expect(screen.getByText('Todo API 구현')).toBeInTheDocument()
    expect(screen.getByText('worker 완료')).toBeInTheDocument()
    expect(screen.getAllByText('gpt-5.5 / high').length).toBeGreaterThan(0)
    expect(screen.getByText('fallback: gpt-5.3-codex is not supported; using gpt-5.5')).toBeInTheDocument()
  })

  it('위임 상태에서 worker 완료와 Orchestrator 검증 완료를 구분해 표시한다', () => {
    render(<AgentPanel runtime={{
      ...runtime,
      active_executions: [],
      delegations: [
        {
          run_id: 'RUN-014',
          sidecar_path: '.vulcan/delegations/RUN-014.json',
          mode: 'codex-thread',
          delegate: 'build',
          task: 'Todo API 구현',
          status: 'worker_completed',
          source: 'delegation_sidecar',
        },
        {
          run_id: 'RUN-015',
          sidecar_path: '.vulcan/delegations/RUN-015.json',
          mode: 'codex-thread',
          delegate: 'qa',
          task: 'QA 증적 확인',
          status: 'verified',
          verification_status: 'orchestrator verified',
          source: 'delegation_sidecar',
        },
      ],
    }} />)

    expect(screen.getByText('worker 완료')).toBeInTheDocument()
    expect(screen.getByText('검증 완료')).toBeInTheDocument()
    expect(screen.getByText('orchestrator verified')).toBeInTheDocument()
  })

  it('Run 위임 기록이 없어도 오류 대신 미기록 안내를 표시한다', () => {
    render(<AgentPanel runtime={{ ...runtime, active_executions: [], delegations: [] }} />)

    expect(screen.getByText('Run에 기록된 위임 경로가 없습니다. 짧은 PoC 작업에서는 정상일 수 있습니다.')).toBeInTheDocument()
  })
})
