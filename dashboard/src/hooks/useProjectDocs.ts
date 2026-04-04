/**
 * @file hooks/useProjectDocs.ts
 * @description 프로젝트 산출물 문서 목록 SWR 훅 (REQ-005-02, REQ-005-05)
 *
 * refreshInterval: 30000 — 30초 주기 자동 재검증.
 * session 훅과 SWR 캐시 키가 분리되어 독립적으로 갱신된다.
 *
 * @see docs/02-design/req-005-009-design.md §useProjectDocs
 */

import useSWR from 'swr'
import { fetcher } from '@/lib/swr'
import { DocsApiResponse } from '@/lib/types'

/** 30초 주기 재검증 — REQ-005-05, REQ-009-05 */
const REFRESH_INTERVAL = 30000

/**
 * 프로젝트 산출물 문서 목록을 패치하는 SWR 훅.
 *
 * @param id - projects.json의 프로젝트 id
 * @returns docs 배열, 로딩/에러 상태, 수동 재검증 함수
 */
export function useProjectDocs(id: string) {
  const { data, error, isLoading, mutate } = useSWR<DocsApiResponse>(
    id ? `/api/projects/${id}/docs` : null,
    fetcher,
    { refreshInterval: REFRESH_INTERVAL },
  )

  return {
    docs: data?.docs ?? [],
    fetchedAt: data?.fetchedAt,
    isLoading,
    error,
    mutate,
  }
}
