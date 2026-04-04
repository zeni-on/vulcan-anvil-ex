'use client'

/**
 * @file components/DocDrawer.tsx
 * @description 선택된 .md 파일을 오른쪽 슬라이드 패널에서 렌더링하는 Drawer (REQ-010)
 *
 * - 오른쪽에서 슬라이드인 애니메이션 (REQ-010-02)
 * - ESC 키, X 버튼, 배경 클릭으로 닫기 (REQ-010-04)
 * - react-markdown + remark-gfm + rehype-sanitize로 Markdown 렌더링 (REQ-010-03)
 *
 * @see docs/02-design/req-010-design.md §DocDrawer 컴포넌트
 * @see docs/02-design/ui-design.md §DocDrawer (REQ-010)
 */

import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import { X, AlertCircle } from 'lucide-react'
import { DocNode } from '@/lib/types'
import { useDocContent } from '@/hooks/useDocContent'

interface DocDrawerProps {
  projectId: string
  doc: DocNode | null
  onClose: () => void
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-3 p-6" aria-busy="true" aria-label="문서 불러오는 중">
      <div className="h-6 bg-zinc-700 rounded w-3/4" />
      <div className="h-4 bg-zinc-700 rounded w-full" />
      <div className="h-4 bg-zinc-700 rounded w-5/6" />
      <div className="h-4 bg-zinc-700 rounded w-4/5" />
      <div className="mt-4 h-4 bg-zinc-700 rounded w-full" />
      <div className="h-4 bg-zinc-700 rounded w-3/4" />
    </div>
  )
}

function DrawerContent({ projectId, doc }: { projectId: string; doc: DocNode }) {
  const { content, isLoading, error } = useDocContent(projectId, doc)

  if (isLoading) return <LoadingSkeleton />

  if (error) {
    return (
      <div
        role="alert"
        className="m-6 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400"
      >
        <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
        문서를 불러올 수 없습니다.
      </div>
    )
  }

  return (
    <div className="p-6 overflow-y-auto flex-1">
      <div className="prose prose-invert prose-sm max-w-none
        prose-headings:text-zinc-100
        prose-p:text-zinc-300
        prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
        prose-code:bg-zinc-800 prose-code:text-zinc-200 prose-code:px-1 prose-code:rounded prose-code:text-xs
        prose-pre:bg-zinc-800 prose-pre:border prose-pre:border-zinc-700
        prose-blockquote:border-zinc-600 prose-blockquote:text-zinc-400
        prose-th:text-zinc-200 prose-td:text-zinc-300
        prose-hr:border-zinc-700
        prose-strong:text-zinc-200
        prose-li:text-zinc-300
        prose-table:w-full prose-table:table-auto
        prose-th:break-words prose-td:break-words prose-td:align-top
        [&_table]:w-full [&_table]:border-collapse
        [&_td]:py-1.5 [&_td]:px-2 [&_td]:border [&_td]:border-zinc-700 [&_td]:text-xs [&_td]:align-top [&_td]:break-words
        [&_th]:py-1.5 [&_th]:px-2 [&_th]:border [&_th]:border-zinc-700 [&_th]:text-xs [&_th]:bg-zinc-800">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize]}
        >
          {content ?? ''}
        </ReactMarkdown>
      </div>
    </div>
  )
}

/**
 * 슬라이드 사이드 패널 Drawer.
 * doc이 null이면 화면 밖으로 숨겨진다 (translate-x-full).
 */
export default function DocDrawer({ projectId, doc, onClose }: DocDrawerProps) {
  const closeBtnRef = useRef<HTMLButtonElement>(null)
  const isOpen = doc !== null

  // ESC 키 닫기
  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Drawer 열릴 때 X 버튼에 포커스
  useEffect(() => {
    if (isOpen) closeBtnRef.current?.focus()
  }, [isOpen])

  return (
    <>
      {/* 배경 오버레이 */}
      <div
        className={`fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* 사이드 패널 */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label={doc?.name ?? '문서 뷰어'}
        className={`fixed right-0 top-0 h-full w-[60vw] max-w-none min-w-[480px] z-50 flex flex-col
          bg-zinc-900 border-l border-zinc-700
          transition-transform duration-300 ease-out
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-700 bg-zinc-800 flex-shrink-0">
          <h2 className="text-sm font-semibold text-zinc-100 truncate pr-4 font-mono">
            {doc?.name ?? ''}
          </h2>
          <button
            ref={closeBtnRef}
            onClick={onClose}
            aria-label="닫기"
            className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-700 transition-colors flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        {/* 콘텐츠 */}
        {doc && <DrawerContent projectId={projectId} doc={doc} />}
      </div>
    </>
  )
}
