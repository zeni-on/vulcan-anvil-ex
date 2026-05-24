'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertTriangle, CheckCircle2, FolderGit2, GitBranch, Loader2, RefreshCw, X, XCircle, type LucideIcon } from 'lucide-react'
import RunnerStatusPanel from '@/components/RunnerStatusPanel'
import { ProjectRuntime, RuntimeActivity, RuntimeActivityEvent, RuntimeWorktree } from '@/lib/types'

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

function compactWorktreePath(path?: string | null): string {
  if (!path) return ''
  const normalized = path.replace(/\\/g, '/')
  const parts = normalized.split('/').filter(Boolean)
  return parts[parts.length - 1] ?? normalized
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

function activityEvents(activity: RuntimeActivity): RuntimeActivityEvent[] {
  const events = activity.events ?? []
  if (events.length > 0) return events
  return [{
    at: activity.last_update,
    phase: activity.phase || activity.status,
    status: activity.status,
    message: activityTask(activity),
  }]
}

function activityKey(activity: RuntimeActivity): string {
  return `${activity.runner}-${activity.target_type ?? 'target'}-${activity.target_id}`
}

function eventTime(value?: string): string {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function ActivityRow({
  activity,
  onSelect,
}: {
  activity: RuntimeActivity
  onSelect: (activity: RuntimeActivity) => void
}) {
  const tone = activityTone(activity)
  const age = formatAge(activity.last_update_age_seconds)
  const targetType = activity.target_type === 'review' ? 'Review' : 'Run'
  const worktree = compactWorktreePath(activity.worktree_path)
  const title = [
    `${runnerLabel(activity.runner)} · ${targetType} ${activity.target_id}`,
    activity.current_task || activity.phase || activity.status,
    activity.current_message,
    age,
    activity.resume_supported ? 'resume 가능' : '',
  ].filter(Boolean).join('\n')

  return (
    <button
      type="button"
      onClick={() => onSelect(activity)}
      className="block w-full min-w-0 rounded-md border border-slate-800 bg-slate-900/45 px-2 py-1.5 text-left hover:border-cyan-700/70 hover:bg-slate-900/70"
      title={title}
      data-testid="agent-worker-line"
    >
      <div className="flex min-w-0 items-center gap-2">
        <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${tone.dotClassName}`} aria-hidden="true" />
        <span className="shrink-0 text-xs font-semibold text-slate-100">{runnerLabel(activity.runner)}</span>
        <span className="min-w-0 truncate text-[11px] text-slate-500">{activity.target_id}</span>
        {age && <span className="ml-auto shrink-0 text-[10px] text-slate-500">{age}</span>}
      </div>
      {worktree && (
        <p className="mt-1 truncate pl-4 text-[11px] leading-4 text-slate-500">
          worktree: {worktree}
        </p>
      )}
      <span className="sr-only">{tone.label}</span>
    </button>
  )
}

function ActivityDrawer({
  activity,
  onClose,
  onRefresh,
}: {
  activity: RuntimeActivity | null
  onClose: () => void
  onRefresh: () => void
}) {
  if (!activity) return null

  const tone = activityTone(activity)
  const targetType = activity.target_type === 'review' ? 'Review' : 'Run'
  const events = activityEvents(activity).slice(-100).reverse()
  const identity = activity.thread_id || activity.session_id || activity.resume_hint

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 p-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-label="worker activity detail">
      <div className="ml-auto flex h-full w-full max-w-xl flex-col rounded-lg border border-slate-700 bg-slate-950 shadow-2xl">
        <header className="border-b border-slate-800 px-4 py-3">
          <div className="flex items-start gap-3">
            <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${tone.dotClassName}`} aria-hidden="true" />
            <div className="min-w-0 flex-1">
              <div className="flex min-w-0 items-center gap-2">
                <h2 className="truncate text-sm font-semibold text-slate-100">
                  {runnerLabel(activity.runner)} · {targetType} {activity.target_id}
                </h2>
                <span className="shrink-0 rounded border border-slate-700 px-1.5 py-0.5 text-[10px] text-slate-400">
                  {activity.status}
                </span>
              </div>
              <p className="mt-1 line-clamp-2 text-xs leading-4 text-slate-400">
                {activityTask(activity)}
              </p>
            </div>
            <button
              type="button"
              onClick={onRefresh}
              className="rounded-md border border-slate-700 p-1 text-slate-400 hover:border-cyan-700 hover:text-cyan-100"
              aria-label="worker 상태 새로고침"
              title="worker 상태 새로고침"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-slate-700 p-1 text-slate-400 hover:border-slate-500 hover:text-slate-100"
              aria-label="닫기"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </header>

        <div className="grid gap-2 border-b border-slate-800 px-4 py-3 text-[11px] text-slate-400">
          <div className="grid grid-cols-[80px_1fr] gap-2">
            <span className="text-slate-600">target</span>
            <span className="truncate">{activity.target_id}</span>
          </div>
          <div className="grid grid-cols-[80px_1fr] gap-2">
            <span className="text-slate-600">runner</span>
            <span className="truncate">{activity.runner}</span>
          </div>
          {identity && (
            <div className="grid grid-cols-[80px_1fr] gap-2">
              <span className="text-slate-600">session</span>
              <span className="truncate">{identity}</span>
            </div>
          )}
          {activity.log && (
            <div className="grid grid-cols-[80px_1fr] gap-2">
              <span className="text-slate-600">log</span>
              <span className="truncate">{activity.log}</span>
            </div>
          )}
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
          <ol className="space-y-2">
            {events.map((event, index) => (
              <li key={`${event.at ?? 'event'}-${index}`} className="rounded-md border border-slate-800 bg-slate-900/45 px-3 py-2">
                <div className="flex min-w-0 items-center gap-2 text-[11px]">
                  <span className="shrink-0 text-slate-500">{eventTime(event.at)}</span>
                  {event.phase && (
                    <span className="min-w-0 truncate rounded border border-slate-700 px-1.5 py-0.5 text-[10px] text-slate-400">
                      {event.phase}
                    </span>
                  )}
                  {event.status && (
                    <span className="ml-auto shrink-0 text-[10px] text-slate-500">{event.status}</span>
                  )}
                </div>
                <p className="mt-1 whitespace-pre-wrap text-xs leading-4 text-slate-200">
                  {event.message || event.phase || event.status || 'worker activity'}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
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
              <span
                className="shrink-0 rounded border border-cyan-500/30 bg-cyan-500/10 px-1.5 py-0.5 text-[10px] text-cyan-200"
                title={worktree.changed_files.join('\n')}
              >
                변경 {worktree.changed_count}
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

function WorkspaceSummary({ runtime }: { runtime: ProjectRuntime | null }) {
  const branch = runtime?.current_branch
  const workflow = runtime?.workflow
  if (!branch && !workflow) return null

  const main = workflow?.main_branch ?? 'main'
  const integration = workflow?.integration_branch ?? 'dev'
  const role = branch === main ? 'baseline' : branch === integration ? 'integration' : 'worktree'
  const qaEnabled = workflow?.qa_worktree_enabled

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/35 px-3 py-2.5">
      <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
        작업공간
      </h3>
      <div className="space-y-1.5 text-xs">
        <div className="flex min-w-0 items-center justify-between gap-2 rounded-md border border-slate-800 bg-slate-900/60 px-2 py-1.5">
          <span className="inline-flex min-w-0 items-center gap-1.5 text-slate-400">
            <GitBranch className="h-3.5 w-3.5 flex-none text-cyan-300" aria-hidden="true" />
            <span className="truncate">{branch ?? 'branch unknown'}</span>
          </span>
          <span className="rounded border border-slate-700 px-1.5 py-0.5 text-[10px] text-slate-300">
            {role}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-1.5 text-[11px] text-slate-500">
          <span className="truncate">main: {main}</span>
          <span className="truncate">dev: {integration}</span>
          <span className="truncate">workflow: {workflow?.branch_mode ?? 'single'}</span>
          <span className="truncate">QA worktree: {qaEnabled ? 'on' : 'off'}</span>
        </div>
      </div>
    </section>
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
  const router = useRouter()
  const [selectedActivityKey, setSelectedActivityKey] = useState<string | null>(null)
  const activities = runtime?.active_executions ?? []
  const worktrees = runtime?.worktrees ?? []
  const selectedActivity = selectedActivityKey
    ? activities.find((activity) => activityKey(activity) === selectedActivityKey) ?? null
    : null
  const visibleActivities = activities
    .filter((activity) => ['running', 'stale', 'completed_no_result_change', 'failed', 'timeout', 'failed_empty_output'].includes(activity.status))
    .slice(0, 4)

  return (
    <div className="space-y-4" data-testid="agent-panel">
      <WorkspaceSummary runtime={runtime} />
      <RunnerStatusPanel runtime={runtime} isLoading={isLoading} error={error} onActivitySelect={(activity) => setSelectedActivityKey(activityKey(activity))} />
      <ActivityDrawer activity={selectedActivity} onClose={() => setSelectedActivityKey(null)} onRefresh={() => router.refresh()} />

      <section className="rounded-lg border border-slate-700 bg-slate-950/35 px-3 py-2.5">
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-slate-400">
          진행 작업
        </h3>
        {visibleActivities.length === 0 ? (
          <p className="text-xs text-slate-500">실행 중인 worker가 없습니다.</p>
        ) : (
          <ul className="space-y-1.5">
            {visibleActivities.map((activity) => (
              <li key={activityKey(activity)}>
                <ActivityRow activity={activity} onSelect={(selected) => setSelectedActivityKey(activityKey(selected))} />
              </li>
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
