'use client'

/**
 * @file app/page.tsx
 * @description 멀티 프로젝트 홈 화면 (REQ-003)
 *
 * SWR로 /api/projects를 패치하여 프로젝트 카드 목록 또는 Empty State를 렌더링한다.
 * 로딩 중 스켈레톤, 오류 시 에러 배너, 빈 목록 시 EmptyState 표시.
 *
 * @see docs/02-design/req-001-004-design.md §page.tsx — 홈 페이지
 * @see docs/02-design/ui-design.md §페이지 1: 홈 (프로젝트 목록)
 */

import { useState } from 'react'
import useSWR from 'swr'
import { Plus, AlertCircle } from 'lucide-react'
import { fetcher } from '@/lib/swr'
import { Project } from '@/lib/types'
import AnvilIcon from '@/components/AnvilIcon'
import ProjectCard from '@/components/ProjectCard'
import EmptyState from '@/components/EmptyState'
import AddProjectDialog from '@/components/AddProjectDialog'

/** GET /api/projects 응답 타입 */
interface ProjectsResponse {
  projects: Project[]
}

/**
 * 스켈레톤 카드 — 로딩 중 animate-pulse 표시 (3개)
 */
function ProjectCardSkeleton() {
  return (
    <li
      role="listitem"
      aria-hidden="true"
      className="rounded-xl border border-[#374151] bg-[#111827] p-5 animate-pulse"
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="h-4 w-36 rounded bg-[#1F2937]" />
        <div className="h-4 w-14 rounded-full bg-[#1F2937]" />
      </div>
      <div className="space-y-2">
        <div className="h-3 w-48 rounded bg-[#1F2937]" />
        <div className="h-3 w-24 rounded bg-[#1F2937]" />
      </div>
    </li>
  )
}

/**
 * 홈 페이지 — 멀티 프로젝트 목록.
 * refreshInterval 미적용 (목록은 사용자 액션 기반 변경).
 */
export default function HomePage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const { data, error, isLoading, mutate } = useSWR<ProjectsResponse>(
    '/api/projects',
    fetcher,
  )

  const projects = data?.projects ?? []

  /** 삭제 성공 후 SWR 캐시를 낙관적으로 갱신한다 */
  const handleDelete = (deletedId: string) => {
    mutate(
      (prev) =>
        prev
          ? { projects: prev.projects.filter((p) => p.id !== deletedId) }
          : prev,
      { revalidate: false },
    )
  }

  /** 추가 성공 후 SWR 재검증을 트리거한다 */
  const handleAddSuccess = () => {
    mutate()
  }

  return (
    <>
      <div className="min-h-screen bg-[#030712]">
        {/* 헤더 */}
        <header className="sticky top-0 z-10 border-b border-[#374151] bg-[#030712]/90 backdrop-blur-sm">
          <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
            {/* 로고 */}
            <div className="flex items-center gap-2.5">
              <AnvilIcon className="w-6 h-6 text-blue-400" />
              <span className="text-sm font-semibold text-[#F9FAFB] tracking-tight">
                Vulcan Anvil
              </span>
            </div>

            {/* 프로젝트 추가 버튼 */}
            <button
              type="button"
              onClick={() => setIsDialogOpen(true)}
              className={`
                inline-flex items-center gap-1.5 px-3 py-1.5
                rounded-lg bg-blue-600 hover:bg-blue-500
                text-xs sm:text-sm font-medium text-white
                transition-colors duration-150
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-950
              `}
              data-testid="add-project-button"
            >
              <Plus className="w-4 h-4" aria-hidden="true" />
              <span className="hidden sm:inline">프로젝트 추가</span>
            </button>
          </div>
        </header>

        {/* 메인 콘텐츠 */}
        <main className="max-w-5xl mx-auto px-6 py-8">
          {/* 에러 배너 */}
          {error && !isLoading && (
            <div
              role="alert"
              className="flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 mb-8 text-sm text-red-400"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              프로젝트 목록을 불러오지 못했습니다. 잠시 후 다시 시도하세요.
              <button
                type="button"
                onClick={() => mutate()}
                className="ml-auto text-xs underline hover:no-underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 rounded"
              >
                재시도
              </button>
            </div>
          )}

          {/* 섹션 레이블 */}
          {!isLoading && !error && projects.length > 0 && (
            <p className="text-xs font-semibold text-[#4B5563] uppercase tracking-widest mb-4">
              프로젝트 ({projects.length}개)
            </p>
          )}

          {/* 로딩 스켈레톤 */}
          {isLoading && (
            <ul
              role="list"
              aria-busy="true"
              aria-label="프로젝트 목록 불러오는 중"
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <ProjectCardSkeleton />
              <ProjectCardSkeleton />
              <ProjectCardSkeleton />
            </ul>
          )}

          {/* 프로젝트 카드 목록 */}
          {!isLoading && projects.length > 0 && (
            <ul
              role="list"
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
              data-testid="project-list"
            >
              {projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onDelete={handleDelete}
                />
              ))}
            </ul>
          )}

          {/* 빈 상태 */}
          {!isLoading && !error && projects.length === 0 && (
            <EmptyState onAddProject={() => setIsDialogOpen(true)} />
          )}
        </main>
      </div>

      {/* 프로젝트 추가 다이얼로그 */}
      <AddProjectDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onSuccess={handleAddSuccess}
      />
    </>
  )
}
