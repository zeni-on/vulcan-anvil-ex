import type { ProductSessionData, ProductState } from '../../lib/types'

export const PRODUCT_STATES = ['planning', 'impl', 'acceptance', 'completed'] as const
// Synthetic persisted display states, not authority/evidence validation fixtures.
export function productSession(state: ProductState = 'planning'): ProductSessionData {
  const current = PRODUCT_STATES.indexOf(state)
  return {
    process_model: 'product-iterative-v1', profile: 'product', current_gate: state,
    gate_status: {
      planning: current > 0 ? 'done' : 'in-progress',
      impl: current > 1 ? 'done' : current === 1 ? 'in-progress' : 'pending',
      acceptance: current > 2 ? 'done' : current === 2 ? 'in-progress' : 'pending',
    },
    current_work: {
      scope: { work: { ref: 'docs/work.md#request', revision: 'sha256:' + 'b'.repeat(64) }, related_ids: ['REQ-001', 'SEC-001'], contracts: [], tests: [], required_checks: [] },
      // Computed with Python product_process.scope_key; no approval/evidence is implied.
      scope_key: 'f62c6809f032d61b250e67c1cf129d6d76fb29528115a4e1c09caa52e44a3e1d', decisions: [],
    },
    work_history: [],
  }
}

// Mirrors new Product init's empty scope using a synthetic revision.
export function newProductSession(): ProductSessionData {
  const session = productSession()
  session.current_work.scope.work.ref = 'docs/product/PRODUCT_BRIEF.md'
  session.current_work.scope.related_ids = []
  // Computed with Python product_process.scope_key for this empty scope.
  session.current_work.scope_key = 'c3b7e03a3f3f9c421616adeaed5027f2d4a457f28646cd79aa04092ad50b7bf4'
  return session
}

export function invalidProductSessions(): [string, unknown][] {
  const base = productSession()
  return [
    ['unknown model', { ...base, process_model: 'future-v2' }],
    ['null marker', { ...base, process_model: null }],
    ['wrong profile', { ...base, profile: 'audit' }],
    ['legacy stage', { ...base, current_gate: 'gate1' }],
    ['conflicting status', { ...base, current_gate: 'completed' }],
    ['old gate key', { ...base, gate_status: { ...base.gate_status, gate1: 'done' } }],
    ['old status', { ...base, gate_status: { ...base.gate_status, planning: 'blocked' } }],
    ['missing work', { ...base, current_work: undefined }],
    ['invalid revision', { ...base, current_work: { ...base.current_work, scope: { ...base.current_work.scope, work: { ref: 'docs/work.md', revision: 12 } } } }],
    ['invalid history', { ...base, work_history: {} }],
  ]
}
