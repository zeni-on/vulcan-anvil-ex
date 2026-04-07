'use client'

/**
 * @file components/MermaidBlock.tsx
 * @description ```mermaid 코드 블록을 SVG 다이어그램으로 렌더링하는 인라인 컴포넌트.
 *
 * `MermaidRenderer`와 달리, 이 컴포넌트는 react-markdown의 `components.code`에서
 * 직접 사용되어 동적으로 추가/교체되는 마크다운(예: DocDrawer)에서도 동작한다.
 */

import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

let initialized = false
function ensureInit() {
  if (initialized) return
  mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    darkMode: true,
    themeVariables: {
      background: '#111827',
      primaryColor: '#3b82f6',
      primaryTextColor: '#f3f4f6',
      primaryBorderColor: '#60a5fa',
      secondaryColor: '#374151',
      secondaryTextColor: '#f3f4f6',
      secondaryBorderColor: '#6b7280',
      tertiaryColor: '#1f2937',
      tertiaryTextColor: '#f3f4f6',
      tertiaryBorderColor: '#6b7280',
      lineColor: '#9ca3af',
      textColor: '#f3f4f6',
      edgeLabelBackground: '#1f2937',
      clusterBkg: '#1f2937',
      clusterBorder: '#6b7280',
      titleColor: '#f3f4f6',
      // 노트(분홍 배경) — 다크 테마에 맞게 어둡게 + 글자색 명시
      noteBkgColor: '#78350f',
      noteTextColor: '#fef3c7',
      noteBorderColor: '#f59e0b',
      // 시퀀스 다이어그램 actor/메시지 색상
      actorBkg: '#1e3a8a',
      actorBorder: '#60a5fa',
      actorTextColor: '#f3f4f6',
      actorLineColor: '#6b7280',
      signalColor: '#f3f4f6',
      signalTextColor: '#f3f4f6',
      labelBoxBkgColor: '#374151',
      labelBoxBorderColor: '#6b7280',
      labelTextColor: '#f3f4f6',
      loopTextColor: '#f3f4f6',
      activationBkgColor: '#374151',
      activationBorderColor: '#6b7280',
    },
  })
  initialized = true
}

interface MermaidBlockProps {
  code: string
}

/**
 * "rgb(r,g,b)" 또는 "#rgb" / "#rrggbb" 색 문자열을 [r,g,b]로 파싱한다.
 * 파싱 실패 시 null.
 */
function parseColor(input: string): [number, number, number] | null {
  const s = input.trim().toLowerCase()
  if (s.startsWith('#')) {
    const hex = s.slice(1)
    if (hex.length === 3) {
      const r = parseInt(hex[0] + hex[0], 16)
      const g = parseInt(hex[1] + hex[1], 16)
      const b = parseInt(hex[2] + hex[2], 16)
      return [r, g, b]
    }
    if (hex.length === 6) {
      return [
        parseInt(hex.slice(0, 2), 16),
        parseInt(hex.slice(2, 4), 16),
        parseInt(hex.slice(4, 6), 16),
      ]
    }
    return null
  }
  const m = s.match(/^rgba?\(([^)]+)\)$/)
  if (m) {
    const parts = m[1].split(',').map((p) => parseFloat(p))
    if (parts.length >= 3) return [parts[0], parts[1], parts[2]]
  }
  return null
}

/** sRGB 상대 휘도 (0~1). 0.6 이상이면 충분히 밝음. */
function luminance(r: number, g: number, b: number): number {
  const channel = (c: number) => {
    const v = c / 255
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  }
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
}

/**
 * 렌더된 SVG를 순회하며 `.node` 안의 도형 fill이 밝은 색이면
 * 같은 노드 안의 텍스트를 어둡게 강제한다.
 * 다이어그램 작성자가 라이트 테마 가정으로 인라인 fill을 박아둔 경우에 가독성을 회복한다.
 */
function fixLightNodes(container: HTMLElement) {
  const nodes = container.querySelectorAll<SVGGElement>('g.node, g.cluster')
  nodes.forEach((node) => {
    // 노드의 배경 도형
    const shape = node.querySelector<SVGGraphicsElement>('rect, polygon, circle, ellipse, path')
    if (!shape) return
    const fill =
      shape.getAttribute('fill') ||
      shape.style.fill ||
      window.getComputedStyle(shape).fill
    if (!fill || fill === 'none') return
    const rgb = parseColor(fill)
    if (!rgb) return
    if (luminance(rgb[0], rgb[1], rgb[2]) < 0.6) return
    // 밝은 배경 — 텍스트 색을 어둡게
    node.querySelectorAll<SVGElement>('text, tspan, .nodeLabel, foreignObject *').forEach((t) => {
      t.style.fill = '#111827'
      t.style.color = '#111827'
    })
  })
}

export default function MermaidBlock({ code }: MermaidBlockProps) {
  const [error, setError] = useState<string | null>(null)
  const [rendered, setRendered] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const idRef = useRef(`mermaid-${Math.random().toString(36).slice(2, 9)}`)

  useEffect(() => {
    let cancelled = false
    ensureInit()
    ;(async () => {
      try {
        const { svg } = await mermaid.render(idRef.current, code)
        if (cancelled || !containerRef.current) return
        containerRef.current.innerHTML = svg
        fixLightNodes(containerRef.current)
        setRendered(true)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [code])

  if (error) {
    return (
      <pre className="my-4 overflow-x-auto rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300">
        <code>mermaid 렌더 실패: {error}{'\n\n'}{code}</code>
      </pre>
    )
  }

  return (
    <>
      {!rendered && (
        <pre className="my-4 overflow-x-auto rounded-lg bg-zinc-900 p-3 text-xs text-zinc-400">
          <code>{code}</code>
        </pre>
      )}
      <div
        ref={containerRef}
        className={`my-6 flex justify-center overflow-x-auto rounded-lg bg-gray-900 p-4 ${
          rendered ? '' : 'hidden'
        }`}
      />
    </>
  )
}
