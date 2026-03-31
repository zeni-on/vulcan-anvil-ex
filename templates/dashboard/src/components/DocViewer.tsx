'use client'

import { marked } from 'marked'
import { useMemo } from 'react'

marked.setOptions({ gfm: true })

export default function DocViewer({ content }: { content: string }) {
  const html = useMemo(() => marked(content) as string, [content])

  return (
    <article
      className="prose prose-invert prose-sm max-w-none
        prose-headings:text-white
        prose-p:text-gray-300
        prose-li:text-gray-300
        prose-td:text-gray-300
        prose-th:text-gray-200
        prose-code:text-blue-300
        prose-pre:bg-gray-900
        prose-blockquote:border-gray-600
        prose-blockquote:text-gray-400
        prose-a:text-blue-400
        prose-strong:text-white
        prose-table:text-sm"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
