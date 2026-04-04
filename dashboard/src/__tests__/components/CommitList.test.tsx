/**
 * @file __tests__/components/CommitList.test.tsx
 * @description CommitList 컴포넌트 렌더링 테스트
 *
 * 커버 항목:
 * - data-testid="commit-list" 컨테이너 렌더링
 * - 빈 배열 → "커밋 이력이 없습니다." 메시지 표시
 * - 커밋 해시 앞 7자 표시
 * - 커밋 메시지 표시
 * - 작성자 표시
 * - 최대 10개 제한 (11개 입력 시 10개만 표시)
 * - role="list" 접근성 속성
 *
 * @see docs/02-design/req-005-009-design.md §CommitList
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import CommitList from '@/components/CommitList'
import { CommitEntry } from '@/lib/types'

/** 테스트용 커밋 항목 생성 헬퍼 */
function makeCommit(index: number): CommitEntry {
  return {
    sha:     `abcdef${index.toString().padStart(2, '0')}0123456789`,
    message: `docs: 테스트 커밋 ${index}`,
    author:  `author${index}`,
    date:    new Date(Date.now() - index * 3_600_000).toISOString(),
  }
}

const mockCommits: CommitEntry[] = [
  {
    sha:     'abc1234567890',
    message: 'docs: Gate 2 설계 문서 추가',
    author:  'iamsong',
    date:    new Date(Date.now() - 3_600_000).toISOString(), // 1시간 전
  },
  {
    sha:     'def5678901234',
    message: 'feat: 프로젝트 상세 페이지 구현',
    author:  'iamsong',
    date:    new Date(Date.now() - 7_200_000).toISOString(), // 2시간 전
  },
  {
    sha:     'ghi9012345678',
    message: 'fix: SWR refreshInterval 수정',
    author:  'contributor',
    date:    new Date(Date.now() - 86_400_000).toISOString(), // 1일 전
  },
]

describe('CommitList', () => {
  it('data-testid="commit-list" 컨테이너를 렌더링한다', () => {
    render(<CommitList commits={mockCommits} />)
    expect(screen.getByTestId('commit-list')).toBeInTheDocument()
  })

  it('빈 배열 전달 시 "커밋 이력이 없습니다." 메시지를 표시한다', () => {
    render(<CommitList commits={[]} />)
    expect(screen.getByTestId('commit-list-empty')).toBeInTheDocument()
    expect(screen.getByText('커밋 이력이 없습니다.')).toBeInTheDocument()
  })

  it('커밋 해시를 앞 7자로 잘라서 표시한다', () => {
    render(<CommitList commits={mockCommits} />)
    const hashElements = screen.getAllByTestId('commit-hash')
    expect(hashElements[0]).toHaveTextContent('abc1234')
    expect(hashElements[1]).toHaveTextContent('def5678')
  })

  it('커밋 메시지를 표시한다', () => {
    render(<CommitList commits={mockCommits} />)
    expect(screen.getByText('docs: Gate 2 설계 문서 추가')).toBeInTheDocument()
    expect(screen.getByText('feat: 프로젝트 상세 페이지 구현')).toBeInTheDocument()
  })

  it('작성자 이름을 표시한다', () => {
    render(<CommitList commits={mockCommits} />)
    const authorElements = screen.getAllByTestId('commit-author')
    expect(authorElements[0]).toHaveTextContent('iamsong')
  })

  it('role="list" 접근성 속성을 가진다', () => {
    render(<CommitList commits={mockCommits} />)
    expect(screen.getByRole('list')).toBeInTheDocument()
  })

  it('커밋이 3개일 때 3개의 listitem을 렌더링한다', () => {
    render(<CommitList commits={mockCommits} />)
    expect(screen.getAllByRole('listitem')).toHaveLength(3)
  })

  it('11개 입력 시 최대 10개만 렌더링한다 (REQ-005-03)', () => {
    const elevenCommits = Array.from({ length: 11 }, (_, i) => makeCommit(i))
    render(<CommitList commits={elevenCommits} />)
    expect(screen.getAllByTestId('commit-item')).toHaveLength(10)
  })

  it('1시간 전 커밋은 "1시간 전" 형식으로 표시한다', () => {
    render(<CommitList commits={mockCommits} />)
    expect(screen.getByText('1시간 전')).toBeInTheDocument()
  })
})
