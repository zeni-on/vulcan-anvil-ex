/**
 * @file __tests__/components/AddProjectDialog.test.tsx
 * @description AddProjectDialog 컴포넌트 렌더링 및 상호작용 테스트
 *
 * 커버 항목:
 * - open=false 시 렌더링하지 않음
 * - open=true 시 다이얼로그 렌더링
 * - GitHub/로컬 탭 전환
 * - 필수 필드 미입력 시 오류 메시지 표시
 * - 취소 버튼 클릭 시 onOpenChange(false) 호출
 *
 * @see docs/02-design/ui-design.md §AddProjectDialog
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import AddProjectDialog from '@/components/AddProjectDialog'

// fetch 모킹
global.fetch = jest.fn()

describe('AddProjectDialog', () => {
  const defaultProps = {
    open: true,
    onOpenChange: jest.fn(),
    onSuccess: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('open=false 시 다이얼로그를 렌더링하지 않는다', () => {
    render(<AddProjectDialog {...defaultProps} open={false} />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('open=true 시 다이얼로그를 렌더링한다', () => {
    render(<AddProjectDialog {...defaultProps} />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('"프로젝트 추가" 제목을 렌더링한다', () => {
    render(<AddProjectDialog {...defaultProps} />)
    // 제목과 버튼에 모두 "프로젝트 추가" 텍스트가 있으므로 heading 역할로 확인
    expect(screen.getByRole('heading', { name: '프로젝트 추가' })).toBeInTheDocument()
  })

  it('기본값으로 GitHub 탭이 선택되어 있다', () => {
    render(<AddProjectDialog {...defaultProps} />)
    const githubTab = screen.getByTestId('tab-github')
    expect(githubTab).toHaveAttribute('aria-pressed', 'true')
  })

  it('로컬 탭 클릭 시 로컬 경로 입력 필드가 표시된다', () => {
    render(<AddProjectDialog {...defaultProps} />)
    fireEvent.click(screen.getByTestId('tab-local'))
    expect(screen.getByTestId('input-path')).toBeInTheDocument()
  })

  it('GitHub 탭 선택 시 repo/branch 입력 필드가 표시된다', () => {
    render(<AddProjectDialog {...defaultProps} />)
    expect(screen.getByTestId('input-repo')).toBeInTheDocument()
    expect(screen.getByTestId('input-branch')).toBeInTheDocument()
  })

  it('GitHub repo 미입력 시 오류 메시지가 표시된다', async () => {
    render(<AddProjectDialog {...defaultProps} />)

    fireEvent.click(screen.getByTestId('dialog-submit-button'))

    await waitFor(() => {
      expect(screen.getByText('GitHub 저장소를 입력하세요.')).toBeInTheDocument()
    })
  })

  it('GitHub repo 형식 오류 시 오류 메시지가 표시된다', async () => {
    render(<AddProjectDialog {...defaultProps} />)

    fireEvent.change(screen.getByTestId('input-repo'), { target: { value: 'invalid-format' } })
    fireEvent.click(screen.getByTestId('dialog-submit-button'))

    await waitFor(() => {
      expect(screen.getByText('owner/repo 형식으로 입력하세요.')).toBeInTheDocument()
    })
  })

  it('로컬 탭에서 비절대경로 입력 시 오류 메시지가 표시된다', async () => {
    render(<AddProjectDialog {...defaultProps} />)

    fireEvent.click(screen.getByTestId('tab-local'))
    fireEvent.change(screen.getByTestId('input-path'), { target: { value: 'relative/path' } })
    fireEvent.click(screen.getByTestId('dialog-submit-button'))

    await waitFor(() => {
      expect(screen.getByText('절대 경로(/ 또는 드라이브 문자로 시작)여야 합니다.')).toBeInTheDocument()
    })
  })

  it('취소 버튼 클릭 시 onOpenChange(false)를 호출한다', () => {
    const onOpenChange = jest.fn()
    render(<AddProjectDialog {...defaultProps} onOpenChange={onOpenChange} />)

    fireEvent.click(screen.getByTestId('dialog-cancel-button'))

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('API 호출 성공 시 onSuccess와 onOpenChange(false)를 호출한다', async () => {
    const onSuccess = jest.fn()
    const onOpenChange = jest.fn()
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ project: { id: 'new-id' } }),
    })

    render(<AddProjectDialog {...defaultProps} onSuccess={onSuccess} onOpenChange={onOpenChange} />)

    fireEvent.change(screen.getByTestId('input-repo'), { target: { value: 'owner/repo' } })
    fireEvent.click(screen.getByTestId('dialog-submit-button'))

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onOpenChange).toHaveBeenCalledWith(false)
    })
  })

  it('API 호출 실패 시 서버 오류 메시지를 표시한다', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ error: '이미 등록된 프로젝트입니다' }),
    })

    render(<AddProjectDialog {...defaultProps} />)

    fireEvent.change(screen.getByTestId('input-repo'), { target: { value: 'owner/repo' } })
    fireEvent.click(screen.getByTestId('dialog-submit-button'))

    await waitFor(() => {
      expect(screen.getByText('이미 등록된 프로젝트입니다')).toBeInTheDocument()
    })
  })
})
