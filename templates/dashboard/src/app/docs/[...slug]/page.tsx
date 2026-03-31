import { readDoc } from '@/lib/project'
import DocViewer from '@/components/DocViewer'
import { notFound } from 'next/navigation'
import ExportButton from '@/components/ExportButton'

export const dynamic = 'force-dynamic'

interface Props {
  params: Promise<{ slug: string[] }>
}

export default async function DocPage({ params }: Props) {
  const { slug } = await params
  const content = readDoc(slug)
  if (!content) notFound()

  const title = slug[slug.length - 1].replace('.md', '')

  return (
    <main className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6 no-print">
        <h1 className="text-lg font-semibold text-gray-300">{title}</h1>
        <ExportButton />
      </div>
      <DocViewer content={content} />
    </main>
  )
}
