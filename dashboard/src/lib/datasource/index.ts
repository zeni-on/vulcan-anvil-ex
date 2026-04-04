/**
 * @file datasource/index.ts
 * @description DataSource 팩토리 함수
 *
 * 역할:
 * - Project 객체를 받아 적절한 DataSource 구현체를 반환한다.
 * - API Route가 DataSource 구현체 선택 로직을 알 필요 없도록 캡슐화한다.
 * - GITHUB_TOKEN은 이 팩토리에서 process.env에서 읽어 GitHubDataSource에 주입한다.
 *   절대 클라이언트에 전달하지 않는다 (REQ-009-02).
 *
 * UT-002-08: type='github' → GitHubDataSource 인스턴스 반환
 * UT-002-09: type='local' → LocalDataSource 인스턴스 반환
 *
 * @see docs/02-design/req-001-004-design.md §createDataSource()
 */

import { Project, DataSource, DataSourceError } from '../types'
import { GitHubDataSource } from './github'
import { LocalDataSource } from './local'

/**
 * Project 객체 기준으로 DataSource 구현체를 생성하여 반환한다.
 *
 * @param project - projects.json에서 읽은 Project 항목
 * @returns DataSource 구현체 (GitHubDataSource | LocalDataSource)
 * @throws DataSourceError GITHUB_TOKEN 미설정 시
 */
export function createDataSource(project: Project): DataSource {
  switch (project.type) {
    case 'github': {
      // GITHUB_TOKEN은 서버사이드 전용 환경변수 (NEXT_PUBLIC_ 접두사 금지)
      const token = process.env.GITHUB_TOKEN ?? ''
      return new GitHubDataSource({
        repo: project.repo,
        branch: project.branch,
        token,
      })
    }
    case 'local': {
      return new LocalDataSource({
        path: project.path,
      })
    }
    default: {
      // TypeScript exhaustive check
      const _exhaustive: never = project
      throw new DataSourceError(`알 수 없는 프로젝트 타입: ${(_exhaustive as Project).type}`)
    }
  }
}

// 구현체 타입 재내보내기 — API Route에서 instanceof 확인 시 사용
export { GitHubDataSource } from './github'
export { LocalDataSource } from './local'
