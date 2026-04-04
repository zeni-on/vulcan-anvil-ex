/**
 * @file lib/swr.ts
 * @description SWR fetcher 및 전역 설정
 *
 * 역할:
 * - 기본 JSON fetcher 함수 제공
 * - SWR 전역 설정 (에러 핸들링, 재시도 정책)
 *
 * @see docs/02-design/req-001-004-design.md §page.tsx — 홈 페이지
 */

/**
 * SWR 기본 fetcher.
 * 네트워크 오류 또는 HTTP 오류 응답 시 Error를 throw하여 SWR의 error 상태로 처리한다.
 */
export async function fetcher<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }))
    const error = new Error(body?.error ?? `HTTP ${res.status}`)
    throw error
  }
  return res.json() as Promise<T>
}
