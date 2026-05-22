'use client'

/**
 * @file components/DocDrawer.tsx
 * @description 선택된 .md 파일을 오른쪽 슬라이드 패널에서 렌더링하는 Drawer (REQ-010)
 *
 * - 오른쪽에서 슬라이드인 애니메이션 (REQ-010-02)
 * - ESC 키, X 버튼, 배경 클릭으로 닫기 (REQ-010-04)
 * - react-markdown + remark-gfm + rehype-sanitize로 Markdown 렌더링 (REQ-010-03)
 *
 * @see docs/02-design/req-010-design.md §DocDrawer 컴포넌트
 * @see docs/02-design/ui-design.md §DocDrawer (REQ-010)
 */

import { Children, isValidElement, useEffect, useRef, useState, type ReactNode } from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize'
import { X, AlertCircle, ChevronDown, Maximize2, Minimize2 } from 'lucide-react'
import { DocNode } from '@/lib/types'
import { useDocContent } from '@/hooks/useDocContent'
import { isScreenSpecDoc, parseScreenSpecDoc } from '@/lib/screenSpecDoc'
import { isTraceabilityDoc, parseTraceabilityDoc } from '@/lib/traceabilityDoc'
import MermaidBlock from './MermaidBlock'
import ScreenSpecDocView from './ScreenSpecDocView'
import TraceabilityDocView from './TraceabilityDocView'

// rehype-sanitize 기본 스키마는 <code>의 className을 제거한다. mermaid 코드 블록을
// 식별하려면 language-* 클래스가 보존되어야 하므로 code의 className을 허용한다.
const sanitizeSchema = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    code: [...(defaultSchema.attributes?.code ?? []), ['className']],
  },
}

/**
 * react-markdown v10에서 code 블록의 children은 텍스트 노드의 React 트리일 수 있다.
 * `String(children)`은 객체에 대해 "[object Object]"가 되어 mermaid 파서가 깨지므로
 * 자식 트리를 재귀적으로 순회해 순수 텍스트만 모은다.
 */
function extractText(node: ReactNode): string {
  if (node == null || node === false || node === true) return ''
  if (typeof node === 'string') return node
  if (typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(extractText).join('')
  if (isValidElement(node)) {
    const children = (node.props as { children?: ReactNode }).children
    return Children.toArray(children).map(extractText).join('')
  }
  return ''
}

interface DocumentMetadata {
  title?: string
  titleKo?: string
  project?: string
  status?: string
  updatedAt?: string
  runId?: string
  gate?: string
  persona?: string
  skill?: string
  createdAt?: string
}

function parseMetadataBlock(block: string): DocumentMetadata {
  const metadata: DocumentMetadata = {}
  for (const line of block.split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z_]+):\s*(.+)$/)
    if (!match) continue
    const [, key, value] = match
    const cleanValue = value.trim()
    if (key === 'title') metadata.title = cleanValue
    else if (key === 'title_ko') metadata.titleKo = cleanValue
    else if (key === 'project') metadata.project = cleanValue
    else if (key === 'status') metadata.status = cleanValue
    else if (key === 'updated_at') metadata.updatedAt = cleanValue
    else if (key === 'run_id') metadata.runId = cleanValue
    else if (key === 'gate') metadata.gate = cleanValue
    else if (key === 'persona') metadata.persona = cleanValue
    else if (key === 'skill') metadata.skill = cleanValue
    else if (key === 'created_at') metadata.createdAt = cleanValue
  }
  return metadata
}

function splitDocumentMetadata(content: string): { metadata: DocumentMetadata; body: string; raw?: string } {
  const frontMatterMatch = content.match(/```ya?ml\s*\n---\s*\n([\s\S]*?)\n---\s*\n```/i)
  if (frontMatterMatch) {
    return {
      metadata: parseMetadataBlock(frontMatterMatch[1]),
      body: content.replace(frontMatterMatch[0], '').trimStart(),
      raw: frontMatterMatch[1].trim(),
    }
  }

  const yamlMatch = content.match(/```ya?ml\s*\n([\s\S]*?)\n```/i)
  if (!yamlMatch || yamlMatch.index == null || yamlMatch.index > 240) {
    return { metadata: {}, body: content }
  }

  const rawYaml = yamlMatch[1].trim()
  const looksLikeRunMetadata = /^(run_id|adapter|gate|persona|skill|status|created_at):/m.test(rawYaml)
  if (!looksLikeRunMetadata) return { metadata: {}, body: content }

  return {
    metadata: parseMetadataBlock(rawYaml),
    body: content.replace(yamlMatch[0], '').trimStart(),
    raw: rawYaml,
  }
}

// react-markdown의 code 렌더러를 가로채 ```mermaid 블록을 SVG로 변환한다.
const markdownComponents: Components = {
  code(props) {
    const { className, children, ...rest } = props
    if (className?.includes('language-mermaid')) {
      const text = extractText(children).replace(/\n$/, '')
      return <MermaidBlock code={text} />
    }
    return (
      <code className={className} {...rest}>
        {children}
      </code>
    )
  },
}

interface DocDrawerProps {
  projectId: string
  doc: DocNode | null
  onClose: () => void
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-3 p-6" aria-busy="true" aria-label="문서 불러오는 중">
      <div className="h-6 bg-zinc-700 rounded w-3/4" />
      <div className="h-4 bg-zinc-700 rounded w-full" />
      <div className="h-4 bg-zinc-700 rounded w-5/6" />
      <div className="h-4 bg-zinc-700 rounded w-4/5" />
      <div className="mt-4 h-4 bg-zinc-700 rounded w-full" />
      <div className="h-4 bg-zinc-700 rounded w-3/4" />
    </div>
  )
}

function DrawerContent({ projectId, doc }: { projectId: string; doc: DocNode }) {
  const { content, isLoading, error } = useDocContent(projectId, doc)
  const [showMetadata, setShowMetadata] = useState(false)
  const genericDoc = splitDocumentMetadata(content ?? '')
  const hasMetadataHeader =
    genericDoc.metadata.titleKo ||
    genericDoc.metadata.title ||
    genericDoc.metadata.runId ||
    genericDoc.raw

  if (isLoading) return <LoadingSkeleton />

  if (error) {
    return (
      <div
        role="alert"
        className="m-6 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400"
      >
        <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
        문서를 불러올 수 없습니다.
      </div>
    )
  }

  return (
    <div
      // tabIndex로 스크롤 컨테이너에 포커스 가능 → PageUp/PageDown이 이 영역을 스크롤
      tabIndex={0}
      data-drawer-scroll
      className="p-6 overflow-y-auto flex-1 focus:outline-none"
    >
      {content && isTraceabilityDoc(doc, content) ? (
        <TraceabilityDocView model={parseTraceabilityDoc(content)} />
      ) : content && isScreenSpecDoc(doc, content) ? (
        <ScreenSpecDocView model={parseScreenSpecDoc(content)} projectId={projectId} />
      ) : (
        <div className="rounded-md bg-slate-100 p-4 text-slate-800">
          {hasMetadataHeader && (
            <header className="mb-4 rounded-md border border-blue-200 bg-gradient-to-r from-blue-50 to-white p-4 shadow-sm">
              <div className="text-xs font-medium text-blue-700">
                {genericDoc.metadata.title ?? genericDoc.metadata.runId ?? 'Document'}
              </div>
              <h2 className="mt-1 text-lg font-semibold text-slate-950">
                {genericDoc.metadata.titleKo ?? genericDoc.metadata.title ?? doc.name}
              </h2>
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">
                {genericDoc.metadata.project && <span>프로젝트: {genericDoc.metadata.project}</span>}
                {genericDoc.metadata.gate && <span>Gate: {genericDoc.metadata.gate}</span>}
                {genericDoc.metadata.persona && <span>Persona: {genericDoc.metadata.persona}</span>}
                {genericDoc.metadata.skill && <span>Skill: {genericDoc.metadata.skill}</span>}
                {genericDoc.metadata.status && <span>상태: {genericDoc.metadata.status}</span>}
                {(genericDoc.metadata.updatedAt || genericDoc.metadata.createdAt) && (
                  <span>일자: {genericDoc.metadata.updatedAt ?? genericDoc.metadata.createdAt}</span>
                )}
              </div>
              {genericDoc.raw && (
                <div className="mt-3">
                  <button
                    type="button"
                    onClick={() => setShowMetadata((value) => !value)}
                    className="inline-flex items-center gap-1 rounded border border-blue-200 bg-white px-2 py-1 text-xs font-medium text-blue-700 hover:bg-blue-50"
                    aria-expanded={showMetadata}
                  >
                    <ChevronDown
                      className={`h-3 w-3 transition-transform ${showMetadata ? 'rotate-180' : ''}`}
                      aria-hidden="true"
                    />
                    메타데이터 보기
                  </button>
                  {showMetadata && (
                    <pre className="mt-2 overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
                      <code>{genericDoc.raw}</code>
                    </pre>
                  )}
                </div>
              )}
            </header>
          )}
          <div className="prose prose-slate prose-sm max-w-none rounded-md bg-white p-5 shadow-sm
            prose-headings:text-slate-950
            prose-h1:border-b prose-h1:border-slate-200 prose-h1:pb-3
            prose-h2:mt-8 prose-h2:border-l-4 prose-h2:border-blue-500 prose-h2:pl-2
            prose-p:text-slate-700
            prose-a:text-blue-700 prose-a:no-underline hover:prose-a:underline
            prose-code:bg-slate-100 prose-code:text-slate-900 prose-code:px-1 prose-code:rounded prose-code:text-xs
            prose-pre:bg-slate-50 prose-pre:border prose-pre:border-slate-200 prose-pre:text-slate-800
            prose-blockquote:border-blue-300 prose-blockquote:bg-blue-50 prose-blockquote:px-3 prose-blockquote:py-1 prose-blockquote:text-slate-700
            prose-th:text-blue-950 prose-td:text-slate-700
            prose-hr:border-slate-200
            prose-strong:text-slate-950
            prose-li:text-slate-700
            prose-table:w-full prose-table:table-auto
            prose-th:break-words prose-td:break-words prose-td:align-top
            [&_table]:w-full [&_table]:border-collapse [&_table]:overflow-hidden [&_table]:rounded-md
            [&_td]:border [&_td]:border-slate-200 [&_td]:px-2 [&_td]:py-1.5 [&_td]:align-top [&_td]:text-xs [&_td]:break-words
            [&_th]:border [&_th]:border-blue-300 [&_th]:bg-blue-100 [&_th]:px-2 [&_th]:py-1.5 [&_th]:text-xs [&_th]:font-semibold
            [&_tbody_tr:nth-child(even)]:bg-slate-50">
            <ReactMarkdown
              remarkPlugins={[[remarkGfm, { singleTilde: false }]]}
              rehypePlugins={[[rehypeSanitize, sanitizeSchema]]}
              components={markdownComponents}
            >
              {genericDoc.body}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * 슬라이드 사이드 패널 Drawer.
 * doc이 null이면 화면 밖으로 숨겨진다 (translate-x-full).
 */
/** Drawer 안의 tabbable 요소를 DOM 순서대로 모은다. */
function getFocusable(container: HTMLElement): HTMLElement[] {
  const selector =
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  return Array.from(container.querySelectorAll<HTMLElement>(selector)).filter(
    (el) => !el.hasAttribute('aria-hidden') && el.offsetParent !== null,
  )
}

export default function DocDrawer({ projectId, doc, onClose }: DocDrawerProps) {
  const closeBtnRef = useRef<HTMLButtonElement>(null)
  const dialogRef = useRef<HTMLDivElement>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  // Drawer가 열릴 때 직전 포커스를 저장 → 닫힐 때 복원하기 위함
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const isOpen = doc !== null

  useEffect(() => {
    if (!isOpen) setIsExpanded(false)
  }, [isOpen])

  // ESC 닫기 + Tab 포커스 트랩 + PageUp/Down 스크롤 위임
  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
        return
      }

      // PageUp/PageDown/Home/End: drawer 밖으로 스크롤이 새거나 포커스가 빠지는
      // 브라우저 기본 동작을 막고, 직접 drawer 스크롤 영역만 스크롤한다.
      if (
        e.key === 'PageUp' ||
        e.key === 'PageDown' ||
        e.key === 'Home' ||
        e.key === 'End'
      ) {
        const scrollArea = dialogRef.current?.querySelector<HTMLElement>(
          '[data-drawer-scroll]',
        )
        if (!scrollArea) return
        // 포커스가 drawer 밖에 있으면 무시 (다른 곳에서 PageDown 사용 가능하게)
        if (!dialogRef.current?.contains(document.activeElement)) return

        e.preventDefault()
        // 페이지당 스크롤 양: 컨테이너 높이의 90%
        const page = scrollArea.clientHeight * 0.9
        if (e.key === 'PageDown') scrollArea.scrollBy({ top: page, behavior: 'auto' })
        else if (e.key === 'PageUp') scrollArea.scrollBy({ top: -page, behavior: 'auto' })
        else if (e.key === 'Home') scrollArea.scrollTo({ top: 0, behavior: 'auto' })
        else if (e.key === 'End') scrollArea.scrollTo({ top: scrollArea.scrollHeight, behavior: 'auto' })

        // 포커스가 스크롤 영역에 머무르도록 보장
        if (document.activeElement !== scrollArea) scrollArea.focus()
        return
      }

      if (e.key !== 'Tab' || !dialogRef.current) return

      const focusables = getFocusable(dialogRef.current)
      if (focusables.length === 0) {
        e.preventDefault()
        return
      }
      const first = focusables[0]
      const last = focusables[focusables.length - 1]
      const active = document.activeElement as HTMLElement | null

      if (e.shiftKey) {
        if (active === first || !dialogRef.current.contains(active)) {
          e.preventDefault()
          last.focus()
        }
      } else {
        if (active === last || !dialogRef.current.contains(active)) {
          e.preventDefault()
          first.focus()
        }
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Drawer 열릴 때: 직전 포커스 저장 + 콘텐츠 스크롤 영역에 포커스
  // (X 버튼 대신 스크롤 영역에 포커스 → PageUp/PageDown이 자연스럽게 본문을 스크롤)
  // 닫힐 때(effect cleanup): 저장해둔 요소에 포커스 복원
  useEffect(() => {
    if (!isOpen) return

    previousFocusRef.current = (document.activeElement as HTMLElement) ?? null

    // 콘텐츠 영역은 비동기 로딩이라 다음 프레임에 시도, 없으면 X 버튼 폴백
    requestAnimationFrame(() => {
      const scrollArea =
        dialogRef.current?.querySelector<HTMLElement>('[data-drawer-scroll]')
      if (scrollArea) scrollArea.focus()
      else closeBtnRef.current?.focus()
    })

    return () => {
      const prev = previousFocusRef.current
      previousFocusRef.current = null
      if (prev && typeof prev.focus === 'function' && document.contains(prev)) {
        // 슬라이드 애니메이션과 충돌하지 않도록 다음 프레임에 복원
        requestAnimationFrame(() => prev.focus())
      }
    }
  }, [isOpen])

  // 콘텐츠가 늦게 로드되는 경우(스켈레톤 → 실제 콘텐츠)에도 스크롤 영역에 포커스가 가도록
  useEffect(() => {
    if (!isOpen) return
    const id = requestAnimationFrame(() => {
      const scrollArea =
        dialogRef.current?.querySelector<HTMLElement>('[data-drawer-scroll]')
      if (scrollArea && !dialogRef.current?.contains(document.activeElement)) {
        scrollArea.focus()
      }
    })
    return () => cancelAnimationFrame(id)
  }, [isOpen, doc])

  return (
    <>
      {/* 배경 오버레이 */}
      <div
        className={`fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* 사이드 패널 */}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label={doc?.name ?? '문서 뷰어'}
        className={`fixed right-0 top-0 h-full max-w-none z-50 flex flex-col
          bg-zinc-900 border-l border-zinc-700
          transition-transform duration-300 ease-out
          ${isExpanded ? 'w-[92vw] min-w-0' : 'w-[60vw] min-w-[480px]'}
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-700 bg-zinc-800 flex-shrink-0">
          <h2 className="text-sm font-semibold text-zinc-100 truncate pr-4 font-mono">
            {doc?.name ?? ''}
          </h2>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setIsExpanded((value) => !value)}
              aria-label={isExpanded ? '기본 폭으로 보기' : '넓게 보기'}
              title={isExpanded ? '기본 폭으로 보기' : '넓게 보기'}
              className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-700 transition-colors flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            >
              {isExpanded ? (
                <Minimize2 className="w-4 h-4" aria-hidden="true" />
              ) : (
                <Maximize2 className="w-4 h-4" aria-hidden="true" />
              )}
            </button>
            <button
              ref={closeBtnRef}
              onClick={onClose}
              aria-label="닫기"
              className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-700 transition-colors flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            >
              <X className="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        </div>

        {/* 콘텐츠 */}
        {doc && <DrawerContent projectId={projectId} doc={doc} />}
      </div>
    </>
  )
}
