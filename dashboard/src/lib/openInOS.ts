/**
 * @file lib/openInOS.ts
 * @description OS 기본 파일 탐색기/연결 프로그램으로 경로(폴더 또는 파일)를 여는 헬퍼.
 *
 * - WSL: wslpath -w로 Windows 경로 변환 후 explorer.exe (파일이면 연결 프로그램이 자동 실행)
 * - macOS: open
 * - Linux: xdg-open
 * - Windows (네이티브 Node): explorer.exe
 *
 * 보안: 호출 측에서 path traversal 검증을 한 뒤 호출해야 한다. 이 모듈은 검증하지 않는다.
 */

import { execSync, spawn } from 'child_process'
import fs from 'fs'

/** WSL 환경 감지 — /proc/version에 'microsoft' 또는 'WSL'이 있으면 WSL */
export function isWSL(): boolean {
  if (process.platform !== 'linux') return false
  try {
    const v = fs.readFileSync('/proc/version', 'utf-8').toLowerCase()
    return v.includes('microsoft') || v.includes('wsl')
  } catch {
    return false
  }
}

/** Windows 드라이브 문자로 시작하는 경로인지 (예: 'C:/...', 'C:\\...') */
function isWindowsPath(p: string): boolean {
  return /^[a-zA-Z]:[\\/]/.test(p)
}

/**
 * WSL에서 Linux 경로를 Windows(또는 \\wsl.localhost\\...) 경로로 변환한다.
 * 변환 실패 또는 이미 Windows 경로면 원본 반환.
 */
function toWindowsPath(p: string): string {
  if (isWindowsPath(p)) return p
  try {
    return execSync(`wslpath -w ${JSON.stringify(p)}`, { encoding: 'utf-8' }).trim() || p
  } catch {
    return p
  }
}

/**
 * 주어진 경로를 OS 파일 탐색기/연결 프로그램으로 연다.
 * 폴더면 탐색기, 파일이면 OS 기본 연결 프로그램이 실행된다.
 *
 * spawn은 detached + unref로 응답 흐름을 막지 않는다.
 */
export function openInOS(targetPath: string): { ok: true } | { ok: false; error: string } {
  try {
    let cmd: string
    let args: string[]

    if (isWSL()) {
      cmd = 'explorer.exe'
      args = [toWindowsPath(targetPath)]
    } else if (process.platform === 'darwin') {
      cmd = 'open'
      args = [targetPath]
    } else if (process.platform === 'win32') {
      cmd = 'explorer.exe'
      args = [targetPath]
    } else {
      cmd = 'xdg-open'
      args = [targetPath]
    }

    const child = spawn(cmd, args, { detached: true, stdio: 'ignore' })
    child.unref()
    return { ok: true }
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) }
  }
}
