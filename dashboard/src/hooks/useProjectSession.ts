/**
 * @file hooks/useProjectSession.ts
 * @description 프로젝트 Gate 상태 SWR 훅 (REQ-005-01, REQ-005-05)
 *
 * refreshInterval: 30000 — 30초 주기 자동 재검증으로 Gate 상태 최신화를 유지한다.
 * session과 docs, commits는 SWR 키가 분리되어 있어 독립적으로 stale/revalidate된다.
 *
 * UT-005-09: SWR refreshInterval이 30000으로 설정됨
 *
 * @see docs/02-design/req-005-009-design.md §useProjectSession
 */

import useSWR from 'swr'
import { fetcher } from '@/lib/swr'
import { SessionApiResponse } from '@/lib/types'

/** 30초 주기 재검증 — REQ-005-05, REQ-009-05 */
const REFRESH_INTERVAL = 30000

/**
 * 프로젝트 Gate 상태를 패치하는 SWR 훅.
 *
 * @param id - projects.json의 프로젝트 id
 * @returns session 데이터, 로딩/에러 상태, 수동 재검증 함수
 */
export function useProjectSession(id: string) {
  const { data, error, isLoading, mutate } = useSWR<SessionApiResponse>(
    id ? `/api/projects/${id}/session` : null,
    fetcher,
    { refreshInterval: REFRESH_INTERVAL },
  )

  return {
    session: data?.session ?? null,
    fetchedAt: data?.fetchedAt,
    isLoading,
    error,
    mutate,
  }
}
