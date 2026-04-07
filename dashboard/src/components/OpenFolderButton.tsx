'use client'

/**
 * @file components/OpenFolderButton.tsx
 * @description 산출물 문서 헤더 옆의 "OS 파일 탐색기로 열기" 버튼.
 *
 * local 프로젝트일 때만 렌더되며, POST /api/projects/[id]/open-folder를 호출해
 * 서버가 프로젝트 docs/ 폴더를 OS 기본 탐색기로 연다 (WSL: explorer.exe).
 */

import { useState } from 'react'
import { FolderOpen } from 'lucide-react'

interface OpenFolderButtonProps {
  projectId: string
}

export default function OpenFolderButton({ projectId }: OpenFolderButtonProps) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleClick = async () => {
    if (busy) return
    setBusy(true)
    setError(null)
    try {
      const res = await fetch(`/api/projects/${projectId}/open-folder`, { method: 'POST' })
      if (!res.ok) {
        const body = (await res.json().catch(() => ({}))) as { error?: string }
        setError(body.error ?? `폴더 열기 실패 (${res.status})`)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
      // 에러 메시지는 3초 뒤 자동으로 사라지게
      if (error) setTimeout(() => setError(null), 3000)
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={busy}
      title={error ?? '파일 탐색기로 docs 폴더 열기'}
      aria-label="파일 탐색기로 docs 폴더 열기"
      data-testid="open-folder-button"
      className={`inline-flex items-center justify-center w-6 h-6 rounded transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
        error
          ? 'text-red-400 hover:bg-red-500/10'
          : 'text-[#9CA3AF] hover:text-[#F9FAFB] hover:bg-zinc-700/60'
      } disabled:opacity-50 disabled:cursor-wait`}
    >
      <FolderOpen className="w-4 h-4" aria-hidden="true" />
    </button>
  )
}
