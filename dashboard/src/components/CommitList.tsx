/**
 * @file components/CommitList.tsx
 * @description 최근 커밋 이력 목록 컴포넌트 (REQ-005-03)
 *
 * CommitEntry[]를 타임라인 형태로 표시한다.
 * 기존 GitTimeline.tsx는 vulcan.py 특화 GitEntry 타입을 사용하므로
 * CommitEntry 타입 기반으로 새 컴포넌트를 구현한다.
 *
 * 커밋 메시지 유형 접두사에 색상을 적용한다:
 * - docs: → blue, feat: → green, fix: → red, 기타 → gray
 *
 * @see docs/02-design/req-005-009-design.md §CommitList
 * @see docs/02-design/ui-design.md §CommitList
 */

import { CommitEntry } from '@/lib/types'

/** 커밋 메시지 유형 접두사 → 색상 매핑 */
const PREFIX_COLOR: Record<string, string> = {
  'docs':    'text-blue-400',
  'feat':    'text-green-400',
  'fix':     'text-red-400',
  'refactor':'text-purple-400',
  'test':    'text-yellow-400',
  'chore':   'text-gray-400',
  'init':    'text-green-400',
  'style':   'text-pink-400',
  'perf':    'text-orange-400',
  'build':   'text-gray-400',
  'ci':      'text-gray-400',
}

/** ISO 8601 날짜 문자열을 "N분 전" 형식으로 변환한다. */
function formatRelativeDate(isoDate: string): string {
  if (!isoDate) return ''
  const diff = Date.now() - new Date(isoDate).getTime()
  const minutes = Math.floor(diff / 60_000)
  if (minutes < 1)   return '방금 전'
  if (minutes < 60)  return `${minutes}분 전`
  const hours = Math.floor(minutes / 60)
  if (hours < 24)    return `${hours}시간 전`
  const days = Math.floor(hours / 24)
  if (days < 30)     return `${days}일 전`
  const months = Math.floor(days / 30)
  return `${months}개월 전`
}

/** 커밋 메시지 유형 접두사를 파싱하여 색상 클래스를 반환한다. */
function getPrefixColor(message: string): string {
  const match = message.match(/^(\w+)(\(.+?\))?:\s/)
  if (!match) return 'text-gray-300'
  return PREFIX_COLOR[match[1]] ?? 'text-gray-300'
}

interface CommitListProps {
  commits: CommitEntry[]
}

/**
 * 커밋 이력을 타임라인 형태로 렌더링한다.
 * 해시는 앞 7자만 표시하고, 커밋 유형 접두사에 색상을 적용한다.
 */
export default function CommitList({ commits }: CommitListProps) {
  // 최대 10개 제한 (설계 §CommitList)
  const displayCommits = commits.slice(0, 10)

  if (displayCommits.length === 0) {
    return (
      <p className="text-sm text-[#6B7280] py-2" data-testid="commit-list-empty">
        커밋 이력이 없습니다.
      </p>
    )
  }

  return (
    <div className="relative" data-testid="commit-list">
      {/* 세로 타임라인 선 */}
      <div
        aria-hidden="true"
        className="absolute left-[3px] top-2 bottom-2 w-px bg-[#1F2937]"
      />

      <ul className="space-y-2" role="list">
        {displayCommits.map((commit) => (
          <li
            key={commit.sha}
            className="flex items-start gap-2 pl-0 py-0"
            role="listitem"
            data-testid="commit-item"
          >
            {/* 타임라인 도트 */}
            <div
              aria-hidden="true"
              className="w-2 h-2 rounded-full flex-shrink-0 mt-1 bg-[#374151] border border-[#4B5563]"
            />

            <div className="flex-1 min-w-0">
              {/* 커밋 해시 + 메시지 */}
              <div className="min-w-0">
                <span
                  className="font-mono text-[10px] text-[#6B7280] mr-1.5"
                  title={commit.sha}
                  data-testid="commit-hash"
                >
                  {commit.sha.slice(0, 7)}
                </span>
                <span
                  className={`text-[11px] break-words ${getPrefixColor(commit.message)}`}
                  title={commit.message}
                  data-testid="commit-message"
                >
                  {commit.message}
                </span>
              </div>

              {/* 작성자 + 날짜 */}
              <div className="text-[10px] text-[#4B5563] mt-0.5">
                <span data-testid="commit-author">{commit.author}</span>
                <span className="mx-1" aria-hidden="true">·</span>
                <span data-testid="commit-date" title={commit.date}>
                  {formatRelativeDate(commit.date)}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
