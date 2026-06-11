'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { CheckCircle2, MessageSquarePlus, RefreshCw } from 'lucide-react'
import {
  DOC_COMMENT_CATEGORIES,
  DOC_COMMENT_STATUSES,
  type DocComment,
  type DocCommentCategory,
  type DocCommentDraftAnchor,
  type DocCommentStatus,
  type DocCommentsResponse,
} from '@/lib/docCommentTypes'

const categoryLabels: Record<DocCommentCategory, string> = {
  note: '메모',
  question: '질문',
  'finding-candidate': 'FIND 후보',
  'cr-candidate': 'CR 후보',
  'issue-candidate': 'ISSUE 후보',
  typo: '오탈자',
}

const statusLabels: Record<DocCommentStatus, string> = {
  open: 'Open',
  closed: 'Closed',
}

const fetcher = async (url: string): Promise<DocCommentsResponse> => {
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to load comments')
  return res.json() as Promise<DocCommentsResponse>
}

interface DocCommentsPanelProps {
  projectId: string
  docPath: string
  selectedAnchor: DocCommentDraftAnchor | null
  onClearSelectedAnchor: () => void
}

function truncateLine(text: string): string {
  const normalized = text.trim() || '(빈 줄)'
  return normalized.length > 180 ? `${normalized.slice(0, 180)}...` : normalized
}

export default function DocCommentsPanel({
  projectId,
  docPath,
  selectedAnchor,
  onClearSelectedAnchor,
}: DocCommentsPanelProps) {
  const commentsUrl = `/api/projects/${encodeURIComponent(projectId)}/comments?document=${encodeURIComponent(docPath)}`
  const { data, error, isLoading, mutate } = useSWR(commentsUrl, fetcher)
  const comments = data?.comments ?? []
  const [category, setCategory] = useState<DocCommentCategory>('note')
  const [body, setBody] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const openCount = comments.filter((comment) => comment.status === 'open').length

  async function createComment() {
    if (!selectedAnchor || !body.trim()) return
    setIsSaving(true)
    try {
      const res = await fetch(`/api/projects/${encodeURIComponent(projectId)}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document: docPath,
          start_line: selectedAnchor.start_line,
          end_line: selectedAnchor.end_line,
          selected_text: selectedAnchor.selected_text,
          heading: selectedAnchor.heading,
          category,
          body,
        }),
      })
      if (!res.ok) throw new Error('Failed to create comment')
      setBody('')
      onClearSelectedAnchor()
      await mutate()
    } finally {
      setIsSaving(false)
    }
  }

  async function updateStatus(comment: DocComment, status: DocCommentStatus) {
    const res = await fetch(`/api/projects/${encodeURIComponent(projectId)}/comments`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment_id: comment.comment_id, status }),
    })
    if (res.ok) await mutate()
  }

  return (
    <aside className="sticky top-0 max-h-[calc(100vh-6.5rem)] self-start overflow-y-auto rounded-md border border-slate-200 bg-white p-3 text-slate-800 shadow-sm">
      <header className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-1.5 text-sm font-semibold text-slate-950">
            <MessageSquarePlus className="h-4 w-4 text-blue-600" aria-hidden="true" />
            문서 코멘트
          </div>
          <p className="mt-0.5 text-xs text-slate-500">
            {comments.length}개 / Open {openCount}개
          </p>
        </div>
        <button
          type="button"
          onClick={() => void mutate()}
          className="rounded border border-slate-200 p-1 text-slate-500 hover:bg-slate-50 hover:text-slate-900"
          title="코멘트 새로고침"
          aria-label="코멘트 새로고침"
        >
          <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
        </button>
      </header>

      <section className="mt-3 space-y-2">
        <div className="rounded border border-slate-200 bg-slate-50 px-2 py-2 text-xs text-slate-600">
          {selectedAnchor ? (
            <>
              <div>
                대상:{' '}
                <span className="font-mono font-semibold text-slate-900">
                  L{selectedAnchor.start_line}
                  {selectedAnchor.end_line !== selectedAnchor.start_line ? `-${selectedAnchor.end_line}` : ''}
                </span>
              </div>
              {selectedAnchor.heading && (
                <div className="mt-1 truncate text-slate-500">{selectedAnchor.heading}</div>
              )}
              <blockquote className="mt-2 border-l-2 border-slate-300 pl-2 font-mono text-[11px] text-slate-500">
                {truncateLine(selectedAnchor.selected_text)}
              </blockquote>
            </>
          ) : (
            '본문의 + 버튼을 눌러 코멘트를 달 위치를 선택하세요.'
          )}
        </div>
        <select
          value={category}
          onChange={(event) => setCategory(event.target.value as DocCommentCategory)}
          className="w-full rounded border border-slate-300 bg-white px-2 py-1.5 text-xs text-slate-800"
        >
          {DOC_COMMENT_CATEGORIES.map((item) => (
            <option key={item} value={item}>
              {categoryLabels[item]}
            </option>
          ))}
        </select>
        <textarea
          value={body}
          onChange={(event) => setBody(event.target.value)}
          placeholder="코멘트를 입력하세요"
          rows={4}
          className="w-full resize-y rounded border border-slate-300 px-2 py-1.5 text-xs text-slate-800 placeholder:text-slate-400"
        />
        <button
          type="button"
          onClick={() => void createComment()}
          disabled={!selectedAnchor || !body.trim() || isSaving}
          className="inline-flex w-full items-center justify-center gap-1.5 rounded bg-blue-600 px-2 py-1.5 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
          저장
        </button>
        {error && <p className="text-xs text-red-600">코멘트를 불러오지 못했습니다.</p>}
      </section>

      <section className="mt-4 space-y-2">
        <div className="text-xs font-semibold text-slate-700">
          기존 코멘트 {isLoading ? '(불러오는 중)' : ''}
        </div>
        {comments.length === 0 ? (
          <p className="rounded border border-dashed border-slate-300 px-2 py-3 text-xs text-slate-500">
            아직 코멘트가 없습니다.
          </p>
        ) : (
          comments.map((comment) => (
            <article key={comment.comment_id} className="rounded border border-slate-200 p-2 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono font-semibold text-slate-700">
                  L{comment.anchor.start_line}
                  {comment.anchor.end_line !== comment.anchor.start_line ? `-${comment.anchor.end_line}` : ''}
                </span>
                <select
                  value={comment.status}
                  onChange={(event) => void updateStatus(comment, event.target.value as DocCommentStatus)}
                  className="rounded border border-slate-200 bg-white px-1 py-0.5 text-[11px] text-slate-700"
                >
                  {DOC_COMMENT_STATUSES.map((status) => (
                    <option key={status} value={status}>
                      {statusLabels[status]}
                    </option>
                  ))}
                </select>
              </div>
              <div className="mt-1 inline-flex rounded bg-slate-100 px-1.5 py-0.5 text-[11px] font-medium text-slate-700">
                {categoryLabels[comment.category]}
              </div>
              <p className="mt-2 whitespace-pre-wrap text-slate-800">{comment.body}</p>
              {comment.anchor.selected_text && (
                <blockquote className="mt-2 border-l-2 border-slate-300 pl-2 font-mono text-[11px] text-slate-500">
                  {truncateLine(comment.anchor.selected_text)}
                </blockquote>
              )}
            </article>
          ))
        )}
      </section>
    </aside>
  )
}
