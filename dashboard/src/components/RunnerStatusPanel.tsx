'use client'

import { AlertCircle, Bot, Cpu, GitBranch, Loader2, Sparkles, type LucideIcon } from 'lucide-react'
import { ProjectRuntime, RuntimeActivity, RuntimeRunner } from '@/lib/types'

function runnerLabel(runner: RuntimeRunner): string {
  if (runner.name === 'codex-cli' || runner.name === 'codex') return 'Codex'
  if (runner.name === 'claude-cli' || runner.name === 'claude') return 'Claude'
  if (runner.name === 'antigravity-cli' || runner.name === 'antigravity' || runner.name === 'agy') return 'Gemini'
  return runner.name.replace(/-cli$/, '')
}

function runnerFamily(name: string): string {
  if (name === 'codex-cli' || name === 'codex') return 'codex'
  if (name === 'claude-cli' || name === 'claude') return 'claude'
  if (name === 'antigravity-cli' || name === 'antigravity' || name === 'agy') return 'gemini'
  return name.replace(/-cli$/, '')
}

function runnerVisual(runner: RuntimeRunner): {
  Icon: LucideIcon
  badgeClass: string
  iconClass: string
} {
  if (runner.name === 'codex-cli' || runner.name === 'codex') {
    return {
      Icon: Bot,
      badgeClass: 'border-cyan-500/35 bg-cyan-500/10',
      iconClass: 'text-cyan-200',
    }
  }
  if (runner.name === 'claude-cli' || runner.name === 'claude') {
    return {
      Icon: Sparkles,
      badgeClass: 'border-amber-500/35 bg-amber-500/10',
      iconClass: 'text-amber-200',
    }
  }
  if (runner.name === 'antigravity-cli' || runner.name === 'antigravity' || runner.name === 'agy') {
    return {
      Icon: Cpu,
      badgeClass: 'border-violet-500/35 bg-violet-500/10',
      iconClass: 'text-violet-200',
    }
  }
  return {
    Icon: Cpu,
    badgeClass: 'border-slate-600 bg-slate-800/70',
    iconClass: 'text-slate-300',
  }
}

function runnerDetail(runner: RuntimeRunner): string {
  const effort = runner.effort ?? runner.reasoning_effort
  return [runner.model, effort].filter(Boolean).join(' / ') || runner.version || '설정값 없음'
}

function activityLabel(activity: RuntimeActivity): string {
  const type = activity.target_type === 'review' ? 'Review' : 'Run'
  return `${type} ${activity.target_id}`
}

function activityDetail(activity: RuntimeActivity): string {
  const message = activity.current_message || activity.current_task || activity.phase || activity.status
  return [activityLabel(activity), message].filter(Boolean).join(' · ')
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
  onActivitySelect,
}: {
  runtime: ProjectRuntime | null
  isLoading?: boolean
  error?: unknown
  compact?: boolean
  onActivitySelect?: (activity: RuntimeActivity) => void
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
  const activities = runtime?.active_executions ?? []
  const runningActivities = activities.filter((activity) => activity.status === 'running')
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
          {runners.map((runner) => {
            const visual = runnerVisual(runner)
            const RunnerIcon = visual.Icon
            const runningActivity = runningActivities.find(
              (activity) => runnerFamily(activity.runner) === runnerFamily(runner.name),
            )
            const selectable = Boolean(runningActivity && onActivitySelect)

            return (
              <li
                key={runner.name}
                role={selectable ? 'button' : undefined}
                tabIndex={selectable ? 0 : undefined}
                onClick={selectable ? () => onActivitySelect?.(runningActivity!) : undefined}
                onKeyDown={selectable ? (event) => {
                  if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault()
                    onActivitySelect?.(runningActivity!)
                  }
                } : undefined}
                className={
                  runningActivity
                    ? `flex min-w-0 items-center gap-2 rounded-md border border-emerald-500/40 bg-emerald-500/10 px-2 py-1.5 shadow-[0_0_0_1px_rgba(16,185,129,0.08)] ${selectable ? 'cursor-pointer hover:border-emerald-300/60 hover:bg-emerald-500/15' : ''}`
                    : 'flex min-w-0 items-center gap-2 rounded-md border border-slate-800 bg-slate-900/45 px-2 py-1.5'
                }
              >
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md border ${visual.badgeClass}`}
                  title={`${runnerLabel(runner)} runner`}
                  aria-label={`${runnerLabel(runner)} runner`}
                >
                  {runningActivity ? (
                    <Loader2 className="h-4 w-4 animate-spin text-emerald-200" />
                  ) : (
                    <RunnerIcon className={`h-4 w-4 ${visual.iconClass}`} />
                  )}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-xs font-semibold text-slate-100">
                    {runnerLabel(runner)}
                  </div>
                  <div className={runningActivity ? 'line-clamp-2 text-[11px] leading-3 text-slate-400' : 'truncate text-[11px] text-slate-500'}>
                    {runningActivity ? activityDetail(runningActivity) : runnerDetail(runner)}
                  </div>
                </div>
                {runningActivity ? (
                  <span className="shrink-0 rounded border border-emerald-500/40 bg-emerald-500/10 px-1.5 py-0.5 text-[10px] text-emerald-200">
                    running
                  </span>
                ) : runner.name === runtime?.primary && (
                  <span className="shrink-0 rounded border border-cyan-500/40 bg-cyan-500/10 px-1.5 py-0.5 text-[10px] text-cyan-200">
                    primary
                  </span>
                )}
              </li>
            )
          })}
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
