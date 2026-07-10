import fs from 'node:fs'
import path from 'node:path'

export class UnsafePathError extends Error {
  constructor(targetPath: string) {
    super(`Path escapes the allowed root: ${targetPath}`)
    this.name = 'UnsafePathError'
  }
}

function canonicalPath(targetPath: string): string {
  const resolved = path.resolve(targetPath)
  let existing = resolved
  const missingSegments: string[] = []
  while (!fs.existsSync(existing)) {
    const parent = path.dirname(existing)
    if (parent === existing) return resolved
    missingSegments.unshift(path.basename(existing))
    existing = parent
  }
  return path.join(fs.realpathSync.native(existing), ...missingSegments)
}

export function isPathInside(rootPath: string, targetPath: string): boolean {
  const root = canonicalPath(rootPath)
  const target = canonicalPath(targetPath)
  const relative = path.relative(root, target)
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative))
}

export function assertPathInside(rootPath: string, targetPath: string): string {
  const resolved = path.resolve(targetPath)
  if (!isPathInside(rootPath, resolved)) {
    throw new UnsafePathError(targetPath)
  }
  return resolved
}

export function configuredProjectRoots(): string[] {
  const configured = process.env.VULCAN_DASHBOARD_ALLOWED_ROOTS?.trim()
  if (!configured) return []
  return configured
    .split(path.delimiter)
    .map((entry) => entry.trim())
    .filter(Boolean)
    .map((entry) => path.resolve(entry))
}

export function isAllowedProjectPath(projectPath: string): boolean {
  const roots = configuredProjectRoots()
  return roots.length === 0 || roots.some((root) => isPathInside(root, projectPath))
}
