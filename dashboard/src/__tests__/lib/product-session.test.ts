import fs from 'fs'
import path from 'path'
import { SessionDataSchema } from '../../lib/schemas'
import { LocalDataSource } from '../../lib/datasource/local'
import { GitHubDataSource } from '../../lib/datasource/github'
import { PRODUCT_STATES, productSession, newProductSession, invalidProductSessions } from '../fixtures/productSession'
import { BASE_SESSION } from '../e2e/fixture'

let root: string
beforeEach(() => {
  fs.mkdirSync(path.resolve('test-results'), { recursive: true })
  root = fs.mkdtempSync(path.resolve('test-results/product-unit-'))
})
afterEach(() => { jest.restoreAllMocks(); fs.rmSync(root, { recursive: true, force: true }) })

function sources(value: unknown) {
  fs.writeFileSync(path.join(root, 'session.json'), JSON.stringify(value))
  jest.spyOn(global, 'fetch').mockResolvedValue({ ok: true, json: async () => ({ encoding: 'base64', content: Buffer.from(JSON.stringify(value)).toString('base64') }) } as Response)
  return [new LocalDataSource({ path: root }), new GitHubDataSource({ repo: 'synthetic/pilot', branch: 'test', token: 'test' })]
}

test.each(PRODUCT_STATES)('minimal %s survives both loaders without legacy metadata', async state => {
  const value = productSession(state)
  expect(SessionDataSchema.parse(value)).toEqual(value)
  for (const source of sources(value)) expect(await source.getSession()).toEqual(value)
  expect(fs.readFileSync(path.join(root, 'session.json'), 'utf8')).toBe(JSON.stringify(value))
})

test('new Product init shape survives both loaders unchanged', async () => {
  const value = newProductSession()
  expect(SessionDataSchema.parse(value)).toEqual(value)
  for (const source of sources(value)) expect(await source.getSession()).toEqual(value)
  expect(fs.readFileSync(path.join(root, 'session.json'), 'utf8')).toBe(JSON.stringify(value))
})

test.each(['product', 'audit', 'poc'])('unmarked %s stays legacy in both loaders', async profile => {
  const value = { ...BASE_SESSION, profile }
  for (const source of sources(value)) expect(await source.getSession()).toEqual(value)
})

test.each(invalidProductSessions())('%s is rejected by both loaders', async (_label, value) => {
  expect(SessionDataSchema.safeParse(value).success).toBe(false)
  for (const source of sources(value)) await expect(source.getSession()).rejects.toThrow('Unsupported or malformed')
})

test('unknown marker cannot fall through even with complete legacy metadata', () => {
  const legacy = { project: 'Legacy', vulcan_version: '1', current_gate: 'impl', gate_status: { gate1: 'done', gate2: 'done', gate3: 'done', impl: 'in-progress', gate4: 'pending', gate5: 'pending' }, started: '2026-09-11', completed: [], pending: [], blocked: [] }
  expect(SessionDataSchema.parse(legacy)).toEqual(legacy)
  expect(SessionDataSchema.safeParse({ ...legacy, process_model: 'future-v2' }).success).toBe(false)
})
