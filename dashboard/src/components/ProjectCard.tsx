'use client'

/**
 * @file ProjectCard.tsx
 * @description 프로젝트 목록 카드 컴포넌트
 *
 * 프로젝트 요약 정보(이름, 소스 타입 배지, 등록일)를 카드 형태로 표시하고
 * 상세 페이지(/projects/[id])로의 링크를 제공한다.
 *
 * Props:
 * - project: Project — GitHubProject | LocalProject
 * - onDelete: (id: string) => void — 삭제 콜백 (SWR mutate 트리거)
 *
 * @see docs/02-design/ui-design.md §ProjectCard
 * @see docs/02-design/req-001-004-design.md §ProjectCard
 */

import Link from 'next/link'
import { Project } from '@/lib/types'
import SourceTypeBadge from './SourceTypeBadge'
import DeleteProjectButton from './DeleteProjectButton'

interface ProjectCardProps {
  project: Project
  onDelete: (id: string) => void
}

/**
 * 등록일(addedAt)을 사람이 읽기 쉬운 상대시각으로 변환한다.
 * 예: "3일 전", "방금 전"
 */
function formatRelativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime()
  const minutes = Math.floor(diff / 60_000)
  if (minutes < 1) return '방금 전'
  if (minutes < 60) return `${minutes}분 전`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}시간 전`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}일 전`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months}개월 전`
  return `${Math.floor(months / 12)}년 전`
}

/**
 * 단일 프로젝트 카드.
 * 카드 전체 영역이 상세 페이지 링크이며, 삭제 버튼은 링크 외부에서 이벤트 전파를 중단한다.
 */
export default function ProjectCard({ project, onDelete }: ProjectCardProps) {
  return (
    <li
      role="listitem"
      className="group relative"
      data-testid="project-card"
    >
      <Link
        href={`/projects/${project.id}`}
        className={`
          block rounded-xl border bg-[#111827] border-[#374151] p-5
          transition-all duration-200
          hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950
        `}
        aria-label={`${project.name} 프로젝트 상세 보기`}
      >
        {/* 카드 헤더: 이름 + 소스 타입 배지 */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <h3 className="text-[15px] font-semibold text-[#F9FAFB] truncate leading-snug">
            {project.name}
          </h3>
          <SourceTypeBadge type={project.type} size="sm" />
        </div>

        {/* 프로젝트 메타 정보 */}
        <div className="space-y-1">
          {project.type === 'github' && (
            <p className="text-xs text-[#9CA3AF] truncate">
              {project.repo}
              <span className="text-[#4B5563] mx-1">/</span>
              {project.branch}
            </p>
          )}
          {project.type === 'local' && (
            <p className="text-xs text-[#9CA3AF] truncate font-mono">
              {project.path}
            </p>
          )}
          <p className="text-xs text-[#4B5563]">
            등록: {formatRelativeTime(project.addedAt)}
          </p>
        </div>
      </Link>

      {/* 삭제 버튼 — 카드 오른쪽 하단에 절대 위치, 링크 클릭 전파 차단 */}
      <div
        className="absolute bottom-4 right-4"
        onClick={(e) => e.preventDefault()}
      >
        <DeleteProjectButton
          projectId={project.id}
          projectName={project.name}
          onSuccess={() => onDelete(project.id)}
        />
      </div>
    </li>
  )
}
