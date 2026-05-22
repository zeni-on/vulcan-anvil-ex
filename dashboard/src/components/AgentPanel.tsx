'use client'

import { AlertTriangle, CheckCircle2, FolderGit2, GitBranch, Loader2, XCircle, type LucideIcon } from 'lucide-react'
import RunnerStatusPanel from '@/components/RunnerStatusPanel'
import { ProjectRuntime, RuntimeActivity, RuntimeWorktree } from '@/lib/types'

function worktreeTone(status: string): {
  label: string
  className: string
  Icon: LucideIcon
  spin?: boolean
} {
  if (status === 'running') {
    return {
      label: 'running',
      className: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
      Icon: Loader2,
      spin: true,
    }
  }
  if (status === 'stale' || status === 'missing') {
    return {
      label: status === 'stale' ? 'stale' : 'missing',
      className: 'border-amber-500/40 bg-amber-500/10 text-amber-200',
      Icon: AlertTriangle,
    }
  }
  if (status === 'failed' || status === 'timeout' || status === 'failed_empty_output') {
    return {
      label: status === 'failed_empty_output' ? 'empty' : status,
      className: 'border-rose-500/40 bg-rose-500/10 text-rose-200',
      Icon: XCircle,
    }
  }
  if (status === 'review_needed') {
    return {
      label: 'review',
      className: 'border-cyan-500/40 bg-cyan-500/10 text-cyan-200',
      Icon: GitBranch,
    }
  }
  return {
    label: status === 'completed_no_result_change' ? 'no result' : status === 'clean' ? 'clean' : status,
    className: 'border-slate-600 bg-slate-800/60 text-slate-300',
    Icon: CheckCircle2,
  }
}

function targetLabel(worktree: RuntimeWorktree): string {
  if (!worktree.target_id) return worktree.id
  return worktree.target_id
}

function runnerLabel(name: string): string {
  if (name === 'codex-cli' || name === 'codex') return 'Codex'
  if (name === 'claude-cli' || name === 'claude') return 'Claude'
  if (name === 'antigravity-cli' || name === 'antigravity' || name === 'agy') return 'Gemini'
  return name.replace(/-cli$/, '')
}

function formatAge(seconds?: number): string {
  if (seconds === undefined || !Number.isFinite(seconds)) return ''
  if (seconds < 60) return '방금 전'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}분 전`
  return `${Math.floor(minutes / 60)}시간 전`
}

function activityTone(activity: RuntimeActivity): {
  dotClassName: string
  label: string
} {
  if (activity.status === 'running') {
    return { dotClassName: 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.7)]', label: 'running' }
  }
  if (activity.status === 'stale' || activity.status === 'completed_no_result_change') {
    return { dotClassName: 'bg-amber-300 shadow-[0_0_10px_rgba(252,211,77,0.55)]', label: activity.status === 'stale' ? 'stale' : 'no result' }
  }
  if (activity.status === 'failed' || activity.status === 'timeout' || activity.status === 'failed_empty_output') {
    return { dotClassName: 'bg-rose-400 shadow-[0_0_10px_rgba(251,113,133,0.65)]', label: activity.status }
  }
  return { dotClassName: 'bg-slate-500', label: activity.status }
}

function activityTask(activity: RuntimeActivity): string {
  if (activity.current_message) return activity.current_message
  if (activity.current_task) return activity.current_task
  if (activity.status === 'running') return '작업 진행 중'
  if (activity.result_file_changed === false || activity.run_file_changed === false) return '결과 파일 미갱신'
  return activity.phase || activity.status
}

function ActivityRow({ activity }: { activity: RuntimeActivity }) {
  const tone = activityTone(activity)
  const age = formatAge(activity.last_update_age_seconds)
  const targetType = activity.target_type === 'review' ? 'Review' : 'Run'
  const title = [
    `${runnerLabel(activity.runner)} · ${targetType} ${activity.target_id}`,
    activity.current_task || activity.phase || activity.status,
    activity.current_message,
    age,
    activity.resume_supported ? 'resume 가능' : '',
  ].filter(Boolean).join('\n')

  return (
    <li
      className="min-w-0 rounded-md border border-slate-800 bg-slate-900/45 px-2 py-1.5"
      title={title}
      data-testid="agent-worker-line"
    >
      <div className="flex min-w-0 items-center gap-2">
        <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${tone.dotClassName}`} aria-hidden="true" />
        <span className="shrink-0 text-xs font-semibold text-slate-100">{runnerLabel(activity.runner)}</span>
        <span className="min-w-0 truncate text-[11px] text-slate-500">{activity.target_id}</span>
        {age && <span className="ml-auto shrink-0 text-[10px] text-slate-500">{age}</span>}
      </div>
      <p className="mt-1 line-clamp-2 min-w-0 pl-4 text-xs leading-4 text-slate-300">
        {activityTask(activity)}
      </p>
      {activity.current_message && activity.current_task && (
        <p className="mt-0.5 line-clamp-1 min-w-0 pl-4 text-[10px] leading-3 text-slate-500">
          {activity.current_task}
        </p>
      )}
      <span className="sr-only">{tone.label}</span>
    </li>
  )
}

function WorktreeRow({ worktree }: { worktree: RuntimeWorktree }) {
  const tone = worktreeTone(worktree.status)
  const StatusIcon = tone.Icon
  const tooltip = [
    worktree.path,
    worktree.branch ? `branch: ${worktree.branch}` : '',
    worktree.runner ? `runner: ${worktree.runner}` : '',
    worktree.changed_files.length > 0 ? `changed: ${worktree.changed_files.join(', ')}` : '',
  ].filter(Boolean).join('\n')

  return (
    <li
      className="rounded-md border border-slate-800 bg-slate-900/45 px-2 py-1.5"
      title={tooltip}
    >
      <div className="flex min-w-0 items-center gap-2">
        <FolderGit2 className="h-4 w-4 shrink-0 text-slate-400" />
        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-2">
            <span className="min-w-0 truncate text-xs font-semibold text-slate-100">
              {targetLabel(worktree)}
            </span>
            {worktree.changed_count > 0 && (
              <span className="shrink-0 rounded border border-cyan-500/30 bg-cyan-500/10 px-1.5 py-0.5 text-[10px] text-cyan-200">
                {worktree.changed_count}
              </span>
            )}
          </div>
          <div className="mt-0.5 flex min-w-0 items-center gap-1.5 text-[11px] text-slate-500">
            {worktree.runner && <span className="shrink-0">{worktree.runner}</span>}
            {worktree.branch && (
              <>
                <span className="shrink-0 text-slate-700">/</span>
                <span className="min-w-0 truncate">{worktree.branch.replace(/^codex\/run-/, '')}</span>
              </>
            )}
          </div>
        </div>
        <span className={`inline-flex shrink-0 items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] ${tone.className}`}>
          <StatusIcon className={`h-3 w-3 ${tone.spin ? 'animate-spin' : ''}`} />
          {tone.label}
        </span>
      </div>
    </li>
  )
}

export default function AgentPanel({
  runtime,
  isLoading,
  error,
}: {
  runtime: ProjectRuntime | null
  isLoading?: boolean
  error?: unknown
}) {
  const activities = runtime?.active_executions ?? []
  const worktrees = runtime?.worktrees ?? []
  const visibleActivities = activities
    .filter((activity) => ['running', 'stale', 'completed_no_result_change', 'failed', 'timeout', 'failed_empty_output'].includes(activity.status))
    .slice(0, 4)

  return (
    <div className="space-y-4" data-testid="agent-panel">
      <RunnerStatusPanel runtime={runtime} isLoading={isLoading} error={error} />

      <section className="rounded-lg border border-slate-700 bg-slate-950/35 px-3 py-2.5">
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          진행 작업
        </h3>
        {visibleActivities.length === 0 ? (
          <p className="text-xs text-slate-500">실행 중인 worker가 없습니다.</p>
        ) : (
          <ul className="space-y-1.5">
            {visibleActivities.map((activity) => (
              <ActivityRow key={`${activity.runner}-${activity.target_id}`} activity={activity} />
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-lg border border-slate-700 bg-slate-950/35 px-3 py-2.5">
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          Worktree
        </h3>
        {worktrees.length === 0 ? (
          <p className="text-xs text-slate-500">표시할 worktree가 없습니다.</p>
        ) : (
          <ul className="space-y-1.5">
            {worktrees.map((worktree) => (
              <WorktreeRow key={worktree.path} worktree={worktree} />
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
