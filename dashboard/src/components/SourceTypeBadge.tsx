/**
 * @file SourceTypeBadge.tsx
 * @description 프로젝트 소스 타입 배지 컴포넌트
 *
 * GitHub 타입: 보라색 배지
 * 로컬 타입: 주황색 배지
 *
 * Props:
 * - type: 'github' | 'local'
 * - size?: 'sm' | 'md' (기본값 'md')
 *
 * @see docs/02-design/ui-design.md §SourceTypeBadge
 */

interface SourceTypeBadgeProps {
  type: 'github' | 'local'
  size?: 'sm' | 'md'
}

/**
 * 소스 타입(GitHub/로컬)을 시각적으로 구분하는 배지 컴포넌트.
 * aria-label로 스크린 리더 접근성을 지원한다.
 */
export default function SourceTypeBadge({ type, size = 'md' }: SourceTypeBadgeProps) {
  const sizeClass = size === 'sm'
    ? 'text-[10px] px-1.5 py-0.5'
    : 'text-xs px-2 py-0.5'

  if (type === 'github') {
    return (
      <span
        className={`inline-flex items-center rounded-full border font-medium
          text-purple-400 bg-purple-500/10 border-purple-500/30
          ${sizeClass}`}
        aria-label="소스 타입: GitHub"
        data-testid="source-type-badge-github"
      >
        GitHub
      </span>
    )
  }

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium
        text-amber-400 bg-amber-500/10 border-amber-500/30
        ${sizeClass}`}
      aria-label="소스 타입: 로컬"
      data-testid="source-type-badge-local"
    >
      로컬
    </span>
  )
}
