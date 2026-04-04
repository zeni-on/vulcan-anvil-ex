/**
 * @file hooks/useProjectCommits.ts
 * @description 프로젝트 커밋 이력 SWR 훅 (REQ-005-03, REQ-005-05)
 *
 * refreshInterval: 30000 — 30초 주기 자동 재검증.
 * session, docs 훅과 SWR 캐시 키가 분리되어 독립적으로 갱신된다.
 *
 * @see docs/02-design/req-005-009-design.md §useProjectCommits
 */

import useSWR from 'swr'
import { fetcher } from '@/lib/swr'
import { CommitsApiResponse } from '@/lib/types'

/** 30초 주기 재검증 — REQ-005-05, REQ-009-05 */
const REFRESH_INTERVAL = 30000

/**
 * 프로젝트 커밋 이력을 패치하는 SWR 훅.
 *
 * @param id - projects.json의 프로젝트 id
 * @returns commits 배열(최대 10개), 로딩/에러 상태, 수동 재검증 함수
 */
export function useProjectCommits(id: string) {
  const { data, error, isLoading, mutate } = useSWR<CommitsApiResponse>(
    id ? `/api/projects/${id}/commits` : null,
    fetcher,
    { refreshInterval: REFRESH_INTERVAL },
  )

  return {
    commits: data?.commits ?? [],
    fetchedAt: data?.fetchedAt,
    isLoading,
    error,
    mutate,
  }
}
