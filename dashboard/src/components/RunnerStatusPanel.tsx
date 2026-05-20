'use client'

import { AlertCircle, CheckCircle2, Cpu, GitBranch } from 'lucide-react'
import { ProjectRuntime, RuntimeRunner } from '@/lib/types'

function runnerLabel(runner: RuntimeRunner): string {
  return runner.name.replace(/-cli$/, '')
}

function runnerDetail(runner: RuntimeRunner): string {
  const effort = runner.effort ?? runner.reasoning_effort
  return [runner.model, effort].filter(Boolean).join(' / ') || runner.version || '설정값 없음'
}

function capabilityLabel(runtime: ProjectRuntime): { label: string; tone: 'green' | 'yellow' | 'gray' } {
  if (runtime.capabilities.cross_model_validation) {
    return { label: '교차검증 가능', tone: 'green' }
  }
  if (runtime.capabilities.same_runner_independent_review) {
    return { label: '독립실행 가능', tone: 'yellow' }
  }
  return { label: '수동 실행', tone: 'gray' }
}

export default function RunnerStatusPanel({
  runtime,
  isLoading,
  error,
  compact = false,
}: {
  runtime: ProjectRuntime | null
  isLoading?: boolean
  error?: unknown
  compact?: boolean
}) {
  if (isLoading) {
    return (
      <section className="rounded-lg border border-slate-700 bg-slate-950/35 px-3 py-2.5" data-testid="runner-status">
        <div className="h-4 w-28 animate-pulse rounded bg-slate-700/70" />
        <div className="mt-3 h-3 w-full animate-pulse rounded bg-slate-800" />
      </section>
    )
  }

  if (error) {
    return (
      <section className="rounded-lg border border-rose-900/60 bg-rose-950/20 px-3 py-2.5" data-testid="runner-status">
        <div className="flex items-center gap-2 text-xs font-semibold text-rose-200">
          <AlertCircle className="h-3.5 w-3.5" />
          Runner 설정 조회 실패
        </div>
      </section>
    )
  }

  const runners = runtime?.available_runners ?? []
  const capability = runtime ? capabilityLabel(runtime) : { label: '설정 없음', tone: 'gray' as const }
  const badgeClass = {
    green: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
    yellow: 'border-amber-500/40 bg-amber-500/10 text-amber-200',
    gray: 'border-slate-600 bg-slate-800/60 text-slate-300',
  }[capability.tone]

  return (
    <section
      className="rounded-lg border border-slate-700 bg-slate-950/35 px-3 py-2.5"
      data-testid="runner-status"
    >
      <div className="mb-2 flex items-center justify-between gap-2">
        <h3 className="flex min-w-0 items-center gap-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          <Cpu className="h-3.5 w-3.5 shrink-0 text-cyan-300" />
          <span className="truncate">Runner</span>
        </h3>
        <span className={`shrink-0 rounded-md border px-2 py-0.5 text-[11px] font-medium ${badgeClass}`}>
          {capability.label}
        </span>
      </div>

      {runners.length === 0 ? (
        <p className="text-xs text-slate-500">vulcan.config.json의 runtime 설정이 없습니다.</p>
      ) : (
        <ul className={compact ? 'space-y-1.5' : 'grid gap-1.5'}>
          {runners.map((runner) => (
            <li
              key={runner.name}
              className="flex min-w-0 items-center gap-2 rounded-md border border-slate-800 bg-slate-900/45 px-2 py-1.5"
            >
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-300" />
              <div className="min-w-0 flex-1">
                <div className="truncate text-xs font-semibold text-slate-100">
                  {runnerLabel(runner)}
                </div>
                <div className="truncate text-[11px] text-slate-500">
                  {runnerDetail(runner)}
                </div>
              </div>
              {runner.name === runtime?.primary && (
                <span className="shrink-0 rounded border border-cyan-500/40 bg-cyan-500/10 px-1.5 py-0.5 text-[10px] text-cyan-200">
                  primary
                </span>
              )}
            </li>
          ))}
        </ul>
      )}

      {!compact && runtime?.capabilities.parallel_cross_runner_work && (
        <div className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-500">
          <GitBranch className="h-3.5 w-3.5 text-slate-500" />
          Build Wave 분리와 PR 교차검증 후보로 사용할 수 있습니다.
        </div>
      )}
    </section>
  )
}
