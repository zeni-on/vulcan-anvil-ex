'use client'

import { AlertTriangle, CheckCircle2, FolderGit2, GitBranch, Loader2, XCircle, type LucideIcon } from 'lucide-react'
import RunnerStatusPanel from '@/components/RunnerStatusPanel'
import { ProjectRuntime, RuntimeWorktree } from '@/lib/types'

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
  const visibleActivities = activities.filter((activity) => activity.status === 'running').slice(0, 4)

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
              <li
                key={`${activity.runner}-${activity.target_id}`}
                className="flex min-w-0 items-center gap-2 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-1.5"
              >
                <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-emerald-200" />
                <div className="min-w-0 flex-1">
                  <div className="truncate text-xs font-semibold text-slate-100">
                    {activity.target_type === 'review' ? 'Review' : 'Run'} {activity.target_id}
                  </div>
                  <div className="truncate text-[11px] text-slate-500">{activity.runner}</div>
                </div>
                <span className="shrink-0 rounded border border-emerald-500/40 bg-emerald-500/10 px-1.5 py-0.5 text-[10px] text-emerald-200">
                  running
                </span>
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
