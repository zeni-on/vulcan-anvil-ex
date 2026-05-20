/**
 * @file hooks/useProjectRuntime.ts
 * @description 프로젝트 runner/runtime 설정 SWR 훅
 */

import useSWR from 'swr'
import { fetcher } from '@/lib/swr'
import { RuntimeApiResponse } from '@/lib/types'

const REFRESH_INTERVAL = 30000

export function useProjectRuntime(id: string) {
  const { data, error, isLoading, mutate } = useSWR<RuntimeApiResponse>(
    id ? `/api/projects/${id}/runtime` : null,
    fetcher,
    { refreshInterval: REFRESH_INTERVAL },
  )

  return {
    runtime: data?.runtime ?? null,
    fetchedAt: data?.fetchedAt,
    isLoading,
    error,
    mutate,
  }
}
