'use client'

/**
 * @file DeleteProjectButton.tsx
 * @description 프로젝트 삭제 버튼 컴포넌트
 *
 * AlertDialog로 삭제 확인 → DELETE /api/projects/[id] 호출 → onSuccess 콜백 실행
 *
 * Props:
 * - projectId: string
 * - projectName: string
 * - onSuccess: () => void — SWR mutate 트리거
 *
 * @see docs/02-design/ui-design.md §DeleteProjectButton
 */

import { useState } from 'react'
import { Trash2, AlertTriangle, Loader2 } from 'lucide-react'

interface DeleteProjectButtonProps {
  projectId: string
  projectName: string
  onSuccess: () => void
}

/**
 * 삭제 확인 AlertDialog를 포함하는 삭제 버튼.
 * 확인 후 DELETE /api/projects/[id]를 호출하고 onSuccess 콜백을 실행한다.
 */
export default function DeleteProjectButton({
  projectId,
  projectName,
  onSuccess,
}: DeleteProjectButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async () => {
    setIsDeleting(true)
    setError(null)

    try {
      const res = await fetch(`/api/projects/${projectId}`, { method: 'DELETE' })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body?.error ?? `삭제 실패 (HTTP ${res.status})`)
      }
      setIsOpen(false)
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.')
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <>
      {/* 삭제 트리거 버튼 */}
      <button
        type="button"
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          setIsOpen(true)
        }}
        className={`
          p-1.5 rounded-md
          text-[#4B5563] hover:text-red-400 hover:bg-red-500/10
          opacity-0 group-hover:opacity-100
          transition-all duration-150
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500
          focus-visible:opacity-100
        `}
        aria-label={`${projectName} 삭제`}
        data-testid="delete-project-button"
      >
        <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
      </button>

      {/* AlertDialog 오버레이 */}
      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-dialog-title"
          aria-describedby="delete-dialog-desc"
          className="fixed inset-0 z-50 flex items-center justify-center"
          onClick={(e) => {
            e.preventDefault()
            e.stopPropagation()
          }}
        >
          {/* 배경 오버레이 */}
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => !isDeleting && setIsOpen(false)}
            aria-hidden="true"
          />

          {/* 다이얼로그 패널 */}
          <div className="relative z-10 w-full max-w-md mx-4 rounded-xl border border-[#374151] bg-[#111827] p-6 shadow-2xl">
            {/* 경고 아이콘 + 제목 */}
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-5 h-5 text-red-400" aria-hidden="true" />
              </div>
              <h2 id="delete-dialog-title" className="text-base font-semibold text-[#F9FAFB]">
                프로젝트 삭제
              </h2>
            </div>

            {/* 확인 문구 */}
            <p id="delete-dialog-desc" className="text-sm text-[#9CA3AF] mb-6 leading-relaxed">
              <span className="text-[#F9FAFB] font-medium">'{projectName}'</span>{' '}
              프로젝트를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
            </p>

            {/* 에러 메시지 */}
            {error && (
              <p
                role="alert"
                className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-4"
              >
                {error}
              </p>
            )}

            {/* 버튼 그룹 */}
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                disabled={isDeleting}
                className={`
                  px-4 py-2 text-sm font-medium rounded-lg
                  text-[#9CA3AF] hover:text-[#F9FAFB]
                  bg-[#1F2937] hover:bg-[#374151]
                  border border-[#374151]
                  transition-colors duration-150
                  disabled:opacity-50 disabled:cursor-not-allowed
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
                `}
                data-testid="delete-cancel-button"
              >
                취소
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={isDeleting}
                autoFocus
                className={`
                  inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg
                  text-white bg-red-600 hover:bg-red-500
                  transition-colors duration-150
                  disabled:opacity-50 disabled:cursor-not-allowed
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500
                `}
                data-testid="delete-confirm-button"
              >
                {isDeleting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                    삭제 중...
                  </>
                ) : (
                  '삭제'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
