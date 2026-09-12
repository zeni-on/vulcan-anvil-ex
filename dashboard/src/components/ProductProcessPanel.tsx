import type { ProductSessionData } from '@/lib/types'

export const PRODUCT_STAGE_LABELS = { planning: '기획·설계', impl: '구현', acceptance: '인수 검증', completed: '이번 범위 인수 완료' }
const STATUS_LABELS = { done: '완료', 'in-progress': '진행중', pending: '대기' }

export default function ProductProcessPanel({ session }: { session: ProductSessionData }) {
  const scope = session.current_work.scope
  const scopeEmpty = [scope.related_ids, scope.contracts, scope.tests, scope.required_checks].every(items => items.length === 0)
  const done = Object.values(session.gate_status).filter(status => status === 'done').length
  return (
    <section data-testid="product-process-panel" className="min-w-0 space-y-3 text-sm text-gray-200 [overflow-wrap:anywhere]">
      <p className="text-xs text-gray-400">Product · 읽기 전용 · 저장된 상태 · 증적 미검증</p>
      <h2 className="text-base font-semibold">{PRODUCT_STAGE_LABELS[session.current_gate]}</h2>
      <ol aria-label="Product 단계" className="grid grid-cols-3 gap-2">
        {(['planning', 'impl', 'acceptance'] as const).map(stage => (
          <li key={stage} aria-current={session.current_gate === stage ? 'step' : undefined} className="min-w-0 border-t-2 border-gray-600 pt-2">
            <span>{PRODUCT_STAGE_LABELS[stage]}</span>
            <span className={`block text-xs ${session.gate_status[stage] === 'done' ? 'text-green-400' : 'text-gray-400'}`}>{STATUS_LABELS[session.gate_status[stage]]}</span>
          </li>
        ))}
      </ol>
      <p className="text-xs text-gray-400">저장된 단계 완료: {done} / 3</p>
      <p className="text-amber-300">릴리즈 별도 승인 필요</p>
      {scopeEmpty && <p className="text-gray-400">아직 관련 ID, 계약, 테스트, 필수 검사가 등록되지 않았습니다.</p>}
      <dl className="space-y-2">
        <div><dt className="text-gray-400">현재 작업</dt><dd>{scope.work.ref}</dd></div>
        <div><dt className="text-gray-400">Revision</dt><dd className="font-mono text-xs">{scope.work.revision}</dd></div>
        <div><dt className="text-gray-400">관련 ID</dt><dd>{scope.related_ids.join(', ') || '없음'}</dd></div>
      </dl>
    </section>
  )
}
