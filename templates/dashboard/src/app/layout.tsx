import type { Metadata } from 'next'
import './globals.css'
import path from 'path'
import { readSession, buildDocTree, PROJECT_ROOT } from '@/lib/project'
import Sidebar from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'Anvil Dashboard',
  description: 'Vulcan-Claude-Anvil Project Dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const session = readSession()
  const docs = buildDocTree(path.join(PROJECT_ROOT, 'docs'))

  return (
    <html lang="ko">
      <body className="flex h-screen bg-gray-950 text-gray-100 overflow-hidden">
        <Sidebar session={session} docs={docs} />
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </body>
    </html>
  )
}
