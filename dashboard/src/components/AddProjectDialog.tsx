'use client'

/**
 * @file AddProjectDialog.tsx
 * @description 프로젝트 추가 다이얼로그 컴포넌트
 *
 * 소스 타입 선택(GitHub/로컬) → 타입별 필드 입력 → POST /api/projects 호출
 * 성공 시 onSuccess 콜백(SWR mutate)을 호출하고 다이얼로그를 닫는다.
 *
 * Props:
 * - open: boolean
 * - onOpenChange: (open: boolean) => void
 * - onSuccess: () => void — SWR mutate 트리거
 *
 * @see docs/02-design/ui-design.md §AddProjectDialog
 * @see docs/02-design/req-001-004-design.md §AddProjectDialog
 */

import { useState, useEffect } from 'react'
import { X, Github, FolderOpen, Loader2 } from 'lucide-react'

interface AddProjectDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

type SourceType = 'github' | 'local'

interface FormState {
  type: SourceType
  repo: string
  branch: string
  path: string
}

interface FormErrors {
  repo?: string
  branch?: string
  path?: string
  server?: string
}

const INITIAL_FORM: FormState = {
  type: 'github',
  repo: '',
  branch: 'main',
  path: '',
}

/**
 * 폼 유효성 클라이언트 검사.
 * 서버 검증과 동일한 규칙을 클라이언트에서 먼저 적용하여 UX를 향상시킨다.
 */
function validate(form: FormState): FormErrors {
  const errors: FormErrors = {}

  if (form.type === 'github') {
    if (!form.repo.trim()) {
      errors.repo = 'GitHub 저장소를 입력하세요.'
    } else if (!/^[^/]+\/[^/]+$/.test(form.repo.trim())) {
      errors.repo = 'owner/repo 형식으로 입력하세요.'
    }
    if (!form.branch.trim()) {
      errors.branch = '브랜치를 입력하세요.'
    }
  }

  if (form.type === 'local') {
    if (!form.path.trim()) {
      errors.path = '절대 경로를 입력하세요.'
    } else {
      const p = form.path.trim()
      const isAbsolute = p.startsWith('/') || /^[A-Za-z]:[/\\]/.test(p)
      if (!isAbsolute) {
        errors.path = '절대 경로(/ 또는 드라이브 문자로 시작)여야 합니다.'
      }
    }
  }

  return errors
}

/**
 * 프로젝트 추가 다이얼로그.
 * GitHub/로컬 탭 전환, 폼 유효성 검사, API 호출, 에러 표시를 처리한다.
 */
export default function AddProjectDialog({
  open,
  onOpenChange,
  onSuccess,
}: AddProjectDialogProps) {
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 다이얼로그가 열릴 때마다 폼 초기화
  useEffect(() => {
    if (open) {
      setForm(INITIAL_FORM)
      setErrors({})
    }
  }, [open])

  // Escape 키로 닫기
  useEffect(() => {
    if (!open) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) {
        onOpenChange(false)
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open, isSubmitting, onOpenChange])

  if (!open) return null

  const handleTypeChange = (type: SourceType) => {
    setForm((prev) => ({ ...prev, type }))
    setErrors({})
  }

  const handleChange = (field: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const validationErrors = validate(form)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    setIsSubmitting(true)
    setErrors({})

    try {
      const body =
        form.type === 'github'
          ? { type: 'github', repo: form.repo.trim(), branch: form.branch.trim() }
          : { type: 'local', path: form.path.trim() }

      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.error ?? `서버 오류 (HTTP ${res.status})`)
      }

      onSuccess()
      onOpenChange(false)
    } catch (err) {
      setErrors({ server: err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-dialog-title"
      className="fixed inset-0 z-50 flex items-center justify-center"
    >
      {/* 배경 오버레이 */}
      <div
        className="absolute inset-0 bg-black/60"
        onClick={() => !isSubmitting && onOpenChange(false)}
        aria-hidden="true"
      />

      {/* 다이얼로그 패널 */}
      <div className="relative z-10 w-full max-w-md mx-4 rounded-xl border border-[#374151] bg-[#111827] shadow-2xl">
        {/* 헤더 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#374151]">
          <h2 id="add-dialog-title" className="text-base font-semibold text-[#F9FAFB]">
            프로젝트 추가
          </h2>
          <button
            type="button"
            onClick={() => !isSubmitting && onOpenChange(false)}
            disabled={isSubmitting}
            className="p-1.5 rounded-md text-[#4B5563] hover:text-[#9CA3AF] hover:bg-[#1F2937] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="다이얼로그 닫기"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        {/* 폼 */}
        <form onSubmit={handleSubmit} noValidate>
          <div className="px-6 py-5 space-y-5">
            {/* 소스 타입 선택 탭 */}
            <div>
              <label className="block text-xs font-semibold text-[#4B5563] uppercase tracking-widest mb-2">
                소스 타입
              </label>
              <div className="grid grid-cols-2 gap-2" role="group" aria-label="소스 타입 선택">
                <button
                  type="button"
                  onClick={() => handleTypeChange('github')}
                  disabled={isSubmitting}
                  className={`
                    flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border text-sm font-medium
                    transition-all duration-150
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
                    ${form.type === 'github'
                      ? 'bg-blue-600/20 border-blue-500/50 text-blue-400'
                      : 'bg-[#1F2937] border-[#374151] text-[#9CA3AF] hover:border-[#6B7280]'
                    }
                  `}
                  aria-pressed={form.type === 'github'}
                  data-testid="tab-github"
                >
                  <Github className="w-4 h-4" aria-hidden="true" />
                  GitHub
                </button>
                <button
                  type="button"
                  onClick={() => handleTypeChange('local')}
                  disabled={isSubmitting}
                  className={`
                    flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border text-sm font-medium
                    transition-all duration-150
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
                    ${form.type === 'local'
                      ? 'bg-blue-600/20 border-blue-500/50 text-blue-400'
                      : 'bg-[#1F2937] border-[#374151] text-[#9CA3AF] hover:border-[#6B7280]'
                    }
                  `}
                  aria-pressed={form.type === 'local'}
                  data-testid="tab-local"
                >
                  <FolderOpen className="w-4 h-4" aria-hidden="true" />
                  로컬 경로
                </button>
              </div>
            </div>

            {/* GitHub 전용 필드 */}
            {form.type === 'github' && (
              <>
                <div>
                  <label htmlFor="project-repo" className="block text-sm font-medium text-[#F9FAFB] mb-1.5">
                    저장소 (owner/repo) <span aria-hidden="true" className="text-red-400">*</span>
                  </label>
                  <input
                    id="project-repo"
                    type="text"
                    value={form.repo}
                    onChange={(e) => handleChange('repo', e.target.value)}
                    disabled={isSubmitting}
                    placeholder="예: octocat/hello-world"
                    className={`
                      w-full rounded-lg border bg-[#0F172A] px-3 py-2 text-sm text-[#F9FAFB]
                      placeholder:text-[#4B5563]
                      focus:outline-none focus:ring-2 focus:ring-blue-500
                      disabled:opacity-50 disabled:cursor-not-allowed
                      transition-colors
                      ${errors.repo ? 'border-red-500' : 'border-[#374151] focus:border-blue-500'}
                    `}
                    aria-required="true"
                    aria-invalid={!!errors.repo}
                    aria-describedby={errors.repo ? 'repo-error' : undefined}
                    data-testid="input-repo"
                  />
                  {errors.repo && (
                    <p id="repo-error" role="alert" className="mt-1 text-xs text-red-400">
                      {errors.repo}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="project-branch" className="block text-sm font-medium text-[#F9FAFB] mb-1.5">
                    브랜치
                  </label>
                  <input
                    id="project-branch"
                    type="text"
                    value={form.branch}
                    onChange={(e) => handleChange('branch', e.target.value)}
                    disabled={isSubmitting}
                    placeholder="main"
                    className={`
                      w-full rounded-lg border bg-[#0F172A] px-3 py-2 text-sm text-[#F9FAFB]
                      placeholder:text-[#4B5563]
                      focus:outline-none focus:ring-2 focus:ring-blue-500
                      disabled:opacity-50 disabled:cursor-not-allowed
                      transition-colors
                      ${errors.branch ? 'border-red-500' : 'border-[#374151] focus:border-blue-500'}
                    `}
                    aria-invalid={!!errors.branch}
                    aria-describedby={errors.branch ? 'branch-error' : undefined}
                    data-testid="input-branch"
                  />
                  {errors.branch && (
                    <p id="branch-error" role="alert" className="mt-1 text-xs text-red-400">
                      {errors.branch}
                    </p>
                  )}
                </div>
              </>
            )}

            {/* 로컬 전용 필드 */}
            {form.type === 'local' && (
              <div>
                <label htmlFor="project-path" className="block text-sm font-medium text-[#F9FAFB] mb-1.5">
                  프로젝트 절대 경로 <span aria-hidden="true" className="text-red-400">*</span>
                </label>
                <input
                  id="project-path"
                  type="text"
                  value={form.path}
                  onChange={(e) => handleChange('path', e.target.value)}
                  disabled={isSubmitting}
                  placeholder="예: /Users/user/projects/my-proj"
                  className={`
                    w-full rounded-lg border bg-[#0F172A] px-3 py-2 text-sm text-[#F9FAFB] font-mono
                    placeholder:text-[#4B5563] placeholder:font-sans
                    focus:outline-none focus:ring-2 focus:ring-blue-500
                    disabled:opacity-50 disabled:cursor-not-allowed
                    transition-colors
                    ${errors.path ? 'border-red-500' : 'border-[#374151] focus:border-blue-500'}
                  `}
                  aria-required="true"
                  aria-invalid={!!errors.path}
                  aria-describedby="path-hint path-error"
                  data-testid="input-path"
                />
                <p id="path-hint" className="mt-1 text-xs text-[#4B5563]">
                  절대 경로여야 합니다 (/ 또는 드라이브 문자로 시작)
                </p>
                {errors.path && (
                  <p id="path-error" role="alert" className="mt-1 text-xs text-red-400">
                    {errors.path}
                  </p>
                )}
              </div>
            )}

            {/* 서버 에러 배너 */}
            {errors.server && (
              <div
                role="alert"
                aria-live="polite"
                className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400"
              >
                {errors.server}
              </div>
            )}
          </div>

          {/* 푸터 버튼 */}
          <div className="flex justify-end gap-2 px-6 py-4 border-t border-[#374151]">
            <button
              type="button"
              onClick={() => !isSubmitting && onOpenChange(false)}
              disabled={isSubmitting}
              className={`
                px-4 py-2 text-sm font-medium rounded-lg
                text-[#9CA3AF] hover:text-[#F9FAFB]
                bg-[#1F2937] hover:bg-[#374151]
                border border-[#374151]
                transition-colors duration-150
                disabled:opacity-50 disabled:cursor-not-allowed
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
              `}
              data-testid="dialog-cancel-button"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={`
                inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg
                text-white bg-blue-600 hover:bg-blue-500
                transition-colors duration-150
                disabled:opacity-50 disabled:cursor-not-allowed
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
              `}
              data-testid="dialog-submit-button"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  추가 중...
                </>
              ) : (
                '프로젝트 추가'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
