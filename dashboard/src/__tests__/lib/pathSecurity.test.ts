import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { assertPathInside, isAllowedProjectPath, isPathInside, UnsafePathError } from '@/lib/pathSecurity'

describe('pathSecurity', () => {
  let root: string
  const originalAllowedRoots = process.env.VULCAN_DASHBOARD_ALLOWED_ROOTS

  beforeEach(() => {
    root = fs.mkdtempSync(path.join(os.tmpdir(), 'vulcan-path-root-'))
  })

  afterEach(() => {
    fs.rmSync(root, { recursive: true, force: true })
    if (originalAllowedRoots === undefined) delete process.env.VULCAN_DASHBOARD_ALLOWED_ROOTS
    else process.env.VULCAN_DASHBOARD_ALLOWED_ROOTS = originalAllowedRoots
  })

  it('does not accept a sibling directory with the same prefix', () => {
    const sibling = `${root}-secrets`
    expect(isPathInside(root, sibling)).toBe(false)
    expect(() => assertPathInside(root, sibling)).toThrow(UnsafePathError)
  })

  it('resolves a symlinked parent even when the final file does not exist', () => {
    const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'vulcan-path-outside-'))
    const link = path.join(root, 'linked')
    try {
      fs.symlinkSync(outside, link, process.platform === 'win32' ? 'junction' : 'dir')
      expect(isPathInside(root, path.join(link, 'new-file.md'))).toBe(false)
    } finally {
      fs.rmSync(outside, { recursive: true, force: true })
    }
  })

  it('applies the configured project root allowlist', () => {
    process.env.VULCAN_DASHBOARD_ALLOWED_ROOTS = root
    expect(isAllowedProjectPath(path.join(root, 'project-a'))).toBe(true)
    expect(isAllowedProjectPath(`${root}-outside`)).toBe(false)
  })
})
