import { renderHook } from '@testing-library/react'
import useSWR from 'swr'
import { useProjectSession } from '../../hooks/useProjectSession'
import { productSession } from '../fixtures/productSession'

jest.mock('swr', () => ({ __esModule: true, default: jest.fn() }))

test('failed revalidation hides cached accepted scope', () => {
  jest.mocked(useSWR).mockReturnValue({ data: { session: productSession('completed') }, error: new Error('Unsupported or malformed process session') } as ReturnType<typeof useSWR>)
  expect(renderHook(() => useProjectSession('pilot')).result.current.session).toBeNull()
})

test('valid persisted session remains visible', () => {
  const session = productSession()
  jest.mocked(useSWR).mockReturnValue({ data: { session }, error: undefined } as ReturnType<typeof useSWR>)
  expect(renderHook(() => useProjectSession('pilot')).result.current.session).toEqual(session)
})
