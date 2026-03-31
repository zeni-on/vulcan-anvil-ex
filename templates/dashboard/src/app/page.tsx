import { readSession } from '@/lib/project'
import GateProgress from '@/components/GateProgress'

export const dynamic = 'force-dynamic'

export default function Home() {
  const session = readSession()
  return (
    <main className="p-8 max-w-4xl">
      <GateProgress session={session} />
    </main>
  )
}
