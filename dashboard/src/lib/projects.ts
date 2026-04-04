/**
 * @file projects.ts
 * @description projects.json 읽기/쓰기 모듈
 *
 * 역할:
 * - dashboard/ 실행 기준 projects.json 파일 읽기/쓰기
 * - Zod 스키마로 개별 항목 검증, 스키마 오류 항목 제외 후 경고 로그 출력 (REQ-009-06)
 * - Atomic Write: tmp 파일에 먼저 쓴 뒤 rename으로 교체 (파일 손상 방지)
 *
 * 에러 처리:
 * - 파일 부재 또는 JSON 파싱 실패 시 빈 배열 반환 (UT-001-02)
 * - 스키마 오류 항목은 제외하고 정상 항목만 반환 (UT-001-03)
 *
 * @see docs/02-design/req-001-004-design.md §projects.json 스키마 모듈
 */

import fs from 'fs'
import path from 'path'
import { Project } from './types'
import { ProjectSchema } from './schemas'

/** projects.json 저장 경로 — dashboard/ 실행 기준 */
const PROJECTS_FILE = path.join(process.cwd(), 'projects.json')
const PROJECTS_FILE_TMP = path.join(process.cwd(), 'projects.json.tmp')

/**
 * projects.json을 읽어 Project 배열을 반환한다.
 *
 * - 파일 부재 → 빈 배열 반환 (UT-001-02)
 * - JSON 파싱 실패 → 빈 배열 반환
 * - 스키마 오류 항목 → 제외 후 경고 로그 출력, 정상 항목만 반환 (UT-001-03)
 */
export function readProjects(): Project[] {
  if (!fs.existsSync(PROJECTS_FILE)) {
    return []
  }

  let raw: string
  try {
    raw = fs.readFileSync(PROJECTS_FILE, 'utf-8')
  } catch (err) {
    console.warn('[projects] projects.json 읽기 실패:', err)
    return []
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch (err) {
    console.warn('[projects] projects.json JSON 파싱 실패:', err)
    return []
  }

  if (!Array.isArray(parsed)) {
    console.warn('[projects] projects.json 최상위 구조가 배열이 아닙니다.')
    return []
  }

  // 개별 항목 Zod 검증 — 오류 항목 제외 (REQ-009-06)
  const validProjects: Project[] = []
  for (const item of parsed) {
    const result = ProjectSchema.safeParse(item)
    if (result.success) {
      validProjects.push(result.data as Project)
    } else {
      console.warn(
        `[projects] 스키마 오류로 항목 제외 (id: ${(item as Record<string, unknown>)?.id ?? '?'}):`,
        result.error.message
      )
    }
  }

  return validProjects
}

/**
 * Project 배열을 projects.json에 Atomic Write로 저장한다.
 *
 * Atomic Write 전략:
 * 1. projects.json.tmp에 먼저 쓰기
 * 2. fs.renameSync으로 교체 — 쓰기 도중 크래시로 인한 파일 손상 방지
 */
export function writeProjects(projects: Project[]): void {
  const content = JSON.stringify(projects, null, 2)
  fs.writeFileSync(PROJECTS_FILE_TMP, content, 'utf-8')
  fs.renameSync(PROJECTS_FILE_TMP, PROJECTS_FILE)
}
