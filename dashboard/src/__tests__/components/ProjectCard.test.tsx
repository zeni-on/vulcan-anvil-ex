/**
 * @file __tests__/components/ProjectCard.test.tsx
 * @description ProjectCard 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - GitHub 프로젝트 카드 렌더링 (이름, 배지, repo/branch, 등록일)
 * - 로컬 프로젝트 카드 렌더링 (이름, 배지, 경로, 등록일)
 * - 삭제 버튼 존재 확인
 * - 상세 페이지 링크(/projects/[id]) 확인
 *
 * @see docs/02-design/ui-design.md §ProjectCard
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import ProjectCard from '@/components/ProjectCard'
import type { GitHubProject, LocalProject } from '@/lib/types'

// Next.js Link 컴포넌트 모킹
jest.mock('next/link', () => {
  const MockLink = ({ href, children, ...props }: { href: string; children: React.ReactNode; [key: string]: unknown }) => (
    <a href={href} {...props}>{children}</a>
  )
  MockLink.displayName = 'Link'
  return MockLink
})

const githubProject: GitHubProject = {
  id: 'github-owner-repo-abc',
  name: 'My GitHub Project',
  type: 'github',
  repo: 'owner/repo',
  branch: 'main',
  addedAt: new Date(Date.now() - 86_400_000).toISOString(), // 1일 전
}

const localProject: LocalProject = {
  id: 'local-home-user-app-xyz',
  name: 'My Local Project',
  type: 'local',
  path: '/home/user/projects/app',
  addedAt: new Date(Date.now() - 3_600_000).toISOString(), // 1시간 전
}

describe('ProjectCard', () => {
  it('GitHub 프로젝트 이름을 렌더링한다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    expect(screen.getByText('My GitHub Project')).toBeInTheDocument()
  })

  it('GitHub 소스 타입 배지를 렌더링한다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    expect(screen.getByTestId('source-type-badge-github')).toBeInTheDocument()
  })

  it('GitHub 프로젝트에 repo/branch 정보를 표시한다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    // repo와 branch는 같은 <p> 요소 안에 있지만 span으로 구분되므로 부분 텍스트로 확인
    expect(screen.getByText((content, element) =>
      element?.tagName === 'P' && content.includes('owner/repo') && content.includes('main')
    )).toBeInTheDocument()
  })

  it('로컬 프로젝트 이름을 렌더링한다', () => {
    render(<ProjectCard project={localProject} onDelete={() => {}} />)
    expect(screen.getByText('My Local Project')).toBeInTheDocument()
  })

  it('로컬 소스 타입 배지를 렌더링한다', () => {
    render(<ProjectCard project={localProject} onDelete={() => {}} />)
    expect(screen.getByTestId('source-type-badge-local')).toBeInTheDocument()
  })

  it('로컬 프로젝트에 경로를 표시한다', () => {
    render(<ProjectCard project={localProject} onDelete={() => {}} />)
    expect(screen.getByText('/home/user/projects/app')).toBeInTheDocument()
  })

  it('상세 페이지 링크(/projects/[id])를 포함한다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    const link = screen.getByRole('link', { name: /My GitHub Project/ })
    expect(link).toHaveAttribute('href', '/projects/github-owner-repo-abc')
  })

  it('삭제 버튼을 포함한다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    expect(screen.getByTestId('delete-project-button')).toBeInTheDocument()
  })

  it('등록일 상대시각을 표시한다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    expect(screen.getByText(/등록:/)).toBeInTheDocument()
  })

  it('role="listitem"으로 렌더링된다', () => {
    render(<ProjectCard project={githubProject} onDelete={() => {}} />)
    expect(screen.getByRole('listitem')).toBeInTheDocument()
  })
})
