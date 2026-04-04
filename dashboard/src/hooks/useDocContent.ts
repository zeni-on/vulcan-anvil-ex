/**
 * @file hooks/useDocContent.ts
 * @description 선택된 DocNode의 .md 파일 내용을 SWR로 패치하는 훅 (REQ-010-01)
 *
 * - doc === null이면 SWR 패치 건너뜀
 * - refreshInterval: 0 — Drawer가 열릴 때 1회만 로드
 *
 * @see docs/02-design/req-010-design.md §useDocContent 훅
 */

import useSWR from 'swr'
import { DocNode } from '@/lib/types'

const fetcher = (url: string) =>
  fetch(url).then((res) => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json() as Promise<{ content: string }>
  })

export function useDocContent(projectId: string, doc: DocNode | null) {
  // slug의 첫 요소 'docs'는 API 경로에 이미 포함되므로 제외
  const key = doc
    ? `/api/projects/${projectId}/docs/${doc.slug.slice(1).join('/')}`
    : null

  const { data, isLoading, error } = useSWR(key, fetcher, {
    refreshInterval: 0,
    revalidateOnFocus: false,
  })

  return {
    content: data?.content ?? null,
    isLoading,
    error,
  }
}
