import { AlertTriangle } from 'lucide-react'
import type { SessionData, QaWorkspaceState } from '@/lib/types'

const BLOCKED_QA_STATUSES = new Set(['blocked', 'failed', 'missing', 'environment_blocked'])

function getQaWorkspace(session: SessionData): QaWorkspaceState | null {
  return session.qa_execution?.gate4_workspace ?? session.qa_execution?.gate4_worktree ?? null
}

function shortPath(value?: string) {
  if (!value) return '-'
  if (value.length <= 52) return value
  return `...${value.slice(-49)}`
}

export default function QaWorkspaceNotice({ session }: { session: SessionData }) {
  const workspace = getQaWorkspace(session)
  const status = (workspace?.status ?? '').toLowerCase()

  if (!workspace || !BLOCKED_QA_STATUSES.has(status)) return null

  return (
    <section
      className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-100"
      data-testid="qa-workspace-blocked-notice"
      aria-label="QA workspace blocked notice"
    >
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-4 w-4 flex-none text-red-300" aria-hidden="true" />
        <div className="min-w-0 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold">QA 환경 차단</span>
            <span className="rounded border border-red-400/40 bg-red-500/10 px-1.5 py-0.5 text-[11px] font-mono text-red-100">
              {workspace.status}
            </span>
          </div>
          <p className="text-xs leading-5 text-red-100/85">
            QA-000의 doctor JSON과 evidence 로그를 확인하고, 제품 결함과 환경 차단을 분리하세요.
          </p>
          <ul className="space-y-1 text-xs leading-5 text-red-100/80">
            <li>환경 문제이면 ISSUE/environment_blocked로 보류</li>
            <li>제품 수정이 필요하면 승인 후 qa-fix-loop 생성</li>
          </ul>
          <div className="grid gap-1 text-[11px] text-red-100/65">
            <span title={workspace.path}>workspace: {shortPath(workspace.path)}</span>
            {workspace.last_stage && <span>last stage: {workspace.last_stage}</span>}
          </div>
        </div>
      </div>
    </section>
  )
}
