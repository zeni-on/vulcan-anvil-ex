#!/usr/bin/env python3
"""
Vulcan-Anvil - 5-Gate AI 협업 개발 프레임워크 (Claude Code 네이티브 하네스)

대장장이 신 Vulcan처럼, 에이전트 팀을 단련하여 체계적으로 프로젝트를 완성합니다.
Agent-Forge의 5-Gate 프로세스를 Claude Code 네이티브 하네스(.claude/) 구조로 재구현.

명령어:
  init         새 프로젝트 초기화
  session      Gate 상태 업데이트 + git commit 자동 생성
  check-trace  Gate별 정합성 검사
  export       snapshot.json 생성 (대시보드용)
  upgrade      프레임워크 파일을 최신 버전으로 업데이트
  version      현재 프레임워크 버전 확인

사용법:
  # 초기화 (Vulcan-Anvil 디렉토리에서 실행)
  python vulcan.py init <target-dir> <project-name> [--agent-name NAME]

  # 이하 명령은 프로젝트 디렉토리에서 실행
  python vulcan.py check-trace
  python vulcan.py session --gate gate1 --status done --feature "로그인 기능"
  python vulcan.py export [--output snapshot.json]
  python vulcan.py upgrade
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
from datetime import date

# Windows 콘솔 UTF-8 출력 보장
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VULCAN_VERSION = "1.5.0"

VULCAN_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(VULCAN_DIR, "templates")
PROJECT_DOC_SETS = [
    "docs/core",
    "docs/templates",
    "docs/adapters",
    "docs/seed-docs",
]
PROJECT_DOC_DIRS = [
    "docs/runs",
    "docs/ref-docs",
]
PROJECT_ROOT_FILES = [
    "AGENTS.md",
]
RUN_SKILLS = {
    "traceability-review": "docs/adapters/codex-gpt/skills/traceability-review.md",
    "security-review": "docs/adapters/codex-gpt/skills/security-review.md",
    "data-standard-review": "docs/adapters/codex-gpt/skills/data-standard-review.md",
    "qa-fix-loop": "docs/adapters/codex-gpt/skills/qa-fix-loop.md",
    "change-impact-analysis": "docs/adapters/codex-gpt/skills/change-impact-analysis.md",
}
RUN_PERSONAS = {
    "discovery": "배경, 제약, 현행 자료, 질문, 위험을 정리한다.",
    "requirements": "요구사항, 비기능 요구사항, 인수기준을 정리한다.",
    "design": "기능, 화면, 프로그램, DB, 보안 설계를 작성한다.",
    "test-design": "AC, SEC, NREQ를 검증 가능한 테스트로 전개한다.",
    "build": "승인된 설계를 코드, 설정, 테스트 코드로 구현한다.",
    "evidence": "테스트 결과, 화면 캡처, 로그 등 증적을 만든다.",
    "review": "추적성, 보안, 품질, 설계 준수 여부를 검토한다.",
    "release": "승인 후보, 릴리즈 범위, 인수인계 항목을 정리한다.",
    "change-control": "변경요청 영향도와 재진입 Gate를 판단한다.",
    "documentation": "용어, 문서 버전, 산출물 일관성을 정리한다.",
}
RUN_SKILL_DEFAULT_PERSONAS = {
    "traceability-review": "review",
    "security-review": "review",
    "data-standard-review": "review",
    "qa-fix-loop": "build",
    "change-impact-analysis": "change-control",
}
RUN_REQUIRED_KEYS = [
    "run_id",
    "adapter",
    "persona",
    "status",
    "skill",
    "related_ids",
    "verification_results",
    "evidence",
    "traceability_updates",
    "open_issues",
]

GATE_LABELS = {
    "gate1": "Gate 1 요구사항",
    "gate2": "Gate 2 설계",
    "gate3": "Gate 3 테스트 플랜",
    "impl":  "구현",
    "gate4": "Gate 4 QA 검토",
    "gate5": "Gate 5 최종 승인",
}


# ── 공통 유틸 ──────────────────────────────────────────────────────────────

def render(text, variables):
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def read_template(rel_path):
    path = os.path.join(TEMPLATES_DIR, rel_path)
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_file(target_dir, rel_path, content):
    full_path = os.path.join(target_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  생성: {rel_path}")


def copy_file(target_dir, rel_path, src_rel_path=None):
    import shutil
    src = os.path.join(TEMPLATES_DIR, src_rel_path or rel_path)
    dst = os.path.join(target_dir, rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  생성: {rel_path}")


def copy_tree(src_dir, dst_dir):
    """디렉토리 트리를 재귀적으로 복사합니다."""
    import shutil
    for root, dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        for f in files:
            src = os.path.join(root, f)
            rel_path = os.path.join(rel_root, f) if rel_root != "." else f
            dst = os.path.join(dst_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def copy_source_tree(target_dir, rel_dir, variables=None, overwrite=True, source_root=None):
    """Copy a repository directory into the target project.

    Markdown and JSON files are rendered with project variables; binary files are copied as-is.
    """
    import shutil

    src_dir = os.path.join(source_root or VULCAN_DIR, rel_dir)
    if not os.path.isdir(src_dir):
        return 0

    copied = 0
    render_exts = {".md", ".json", ".txt", ".yml", ".yaml"}
    for root, dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        for f in files:
            src = os.path.join(root, f)
            child_rel = os.path.join(rel_root, f) if rel_root != "." else f
            dst_rel = os.path.join(rel_dir, child_rel)
            dst = os.path.join(target_dir, dst_rel)

            if os.path.exists(dst) and not overwrite:
                continue

            os.makedirs(os.path.dirname(dst), exist_ok=True)
            ext = os.path.splitext(f)[1].lower()
            if variables is not None and ext in render_exts:
                with open(src, encoding="utf-8") as fp:
                    content = render(fp.read(), variables)
                with open(dst, "w", encoding="utf-8") as fp:
                    fp.write(content)
            else:
                shutil.copy2(src, dst)
            copied += 1
    return copied


def install_project_doc_framework(target_dir, variables, overwrite=True, source_root=None):
    """Install audit/agent document framework files into a project."""
    source_root = source_root or VULCAN_DIR

    for rel_path in PROJECT_ROOT_FILES:
        src = os.path.join(source_root, rel_path)
        dst = os.path.join(target_dir, rel_path)
        if not os.path.isfile(src):
            continue
        if os.path.exists(dst) and not overwrite:
            continue
        with open(src, encoding="utf-8") as fp:
            content = render(fp.read(), variables)
        with open(dst, "w", encoding="utf-8") as fp:
            fp.write(content)
        print(f"  install/update: {rel_path}")

    for rel_dir in PROJECT_DOC_SETS:
        copied = copy_source_tree(
            target_dir,
            rel_dir,
            variables=variables,
            overwrite=overwrite,
            source_root=source_root,
        )
        if copied:
            print(f"  install/update: {rel_dir}/ ({copied} files)")

    for rel_dir in PROJECT_DOC_DIRS:
        write_file(target_dir, os.path.join(rel_dir, ".gitkeep"), "")


def ensure_gitignore_entry(project_dir, entry):
    path = os.path.join(project_dir, ".gitignore")
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()

    lines = {line.strip() for line in existing.splitlines()}
    if entry.strip() in lines:
        return

    suffix = "" if not existing or existing.endswith("\n") else "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(existing + suffix + entry.rstrip() + "\n")
    print(f"  update: .gitignore ({entry})")


def slugify(value):
    value = value.strip().lower()
    value = re.sub(r"[^0-9a-zA-Z가-힣_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "run"


def split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def next_run_id(project_dir="."):
    runs_dir = os.path.join(project_dir, "docs", "runs")
    max_num = 0
    if os.path.isdir(runs_dir):
        for name in os.listdir(runs_dir):
            match = re.match(r"RUN-(\d+)", name)
            if match:
                max_num = max(max_num, int(match.group(1)))
    return f"RUN-{max_num + 1:03d}"


def format_yaml_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def default_persona_for_run(gate, skill):
    if skill in RUN_SKILL_DEFAULT_PERSONAS:
        return RUN_SKILL_DEFAULT_PERSONAS[skill]

    return {
        "gate1": "requirements",
        "gate2": "design",
        "gate3": "test-design",
        "impl": "build",
        "gate4": "review",
        "gate5": "release",
    }.get(gate, "review")


def load_session(project_dir="."):
    path = os.path.join(project_dir, "session.json")
    if not os.path.exists(path):
        print("오류: session.json을 찾을 수 없습니다. 프로젝트 디렉토리에서 실행하세요.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_session(session, project_dir="."):
    path = os.path.join(project_dir, "session.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)


def git_commit(message, project_dir=".", include_source=False):
    try:
        subprocess.run(["git", "add", "session.json"], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "docs/"], cwd=project_dir, check=True, capture_output=True)
        if include_source:
            # 구현/QA 이후: .gitignore가 관리하는 범위 내에서 모든 변경 포함
            subprocess.run(["git", "add", "-A"], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], cwd=project_dir, check=True, capture_output=True)
        print(f"  커밋 완료: {message}")
    except subprocess.CalledProcessError as e:
        # git commit 실패는 경고만 출력하고 계속 진행 (git_push와 다른 동작)
        print(f"  경고: git commit 실패 - {e.stderr.decode().strip()}")


def git_push(project_dir="."):
    """현재 프로젝트 디렉토리에서 git push를 실행합니다.

    git commit과 달리 push 실패는 프로세스를 즉시 중단합니다 (REQ-006-02).

    Args:
        project_dir: git push를 실행할 프로젝트 디렉토리 경로.
    """
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        print(f"  푸시 완료")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace").strip()
        print(f"git push 실패: {stderr}")
        sys.exit(1)


# ── check-trace ────────────────────────────────────────────────────────────

def count_docs(project_dir="."):
    """docs/ 하위 4개 디렉토리의 .md 파일 수를 카운트한다.

    서브디렉토리 내 .md 파일도 포함한다. 디렉토리가 없거나 권한 오류 시
    해당 카테고리를 0으로 처리하고 계속 진행한다 (graceful).

    Args:
        project_dir: 프로젝트 루트 디렉토리 경로.

    Returns:
        requirements, design, test_plan, review 카테고리별 .md 파일 수와
        total 합계를 담은 dict.
    """
    categories = {
        "requirements": os.path.join(project_dir, "docs", "01-requirements"),
        "design":       os.path.join(project_dir, "docs", "02-design"),
        "test_plan":    os.path.join(project_dir, "docs", "03-test-plan"),
        "review":       os.path.join(project_dir, "docs", "04-review"),
    }
    counts = {}
    for key, dir_path in categories.items():
        count = 0
        try:
            for root, _dirs, files in os.walk(dir_path):
                count += sum(1 for f in files if f.endswith(".md"))
        except OSError:
            # 디렉토리 미존재 또는 권한 오류 — 0으로 처리하고 계속 진행
            count = 0
        counts[key] = count
    counts["total"] = sum(counts.values())
    return counts


def compute_stats(project_dir="."):
    """check-trace에서 수집한 파싱 결과를 조합하여 stats 딕셔너리를 조립한다.

    parse_requirements, parse_test_plan_status, count_docs, parse_traceability를
    호출하여 요구사항/테스트/문서 통계를 단일 dict로 반환한다. 파싱 실패 시
    해당 섹션을 0 기본값으로 채우고 예외를 전파하지 않는다.

    Args:
        project_dir: 프로젝트 루트 디렉토리 경로.

    Returns:
        requirements, tests, docs 섹션과 updated_at을 포함한 stats dict.
    """
    # requirements 섹션
    try:
        group_reqs, detail_reqs, defined_acs, ac_delegates = parse_requirements(project_dir)
        traceability = parse_traceability(project_dir)
        implemented = sum(
            1 for info in traceability.values()
            if info.get("status") in ("구현완료", "완료")
        )
        total_reqs = len(detail_reqs)
        # ac가 있는 REQ: defined_acs에 해당 AC-ID가 있거나 ac_delegates에 위임 참조가 있는 경우
        ac_covered = sum(
            1 for req in detail_reqs
            if req.replace("REQ-", "") in defined_acs
            or req.replace("REQ-", "") in ac_delegates
        )
        requirements_stats = {
            "groups":      len(group_reqs),
            "total":       total_reqs,
            "implemented": implemented,
            "pending":     total_reqs - implemented,
            "ac_defined":  ac_covered,
            "ac_missing":  total_reqs - ac_covered,
        }
    except Exception:
        requirements_stats = {
            "groups": 0, "total": 0, "implemented": 0,
            "pending": 0, "ac_defined": 0, "ac_missing": 0,
        }

    # tests 섹션
    try:
        tst_results = parse_test_plan_status(project_dir)
        tests_stats = {
            "total":   len(tst_results),
            "passed":  sum(1 for _, s in tst_results if s == "pass"),
            "failed":  sum(1 for _, s in tst_results if s == "fail"),
            "skipped": sum(1 for _, s in tst_results if s == "skip"),
            "pending": sum(1 for _, s in tst_results if s == "not_executed"),
        }
    except Exception:
        tests_stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "pending": 0}

    # docs 섹션
    try:
        docs_stats = count_docs(project_dir)
    except Exception:
        docs_stats = {"requirements": 0, "design": 0, "test_plan": 0, "review": 0, "total": 0}

    # backlog 섹션
    try:
        backlog_stats = compute_backlog_stats(project_dir)
    except Exception:
        backlog_stats = {
            "active": 0, "done": 0, "rejected": 0,
            "by_level": {"trivial": 0, "small": 0, "major": 0},
            "by_priority": {"p0": 0, "p1": 0, "p2": 0, "p3": 0},
        }

    return {
        "requirements": requirements_stats,
        "tests":        tests_stats,
        "docs":         docs_stats,
        "backlog":      backlog_stats,
        "updated_at":   date.today().isoformat(),
    }


def parse_requirements(project_dir="."):
    """REQUIREMENTS.md에서 REQ-ID 및 AC 정보를 파싱합니다."""
    path = os.path.join(project_dir, "docs", "01-requirements", "REQUIREMENTS.md")
    if not os.path.exists(path):
        return set(), set(), set(), {}

    with open(path, encoding="utf-8") as f:
        content = f.read()

    detail_reqs = set(re.findall(r'\bREQ-\d{3}-\d{2}\b', content))
    all_reqs = set(re.findall(r'\bREQ-\d{3}\b', content))
    group_reqs = {r for r in all_reqs if not re.match(r'REQ-\d{3}-\d{2}', r)}
    defined_acs = set(re.findall(r'###\s+AC-(\d{3}-\d{2})', content))

    # AC 위임 관계 파싱: REQ-XXX-XX 행에 자기 AC는 없지만 다른 AC-ID가 참조되면 위임
    ac_delegates = {}
    for line in content.splitlines():
        m_req = re.search(r'\bREQ-(\d{3}-\d{2})\b', line)
        if m_req:
            req_id = m_req.group(1)
            if req_id not in defined_acs:
                refs = re.findall(r'\bAC-(\d{3}-\d{2})\b', line)
                for ref in refs:
                    if ref != req_id:
                        ac_delegates[req_id] = ref
                        break

    return group_reqs, detail_reqs, defined_acs, ac_delegates


def parse_traceability(project_dir="."):
    """TRACEABILITY.md를 파싱하여 REQ-ID별 추적 정보를 반환합니다.
    Returns: dict[req_id] = {"design": str, "tst_ids": list, "review": str, "status": str}
    TRACEABILITY.md가 없으면 빈 dict 반환 (하위 호환성 유지).
    """
    path = os.path.join(project_dir, "docs", "TRACEABILITY.md")
    if not os.path.exists(path):
        return {}
    result = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip().startswith('|'):
                continue
            cols = [c.strip() for c in line.split('|')]
            if len(cols) < 6:
                continue
            req_id = cols[1]
            if not re.match(r'REQ-\d{3}-\d{2}', req_id):
                continue
            design  = cols[2] if cols[2] != '-' else ''
            tst_raw = cols[3] if cols[3] != '-' else ''
            review  = cols[4] if cols[4] != '-' else ''
            status  = cols[5] if len(cols) > 5 else ''
            tst_ids = [t.strip() for t in tst_raw.split(',') if t.strip() and t.strip() != '-']
            result[req_id] = {"design": design, "tst_ids": tst_ids, "review": review, "status": status}
    return result


def parse_test_plan(project_dir="."):
    """Test-Plan.md에서 TST-ID → REQ-ID 매핑을 파싱합니다."""
    path = os.path.join(project_dir, "docs", "03-test-plan", "Test-Plan.md")
    if not os.path.exists(path):
        return set()

    with open(path, encoding="utf-8") as f:
        content = f.read()

    return set(re.findall(r'\bREQ-\d{3}-\d{2}\b', content))


def parse_test_plan_status(project_dir="."):
    """Test-Plan.md에서 TST-ID별 실행 상태를 파싱합니다.
    마크다운 테이블 행에서 '| TST-NNN-NN |' 패턴만 파싱합니다.
    템플릿 행(TST-ID, TST-NNN-NN 등)과 본문 참조는 무시합니다.
    Returns: list of (tst_id, status) tuples
    """
    path = os.path.join(project_dir, "docs", "03-test-plan", "Test-Plan.md")
    if not os.path.exists(path):
        return []

    with open(path, encoding="utf-8") as f:
        content = f.read()

    results = []
    for line in content.splitlines():
        # 마크다운 테이블 행만 대상 (|로 시작)
        if not line.strip().startswith('|'):
            continue
        # 구체적인 TST-ID만 매칭 (TST-NNN-NN 또는 TST-SEC-NN 형식)
        # TST-ID, TST-NNN-NN 같은 템플릿/플레이스홀더는 제외
        tst_match = re.search(r'\|\s*(TST-(?:\d{3}-\d{2}|SEC-\d{2}))\s*\|', line)
        if not tst_match:
            continue
        tst_id = tst_match.group(1)

        # 상태 판별: Pass/Fail/Skip/미실행
        line_lower = line.lower()
        if re.search(r'\bpass\b', line_lower):
            status = 'pass'
        elif re.search(r'\bfail\b', line_lower):
            status = 'fail'
        elif re.search(r'\bskip\b', line_lower):
            status = 'skip'
        else:
            status = 'not_executed'

        results.append((tst_id, status))

    return results


def check_trace(project_dir="."):
    session = load_session(project_dir)
    current_gate = session.get("current_gate", "gate1")
    issues = []

    print(f"\n[check-trace] {session.get('project', '프로젝트')} - {GATE_LABELS.get(current_gate, current_gate)}\n")

    group_reqs, detail_reqs, defined_acs, ac_delegates = parse_requirements(project_dir)

    # 증분 Rollback: rollback_scope가 있으면 scope 내 REQ만 검증 대상
    rollback_scope = session.get("rollback_scope")
    if rollback_scope and rollback_scope.get("req_ids"):
        scope_set = set()
        for rid in rollback_scope["req_ids"]:
            # REQ-NNN 형식이면 해당 그룹의 REQ-NNN-NN 전부 포함
            if re.match(r'^(REQ|NREQ)-\d{3}$', rid):
                prefix = rid + "-"
                for r in detail_reqs:
                    if r.startswith(prefix):
                        scope_set.add(r)
            else:
                scope_set.add(rid)
        original_count = len(detail_reqs)
        detail_reqs = {r for r in detail_reqs if r in scope_set}
        print(f"  [증분 Rollback 모드] scope: {', '.join(sorted(rollback_scope['req_ids']))}")
        print(f"  scope 내 REQ: {len(detail_reqs)}/{original_count} (나머지는 이미 통과로 간주)\n")

    # ── Gate 1: REQ-ID별 AC 존재 여부 + TRACEABILITY.md 행 등록 여부
    if current_gate == "gate1":
        print("  Gate 1 검사 (1): 인수 기준(AC) 정의 여부")
        if not detail_reqs:
            issues.append("REQUIREMENTS.md에 REQ-NNN-NN 형식의 요구사항이 없습니다.")
        for req in sorted(detail_reqs):
            ac_id = req.replace("REQ-", "")
            if ac_id in defined_acs:
                print(f"  O {req} - AC 확인")
            elif ac_id in ac_delegates and ac_delegates[ac_id] in defined_acs:
                print(f"  O {req} - AC-{ac_delegates[ac_id]} 위임 확인")
            else:
                issues.append(f"  X {req} - AC 미정의")

        print("\n  Gate 1 검사 (2): TRACEABILITY.md 행 등록 여부")
        traceability = parse_traceability(project_dir)
        if not traceability:
            issues.append("  X TRACEABILITY.md 없음 — PM이 작성해야 합니다")
        else:
            for req in sorted(detail_reqs):
                if req in traceability:
                    print(f"  O {req} - TRACEABILITY.md 행 확인")
                else:
                    issues.append(f"  X {req} - TRACEABILITY.md에 행 미등록")

    # ── Gate 2: 설계 파일 내 REQ-ID 포함 여부 (TRACEABILITY.md 우선, 없으면 그룹 파일 fallback)
    if current_gate == "gate2":
        design_dir = os.path.join(project_dir, "docs", "02-design")
        traceability = parse_traceability(project_dir)

        if traceability:
            print("  Gate 2 검사: TRACEABILITY.md 기반 설계 파일 내 REQ-ID 포함 확인")
            for req in sorted(detail_reqs):
                info = traceability.get(req)
                if info and re.search(r'통합|삭제됨', info.get("status", "")):
                    print(f"  - {req} - {info['status']} (검사 제외)")
                    continue
                if not info or not info["design"]:
                    issues.append(f"  X {req} - TRACEABILITY.md에 설계 문서 미등록")
                    continue
                # 쉼표 구분된 복수 설계 파일 지원
                design_files = [f.strip() for f in info["design"].split(',') if f.strip()]
                found_in_any = False
                missing_files = []
                for df in design_files:
                    filepath = os.path.join(design_dir, df)
                    if not os.path.exists(filepath):
                        missing_files.append(df)
                        continue
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                    if req in content:
                        found_in_any = True
                        break
                if missing_files and not found_in_any:
                    issues.append(f"  X {req} - {', '.join(missing_files)} 파일 없음")
                elif found_in_any:
                    print(f"  O {req} - {info['design']} 내 ID 확인")
                else:
                    issues.append(f"  X {req} - {info['design']} 안에 {req} 없음")
        else:
            print("  Gate 2 검사: REQ 그룹별 설계 파일 존재 여부 (TRACEABILITY.md 없음 — fallback)")
            for group in sorted(group_reqs):
                filename = f"{group.lower()}-design.md"
                filepath = os.path.join(design_dir, filename)
                if os.path.exists(filepath):
                    print(f"  O {group} - {filename} 확인")
                else:
                    issues.append(f"  X {group} - docs/02-design/{filename} 없음")

    # ── Gate 3: 모든 REQ-NNN-NN에 TST-ID 매핑 여부 + TRACEABILITY.md tst_ids 등록 여부
    if current_gate == "gate3":
        print("  Gate 3 검사 (1): REQ-ID별 TST-ID 커버리지")
        covered = parse_test_plan(project_dir)
        traceability = parse_traceability(project_dir)
        for req in sorted(detail_reqs):
            req_status = traceability.get(req, {}).get("status", "")
            if req_status == "삭제됨" or re.search(r'통합', req_status):
                print(f"  - {req} - {req_status} (검사 제외)")
                continue
            if req in covered:
                print(f"  O {req} - TST 매핑 확인")
            else:
                issues.append(f"  X {req} - Test-Plan.md에 TST 매핑 없음")

        print("\n  Gate 3 검사 (2): TRACEABILITY.md tst_ids 컬럼 등록 여부")
        for req in sorted(detail_reqs):
            info = traceability.get(req, {})
            req_status2 = info.get("status", "")
            if req_status2 == "삭제됨" or re.search(r'통합', req_status2):
                continue
            tst_ids = info.get("tst_ids", [])
            if tst_ids:
                print(f"  O {req} - TST-ID {', '.join(tst_ids)} 등록 확인")
            else:
                issues.append(f"  X {req} - TRACEABILITY.md에 tst_ids 미등록")

    # ── Gate 4: 리뷰 파일 내 REQ-ID 포함 여부 + TST-ID 실행 상태
    if current_gate == "gate4":
        review_dir = os.path.join(project_dir, "docs", "04-review")
        traceability = parse_traceability(project_dir)

        if traceability:
            print("  Gate 4 검사 (1): TRACEABILITY.md 기반 리뷰 파일 내 REQ-ID 포함 확인")
            file_contents = {}  # 파일별 내용 캐시 (중복 읽기 방지)
            for req in sorted(detail_reqs):
                info = traceability.get(req, {})
                status = info.get("status", "")
                if status in ("미구현", "삭제됨"):
                    print(f"  - {req} - {status} (리뷰 검사 제외)")
                    continue
                review = info.get("review", "")
                if not review:
                    issues.append(f"  X {req} - TRACEABILITY.md에 리뷰 문서 미등록")
                    continue
                filepath = os.path.join(review_dir, review)
                if not os.path.exists(filepath):
                    issues.append(f"  X {req} - {review} 파일 없음")
                    continue
                if review not in file_contents:
                    with open(filepath, encoding="utf-8") as f:
                        file_contents[review] = f.read()
                if req in file_contents[review]:
                    print(f"  O {req} - {review} 내 ID 확인")
                else:
                    issues.append(f"  X {req} - {review} 안에 {req} 없음")
        else:
            print("  Gate 4 검사 (1): REQ 그룹별 리뷰 파일 존재 여부 (TRACEABILITY.md 없음 — fallback)")
            review_dir = os.path.join(project_dir, "docs", "04-review")
            for group in sorted(group_reqs):
                filename = f"{group.lower()}-review.md"
                filepath = os.path.join(review_dir, filename)
                if os.path.exists(filepath):
                    print(f"  O {group} - {filename} 확인")
                else:
                    issues.append(f"  X {group} - docs/04-review/{filename} 없음")

        print("\n  Gate 4 검사 (2): TST-ID 실행 상태")
        tst_results = parse_test_plan_status(project_dir)
        if not tst_results:
            issues.append("Test-Plan.md에 TST-ID가 없거나 파일이 존재하지 않습니다.")
        else:
            not_executed = [(tid, s) for tid, s in tst_results if s == 'not_executed']
            failed = [(tid, s) for tid, s in tst_results if s == 'fail']
            passed = [(tid, s) for tid, s in tst_results if s == 'pass']
            skipped = [(tid, s) for tid, s in tst_results if s == 'skip']

            print(f"  총 {len(tst_results)}건: Pass {len(passed)}, Fail {len(failed)}, Skip {len(skipped)}, 미실행 {len(not_executed)}")

            for tid, _ in passed:
                print(f"  O {tid} - Pass")
            for tid, _ in skipped:
                print(f"  - {tid} - Skip")
            for tid, _ in failed:
                issues.append(f"  X {tid} - Fail")
                print(f"  X {tid} - Fail")
            for tid, _ in not_executed:
                issues.append(f"  X {tid} - 미실행")
                print(f"  X {tid} - 미실행")

    # stats 계산 및 session.json 업데이트 — 이슈 유무와 무관하게 항상 실행
    try:
        stats = compute_stats(project_dir)
        session["stats"] = stats
        save_session(session, project_dir)
    except Exception as e:
        print(f"  [경고] stats 계산 실패: {e}")

    print()
    if issues:
        print(f"이슈 {len(issues)}건 발견 - Gate 완료 불가:\n")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("이슈 0건 - Gate 완료 가능합니다.")


# ── rollback ──────────────────────────────────────────────────────────────

def cmd_rollback(gate, reason="", scope=None, project_dir="."):
    """Gate 상태를 되돌린다. --scope가 있으면 증분 Rollback 모드로 작동한다.

    증분 모드에서는 session.json에 rollback_scope를 기록하여 check-trace가
    scope 내 REQ-ID만 재검증 대상으로 삼도록 한다. 기존 문서/코드는 보존된다.
    scope 생략 시 기존 전체 rollback 동작과 호환된다.
    """
    session = load_session(project_dir)

    if gate not in GATE_LABELS:
        print(f"오류: 유효하지 않은 gate - {gate}")
        print(f"  사용 가능: {', '.join(GATE_LABELS.keys())}")
        sys.exit(1)

    gate_order = ["gate1", "gate2", "gate3", "impl", "gate4", "gate5"]
    rollback_idx = gate_order.index(gate)

    # 대상 gate 및 이후 모든 gate를 pending으로 리셋
    for g in gate_order[rollback_idx:]:
        session["gate_status"][g] = "pending"

    session["current_gate"] = gate

    # completed 목록에서 rollback 대상 gate 이후 항목 제거
    labels_to_remove = {GATE_LABELS[g] for g in gate_order[rollback_idx:]}
    session["completed"] = [
        c for c in session.get("completed", [])
        if not any(c.startswith(label) for label in labels_to_remove)
    ]

    # 증분 rollback: scope 기록
    scope_list = []
    if scope:
        scope_list = [s.strip() for s in scope.split(",") if s.strip()]
        session["rollback_scope"] = {
            "gate": gate,
            "req_ids": scope_list,
            "reason": reason,
        }
    elif "rollback_scope" in session:
        # 전체 rollback이면 기존 scope 제거
        del session["rollback_scope"]

    if reason:
        session.setdefault("blocked", [])
        scope_tag = f" scope={','.join(scope_list)}" if scope_list else ""
        note = f"[rollback to {gate}{scope_tag}] {reason}"
        if note not in session["blocked"]:
            session["blocked"].append(note)

    save_session(session, project_dir)

    if scope_list:
        print(f"  증분 rollback: {gate} ({GATE_LABELS[gate]}) — scope: {', '.join(scope_list)}")
        print(f"  scope 내 REQ만 재검증 대상. 다른 REQ는 이미 통과로 간주.")
    else:
        print(f"  rollback 완료: {gate} ({GATE_LABELS[gate]}) 부터 재시작")
    print(f"  리셋된 Gate: {', '.join(gate_order[rollback_idx:])}")

    commit_msg = f"rollback: {gate}부터 재시작 - {GATE_LABELS[gate]}"
    if scope_list:
        commit_msg = f"rollback(scope={','.join(scope_list)}): {gate} - {GATE_LABELS[gate]}"
    if reason:
        commit_msg += f" ({reason})"
    git_commit(commit_msg, project_dir, include_source=False)


# ── backlog ────────────────────────────────────────────────────────────────

BACKLOG_PATH = "docs/06-backlog/BACKLOG.md"


def _parse_backlog_items(content):
    """BACKLOG.md Active 섹션의 마크다운 테이블에서 BL-NNN 항목을 파싱한다.

    Returns: list of dict{id, title, level, priority, status, req, source, note}
    """
    items = []
    in_active = False
    for line in content.splitlines():
        if line.startswith("## Active"):
            in_active = True
            continue
        if in_active and line.startswith("## ") and not line.startswith("## Active"):
            break
        if not in_active:
            continue
        m = re.match(r'^\|\s*(BL-\d{3})\s*\|', line)
        if not m:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8:
            continue
        items.append({
            "id": cols[0], "title": cols[1], "level": cols[2],
            "priority": cols[3], "status": cols[4], "req": cols[5],
            "source": cols[6], "note": cols[7],
        })
    return items


def compute_backlog_stats(project_dir="."):
    """BACKLOG.md에서 Active/Done/Rejected 건수와 레벨·우선순위별 카운트를 계산한다."""
    path = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(path):
        return {
            "active": 0, "done": 0, "rejected": 0,
            "by_level": {"trivial": 0, "small": 0, "major": 0},
            "by_priority": {"p0": 0, "p1": 0, "p2": 0, "p3": 0},
        }

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Active 항목 파싱 (레벨·우선순위 포함)
    active_items = _parse_backlog_items(content)

    # Done / Rejected 건수: BL-NNN 행만 카운트 (헤더·빈행 제외)
    def _count_section(section_header):
        count = 0
        in_section = False
        for line in content.splitlines():
            if line.startswith(f"## {section_header}"):
                in_section = True
                continue
            if in_section and line.startswith("## ") and not line.startswith(f"## {section_header}"):
                break
            if in_section and re.match(r'^\|\s*BL-\d{3}\s*\|', line):
                count += 1
        return count

    level_map = {"🟢": "trivial", "🟡": "small", "🔴": "major"}
    by_level = {"trivial": 0, "small": 0, "major": 0}
    by_priority = {"p0": 0, "p1": 0, "p2": 0, "p3": 0}
    for item in active_items:
        lv = level_map.get(item["level"])
        if lv:
            by_level[lv] += 1
        pr = item["priority"].lower()
        if pr in by_priority:
            by_priority[pr] += 1

    return {
        "active":       len(active_items),
        "done":         _count_section("Done"),
        "rejected":     _count_section("Rejected"),
        "by_level":     by_level,
        "by_priority":  by_priority,
    }


def _next_backlog_id(content):
    ids = re.findall(r'\bBL-(\d{3})\b', content)
    next_num = max([int(i) for i in ids], default=0) + 1
    return f"BL-{next_num:03d}"


def cmd_backlog_list(project_dir="."):
    path = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음. 프로젝트가 v1.1 이상인지 확인하세요.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    items = _parse_backlog_items(content)
    if not items:
        print("  백로그 Active 항목이 없습니다.")
        return

    # 우선순위 순 정렬: P0 > P1 > P2 > P3 > 기타
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    items.sort(key=lambda x: order.get(x["priority"], 9))

    print(f"\n  백로그 Active {len(items)}건:\n")
    for it in items:
        print(f"  {it['id']} [{it['priority']}/{it['level']}] {it['status']:10s} {it['title']}")
        if it["req"] and it["req"] != "-":
            print(f"         ↳ {it['req']}  ({it['source']})")
    print()


def cmd_backlog_add(title, level="", priority="P2", req="", source="", note="", project_dir="."):
    path = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    new_id = _next_backlog_id(content)
    new_row = (
        f"| {new_id} | {title} | {level or '—'} | {priority} | Proposed | "
        f"{req or '-'} | {source or '-'} | {note or '-'} |"
    )

    # Active 테이블의 placeholder 행이 있으면 대체, 아니면 마지막 BL 행 뒤에 삽입
    lines = content.splitlines()
    out = []
    inserted = False
    in_active = False
    for i, line in enumerate(lines):
        if line.startswith("## Active"):
            in_active = True
            out.append(line)
            continue
        if in_active and line.startswith("## ") and not line.startswith("## Active"):
            if not inserted:
                # Active 섹션이 끝나기 전에 새 행 삽입 (빈 줄 앞)
                # 직전 빈 줄들 건너뛰고 테이블 끝 찾기
                j = len(out) - 1
                while j > 0 and out[j].strip() == "":
                    j -= 1
                out.insert(j + 1, new_row)
                inserted = True
            in_active = False
            out.append(line)
            continue
        if in_active and "(아직 없음)" in line:
            out.append(new_row)
            inserted = True
            continue
        out.append(line)

    if not inserted:
        print("오류: BACKLOG.md Active 섹션을 찾지 못했습니다.")
        sys.exit(1)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + ("\n" if content.endswith("\n") else ""))
    print(f"  추가: {new_id} - {title}")
    print(f"  다음 단계: Triage (레벨/우선순위 결정) 후 상태 → Triaged")


def cmd_backlog_done(bl_id, commit_hash="", project_dir="."):
    """BL 항목을 Done으로 이동시킨다. Active에서 제거 후 Done 섹션에 기록."""
    path = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    items = _parse_backlog_items(content)
    target = next((i for i in items if i["id"] == bl_id), None)
    if not target:
        print(f"오류: {bl_id}를 Active 섹션에서 찾지 못했습니다.")
        sys.exit(1)

    done_row = (
        f"| {target['id']} | {target['title']} | {date.today().isoformat()} | "
        f"{commit_hash or '-'} | {target['level']} | {target['req']} |"
    )

    lines = content.splitlines()
    out = []
    in_done = False
    removed = False
    done_inserted = False
    for line in lines:
        # Active에서 대상 행 제거
        if not removed and re.match(r'^\|\s*' + re.escape(bl_id) + r'\s*\|', line):
            removed = True
            continue
        if line.startswith("## Done"):
            in_done = True
            out.append(line)
            continue
        if in_done and line.startswith("## ") and not line.startswith("## Done"):
            in_done = False
        if in_done and "(아직 없음)" in line and not done_inserted:
            out.append(done_row)
            done_inserted = True
            continue
        if in_done and re.match(r'^\|\s*\|', line) and not done_inserted:
            pass  # skip accidentally
        out.append(line)

    if in_done and not done_inserted:
        pass

    # 만약 placeholder가 없었다면 Done 섹션 마지막 행 다음에 추가
    if not done_inserted:
        new_out = []
        in_done2 = False
        appended = False
        for line in out:
            if line.startswith("## Done"):
                in_done2 = True
                new_out.append(line)
                continue
            if in_done2 and line.startswith("## ") and not line.startswith("## Done") and not appended:
                # 섹션 종료 직전에 삽입
                j = len(new_out) - 1
                while j > 0 and new_out[j].strip() == "":
                    j -= 1
                new_out.insert(j + 1, done_row)
                appended = True
                in_done2 = False
            new_out.append(line)
        out = new_out
        done_inserted = appended

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + ("\n" if content.endswith("\n") else ""))
    print(f"  완료: {bl_id} → Done ({commit_hash or 'commit 미지정'})")


def cmd_backlog_reject(bl_id, reason="", project_dir="."):
    path = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    items = _parse_backlog_items(content)
    target = next((i for i in items if i["id"] == bl_id), None)
    if not target:
        print(f"오류: {bl_id}를 Active 섹션에서 찾지 못했습니다.")
        sys.exit(1)

    rej_row = f"| {target['id']} | {target['title']} | {date.today().isoformat()} | {reason or '-'} |"

    lines = content.splitlines()
    out = []
    in_rej = False
    removed = False
    rej_inserted = False
    for line in lines:
        if not removed and re.match(r'^\|\s*' + re.escape(bl_id) + r'\s*\|', line):
            removed = True
            continue
        if line.startswith("## Rejected"):
            in_rej = True
            out.append(line)
            continue
        if in_rej and line.startswith("## ") and not line.startswith("## Rejected"):
            in_rej = False
        if in_rej and "(아직 없음)" in line and not rej_inserted:
            out.append(rej_row)
            rej_inserted = True
            continue
        out.append(line)

    if not rej_inserted:
        # fallback: append before next section
        new_out = []
        in_rej2 = False
        appended = False
        for line in out:
            if line.startswith("## Rejected"):
                in_rej2 = True
                new_out.append(line)
                continue
            if in_rej2 and line.startswith("## ") and not line.startswith("## Rejected") and not appended:
                j = len(new_out) - 1
                while j > 0 and new_out[j].strip() == "":
                    j -= 1
                new_out.insert(j + 1, rej_row)
                appended = True
                in_rej2 = False
            new_out.append(line)
        out = new_out

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + ("\n" if content.endswith("\n") else ""))
    print(f"  반려: {bl_id} → Rejected ({reason or '사유 미지정'})")


# ── session ────────────────────────────────────────────────────────────────

def cmd_session(gate, status, feature, project_dir="."):
    session = load_session(project_dir)

    if gate not in GATE_LABELS:
        print(f"오류: 유효하지 않은 gate - {gate}")
        print(f"  사용 가능: {', '.join(GATE_LABELS.keys())}")
        sys.exit(1)

    if feature:
        session["feature"] = feature

    session["gate_status"][gate] = status

    gate_order = ["gate1", "gate2", "gate3", "impl", "gate4", "gate5"]
    if status == "done":
        current_idx = gate_order.index(gate)
        if current_idx + 1 < len(gate_order):
            session["current_gate"] = gate_order[current_idx + 1]
        else:
            session["current_gate"] = "completed"

        entry = f"{GATE_LABELS[gate]} - {session.get('feature', '')}"
        if entry not in session.get("completed", []):
            session.setdefault("completed", []).append(entry)

    save_session(session, project_dir)
    print(f"  session.json 업데이트: {gate} → {status}")

    feature_label = session.get("feature", "")
    commit_msg = f"session: {gate} done - {GATE_LABELS[gate]}"
    if feature_label:
        commit_msg += f" ({feature_label})"
    # 구현(impl), Gate 4(QA리뷰), Gate 5(최종승인): 소스코드 포함 커밋
    include_source = gate in ("impl", "gate4", "gate5")
    git_commit(commit_msg, project_dir, include_source=include_source)
    # git push: commit 성공 직후 실행. 실패 시 sys.exit(1) (REQ-006-01, REQ-006-02)
    git_push(project_dir)


# ── export ────────────────────────────────────────────────────────────────

def git_log_timeline(project_dir="."):
    try:
        result = subprocess.run(
            ["git", "log", "--grep=^session:", "--date=short",
             "--pretty=format:%H|%ad|%s", "--", "session.json"],
            cwd=project_dir, capture_output=True, text=True, check=True
        )
        timeline = []
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            commit, date_str, message = parts
            timeline.append({"commit": commit[:7], "date": date_str, "message": message})
        return list(reversed(timeline))
    except subprocess.CalledProcessError:
        return []


def collect_documents(project_dir="."):
    docs = {"requirements": None, "design": [], "test_plan": None, "review": []}

    req = os.path.join(project_dir, "docs", "01-requirements", "REQUIREMENTS.md")
    if os.path.exists(req):
        docs["requirements"] = "docs/01-requirements/REQUIREMENTS.md"

    design_dir = os.path.join(project_dir, "docs", "02-design")
    if os.path.isdir(design_dir):
        docs["design"] = sorted([
            f"docs/02-design/{f}" for f in os.listdir(design_dir) if f.endswith(".md")
        ])

    tp = os.path.join(project_dir, "docs", "03-test-plan", "Test-Plan.md")
    if os.path.exists(tp):
        docs["test_plan"] = "docs/03-test-plan/Test-Plan.md"

    review_dir = os.path.join(project_dir, "docs", "04-review")
    if os.path.isdir(review_dir):
        docs["review"] = sorted([
            f"docs/04-review/{f}" for f in os.listdir(review_dir) if f.endswith(".md")
        ])

    return docs


def cmd_export(output="snapshot.json", project_dir="."):
    from datetime import datetime
    session = load_session(project_dir)

    snapshot = {
        "schema_version": "1.0",
        "framework": "vulcan-anvil",
        "project": session.get("project", ""),
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "current_gate": session.get("current_gate", "gate1"),
        "gate_status": session.get("gate_status", {}),
        "feature": session.get("feature", ""),
        "started": session.get("started", ""),
        "completed": session.get("completed", []),
        "blocked": session.get("blocked", []),
        "timeline": git_log_timeline(project_dir),
        "documents": collect_documents(project_dir),
        "stats": session.get("stats"),
    }

    out_path = os.path.join(project_dir, output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  snapshot 생성: {output}")
    print(f"  프로젝트: {snapshot['project']} | Gate: {snapshot['current_gate']}")


# ── release ───────────────────────────────────────────────────────────────

# dashboard/ 복사 시 제외할 디렉토리/파일 이름 목록 (REQ-008-03, SEC-002-03)
_DASHBOARD_EXCLUDES = {"node_modules", ".next", ".env.local"}


def _copy_tree_filtered(src_dir, dst_dir, excludes):
    """excludes에 포함된 이름을 건너뛰며 디렉토리 트리를 복사합니다.

    Args:
        src_dir: 복사 원본 디렉토리 절대 경로.
        dst_dir: 복사 대상 디렉토리 절대 경로.
        excludes: 건너뛸 파일/디렉토리 이름 집합.
    """
    import shutil
    for root, dirs, files in os.walk(src_dir):
        # 제외 디렉토리는 재귀 탐색에서도 제외 (os.walk in-place 수정)
        dirs[:] = [d for d in dirs if d not in excludes]
        rel_root = os.path.relpath(root, src_dir)
        for f in files:
            if f in excludes:
                continue
            src = os.path.join(root, f)
            rel_path = os.path.join(rel_root, f) if rel_root != "." else f
            dst = os.path.join(dst_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def cmd_release(target):
    """Vulcan-Dev에서 Vulcan-Anvil 경로로 배포 대상 파일을 복사합니다.

    배포 대상: vulcan.py, templates/, dashboard/, README.md
    배포 제외: docs/, session.json, .claude/, node_modules/, .env.local, .git/

    Args:
        target: 배포 대상 디렉토리 경로 (절대 또는 상대). (REQ-008-01)
    """
    import shutil

    target_abs = os.path.abspath(target)

    # 자기 자신 덮어쓰기 방지 (REQ-008-01)
    if os.path.abspath(VULCAN_DIR) == target_abs:
        print(f"오류: 대상 경로가 현재 Vulcan-Dev 디렉토리와 동일합니다. 자기 자신 덮어쓰기는 허용되지 않습니다.")
        sys.exit(1)

    # 대상 경로 존재 확인
    if not os.path.isdir(target_abs):
        print(f"오류: 대상 경로가 존재하지 않습니다 — {target_abs}")
        sys.exit(1)

    print(f"\nVulcan-Anvil release")
    print(f"  소스: {VULCAN_DIR}")
    print(f"  대상: {target_abs}\n")

    # vulcan.py 복사
    src_vulcan = os.path.join(VULCAN_DIR, "vulcan.py")
    if os.path.isfile(src_vulcan):
        shutil.copy2(src_vulcan, os.path.join(target_abs, "vulcan.py"))
        print(f"  생성/업데이트: vulcan.py")

    # templates/ 복사
    src_templates = os.path.join(VULCAN_DIR, "templates")
    if os.path.isdir(src_templates):
        dst_templates = os.path.join(target_abs, "templates")
        _copy_tree_filtered(src_templates, dst_templates, excludes=set())
        print(f"  생성/업데이트: templates/")

    # dashboard/ 복사 (node_modules/, .next/, .env.local 제외)
    src_dashboard = os.path.join(VULCAN_DIR, "dashboard")
    if os.path.isdir(src_dashboard):
        dst_dashboard = os.path.join(target_abs, "dashboard")
        _copy_tree_filtered(src_dashboard, dst_dashboard, excludes=_DASHBOARD_EXCLUDES)
        print(f"  생성/업데이트: dashboard/")

    # README.md 복사
    src_readme = os.path.join(VULCAN_DIR, "README.md")
    if os.path.isfile(src_readme):
        shutil.copy2(src_readme, os.path.join(target_abs, "README.md"))
        print(f"  생성/업데이트: README.md")

    print(f"\n완료! {target_abs} 에 배포되었습니다.")


# ── upgrade ────────────────────────────────────────────────────────────────

# upgrade 시 타겟에서 삭제할 파일 (이전 버전에서 제거된 파일)
DEPRECATED_FILES = [
    ".claude/skills/gate-transition/skill.md",
    "docs/CHANGE_PROCESS.md",
]

FRAMEWORK_FILES = [
    # CLAUDE.md & settings
    ".claude/CLAUDE.md",
    ".claude/settings.json",
    # agents
    ".claude/agents/concierge.md",
    ".claude/agents/pm.md",
    ".claude/agents/architect.md",
    ".claude/agents/dba.md",
    ".claude/agents/ui-designer.md",
    ".claude/agents/frontend-dev.md",
    ".claude/agents/backend-dev.md",
    ".claude/agents/ux-reviewer.md",
    ".claude/agents/qa.md",
    # rules
    ".claude/rules/core-principles.md",
    ".claude/rules/gate1-requirements.md",
    ".claude/rules/gate2-design.md",
    ".claude/rules/gate3-testplan.md",
    ".claude/rules/gate4-review.md",
    ".claude/rules/implementation.md",
    ".claude/rules/traceability.md",
    # skills
    ".claude/skills/vulcan/skill.md",
    ".claude/skills/security-baseline/skill.md",
    ".claude/skills/debugging-and-error-recovery/skill.md",
    ".claude/skills/context-engineering/skill.md",
    ".claude/skills/git-workflow-and-versioning/skill.md",
    # docs & guides
    "commenting-standards.md",
    "GATE_GUIDE.md",
    "docs/05-security/baseline.md",
    # backlog (v1.1+): PROCESS.md는 upgrade 시 덮어쓰기, BACKLOG.md는 보존
    "docs/06-backlog/PROCESS.md",
]


def read_version_from_vulcan(vulcan_py_path):
    try:
        with open(vulcan_py_path, encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'^VULCAN_VERSION\s*=\s*["\'](.+?)["\']', content, re.MULTILINE)
        return match.group(1) if match else "unknown"
    except OSError:
        return "unknown"


def extract_variables(project_dir="."):
    """CLAUDE.md에서 프로젝트 변수 추출."""
    claude_path = os.path.join(project_dir, ".claude", "CLAUDE.md")
    if not os.path.exists(claude_path):
        print("오류: .claude/CLAUDE.md를 찾을 수 없습니다.")
        sys.exit(1)

    with open(claude_path, encoding="utf-8") as f:
        content = f.read()

    project = re.search(r'^# (.+?)(?:\s+-|\s+Harness)', content, re.MULTILINE)
    generated = re.search(r'생성일: (.+)', content)

    session = load_session(project_dir)

    return {
        "PROJECT_NAME": project.group(1).strip() if project else session.get("project", "Unknown"),
        "GENERATED_DATE": generated.group(1).strip() if generated else str(date.today()),
    }


def cmd_upgrade(project_dir="."):
    import shutil

    session = load_session(project_dir)
    vulcan_src = session.get("vulcan_src") or VULCAN_DIR
    src_templates = os.path.join(vulcan_src, "templates")

    if not os.path.isdir(src_templates):
        print("오류: Vulcan-Anvil 원본 경로를 찾을 수 없습니다.")
        print(f"  templates 디렉터리가 없습니다: {src_templates}")
        sys.exit(1)

    current_ver = session.get("vulcan_version", "unknown")
    src_vulcan = os.path.join(vulcan_src, "vulcan.py")
    new_ver = read_version_from_vulcan(src_vulcan)

    variables = extract_variables(project_dir)
    print(f"\nVulcan-Anvil upgrade")
    print(f"  프로젝트: {variables['PROJECT_NAME']}")
    print(f"  버전: {current_ver} → {new_ver}")
    print(f"  소스: {vulcan_src}\n")

    for rel_path in FRAMEWORK_FILES:
        tpl_path = os.path.join(src_templates, rel_path)
        if not os.path.exists(tpl_path):
            print(f"  건너뜀 (템플릿 없음): {rel_path}")
            continue
        with open(tpl_path, encoding="utf-8") as f:
            content = render(f.read(), variables)
        dst = os.path.join(project_dir, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  업데이트: {rel_path}")

    for rel_path in DEPRECATED_FILES:
        dst = os.path.join(project_dir, rel_path)
        if os.path.exists(dst):
            os.remove(dst)
            parent = os.path.dirname(dst)
            if os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)
            print(f"  삭제 (deprecated): {rel_path}")

    if os.path.exists(src_vulcan):
        shutil.copy2(src_vulcan, os.path.join(project_dir, "vulcan.py"))
        print(f"  업데이트: vulcan.py")

    # v1.1+: BACKLOG.md가 없으면 생성 (있으면 사용자 데이터 보존)
    backlog_dst = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(backlog_dst):
        tpl = os.path.join(src_templates, "docs/06-backlog/BACKLOG.md")
        if os.path.exists(tpl):
            with open(tpl, encoding="utf-8") as f:
                content = render(f.read(), variables)
            os.makedirs(os.path.dirname(backlog_dst), exist_ok=True)
            with open(backlog_dst, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  생성 (v1.1 신규): docs/06-backlog/BACKLOG.md")

    # v1.2+: 설계·리뷰 템플릿이 없으면 생성 (있으면 사용자 작업 보존)
    for tpl_rel, label in [
        ("docs/02-design/REQ-NNN-Design.md", "Gate 2 설계 템플릿"),
        ("docs/04-review/UX-Review.md",       "UX 리뷰 템플릿"),
        ("docs/04-review/REQ-NNN-Review.md",  "QA 리뷰 템플릿"),
    ]:
        dst = os.path.join(project_dir, tpl_rel)
        if not os.path.exists(dst):
            tpl = os.path.join(src_templates, tpl_rel)
            if os.path.exists(tpl):
                with open(tpl, encoding="utf-8") as f:
                    content = render(f.read(), variables)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  생성 (v1.2 신규): {tpl_rel} ({label})")

    install_project_doc_framework(project_dir, variables, overwrite=True, source_root=vulcan_src)
    ensure_gitignore_entry(project_dir, "docs/ref-docs/")

    session["vulcan_version"] = new_ver
    session["vulcan_src"] = vulcan_src
    save_session(session, project_dir)

    print(f"\n완료! v{current_ver} → v{new_ver}")
    print(f"보존된 파일: ENVIRONMENT.md, session.json, docs/")


# ── version ───────────────────────────────────────────────────────────────

def cmd_version(project_dir="."):
    print(f"Vulcan-Anvil v{VULCAN_VERSION}")
    session_path = os.path.join(project_dir, "session.json")
    if os.path.exists(session_path):
        session = load_session(project_dir)
        project_ver = session.get("vulcan_version", "unknown")
        print(f"  프로젝트: {session.get('project', '-')} (설치 버전: {project_ver})")


# ── init ───────────────────────────────────────────────────────────────────

def cmd_run_new(adapter, gate, skill, title, related_ids, persona=None, project_dir="."):
    if skill not in RUN_SKILLS:
        print(f"오류: 알 수 없는 skill입니다: {skill}")
        print("사용 가능 skill:")
        for name in RUN_SKILLS:
            print(f"  - {name}")
        sys.exit(1)

    persona = persona or default_persona_for_run(gate, skill)
    if persona not in RUN_PERSONAS:
        print(f"오류: 알 수 없는 persona입니다: {persona}")
        print("사용 가능 persona:")
        for name in RUN_PERSONAS:
            print(f"  - {name}")
        sys.exit(1)

    run_id = next_run_id(project_dir)
    rel_path = os.path.join("docs", "runs", f"{run_id}_{slugify(title)}_v0.1.md")
    ids = split_csv(related_ids)
    skill_path = RUN_SKILLS[skill]

    content = f"""# {run_id} {title}

```yaml
run_id: {run_id}
adapter: {adapter}
gate: {gate}
persona: {persona}
skill: {skill}
skill_path: {skill_path}
status: Draft
created_at: {date.today()}
related_ids: {format_yaml_list(ids)}
verification_results: []
evidence: []
traceability_updates: []
findings: []
change_requests: []
open_issues: []
```

## 1. Run 목표

{title}

## 2. 에이전트가 먼저 읽을 문서

- `AGENTS.md`
- `docs/core/ID_SYSTEM.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/PERSONA_DELEGATION.md`
- `{skill_path}`

## 3. 입력 범위

| 항목 | 내용 |
| --- | --- |
| 관련 ID | `{format_yaml_list(ids)}` |
| Persona | `{persona}` |
| 대상 문서 | TBD |
| 대상 코드 | TBD |
| 제외 범위 | TBD |

## 4. 수행 지시

1. 관련 문서와 코드를 확인한다.
2. `{persona}` persona의 책임과 금지사항을 확인한다.
3. skill 절차에 따라 누락, 결함, 변경 필요 여부를 판단한다.
4. 필요한 경우 문서, 코드, 테스트, 증적을 갱신한다.
5. 검증 명령을 실행하고 결과를 기록한다.
6. `RUN_OUTPUT_CONTRACT.md` 형식에 맞게 이 Run 기록을 갱신한다.

## 5. 완료 보고

### 요약

TBD

### 변경 파일

TBD

### 검증 결과

TBD

### 후속 조치

TBD
"""
    write_file(project_dir, rel_path, content)
    print(f"\nRun 초안 생성 완료: {rel_path}")
    print(f"다음 단계: 에이전트는 Run 파일과 `{skill_path}`를 기준으로 작업합니다.")


def check_run_file(path):
    issues = []
    warnings = []
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"오류: Run 파일을 읽을 수 없습니다: {e}")
        sys.exit(1)

    for key in RUN_REQUIRED_KEYS:
        if not re.search(rf"^\s*{re.escape(key)}\s*:", content, re.MULTILINE):
            issues.append(f"필수 필드 누락: {key}")

    if not re.search(r"\b(REQ|NREQ|AC|FUNC|SCR|PGM|DB|IF|SEC|UT|IT|PT|UI|FIND|CR|ISSUE|RUN)-\d+\b", content):
        issues.append("관련 추적 ID가 없습니다.")

    status_match = re.search(r"^\s*status\s*:\s*(.+)$", content, re.MULTILINE)
    if status_match:
        status = status_match.group(1).strip()
        if status not in {"Draft", "InProgress", "Completed", "Blocked", "Failed", "CompletedWithIssues"}:
            issues.append(f"허용되지 않은 status 값: {status}")

    skill_match = re.search(r"^\s*skill\s*:\s*(.+)$", content, re.MULTILINE)
    if skill_match:
        skill = skill_match.group(1).strip()
        if skill not in RUN_SKILLS:
            issues.append(f"알 수 없는 skill 값: {skill}")

    persona_match = re.search(r"^\s*persona\s*:\s*(.+)$", content, re.MULTILINE)
    if persona_match:
        persona = persona_match.group(1).strip()
        if persona not in RUN_PERSONAS:
            issues.append(f"알 수 없는 persona 값: {persona}")

    if re.search(r"result\s*:\s*passed", content, re.IGNORECASE) and not re.search(r"command\s*:", content):
        issues.append("passed 결과가 있지만 검증 command가 없습니다.")

    if re.search(r"status\s*:\s*Completed", content) and re.search(r"verification_results\s*:\s*\[\]", content):
        warnings.append("Completed 상태이지만 verification_results가 비어 있습니다.")

    if re.search(r"status\s*:\s*Completed", content) and re.search(r"traceability_updates\s*:\s*\[\]", content):
        warnings.append("Completed 상태이지만 traceability_updates가 비어 있습니다.")

    return issues, warnings


def cmd_run_check(run_file):
    issues, warnings = check_run_file(run_file)
    if warnings:
        print("경고:")
        for warning in warnings:
            print(f"  - {warning}")

    if issues:
        print("Run 검증 실패:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    print("Run 검증 통과")


def create_session_json(target_dir, project_name):
    session = {
        "project": project_name,
        "vulcan_src": VULCAN_DIR,
        "vulcan_version": VULCAN_VERSION,
        "current_gate": "gate1",
        "gate_status": {
            "gate1": "pending",
            "gate2": "pending",
            "gate3": "pending",
            "impl":  "pending",
            "gate4": "pending",
            "gate5": "pending"
        },
        "feature": "",
        "started": str(date.today()),
        "completed": [],
        "pending": [],
        "blocked": []
    }
    write_file(target_dir, "session.json", json.dumps(session, ensure_ascii=False, indent=2))


def init(target_dir, project_name, agent_name):
    import shutil
    print(f"\nVulcan-Anvil 초기화")
    print(f"  프로젝트: {project_name}")
    print(f"  대상 폴더: {target_dir}\n")

    if os.path.exists(target_dir):
        files = os.listdir(target_dir)
        if files:
            print(f"경고: {target_dir} 폴더가 비어있지 않습니다.")
            answer = input("계속 진행할까요? (y/N): ").strip().lower()
            if answer != "y":
                print("취소됨.")
                sys.exit(0)
    else:
        os.makedirs(target_dir)

    variables = {
        "PROJECT_NAME": project_name,
        "GENERATED_DATE": str(date.today()),
    }

    # .claude/ 디렉토리 전체 복사 후 변수 치환
    src_claude = os.path.join(TEMPLATES_DIR, ".claude")
    dst_claude = os.path.join(target_dir, ".claude")
    copy_tree(src_claude, dst_claude)
    print(f"  생성: .claude/ (agents 13, skills 5, rules 7)")

    # .claude/ 내 모든 .md 파일에 변수 치환 적용
    for root, dirs, files in os.walk(dst_claude):
        for f in files:
            if f.endswith(".md"):
                fpath = os.path.join(root, f)
                with open(fpath, encoding="utf-8") as fp:
                    content = render(fp.read(), variables)
                with open(fpath, "w", encoding="utf-8") as fp:
                    fp.write(content)

    # ENVIRONMENT.md
    content = render(read_template("ENVIRONMENT.md"), variables)
    write_file(target_dir, "ENVIRONMENT.md", content)

    # commenting-standards.md
    copy_file(target_dir, "commenting-standards.md")

    # GATE_GUIDE.md
    copy_file(target_dir, "GATE_GUIDE.md")

    # docs/00-discovery/
    copy_file(target_dir, "docs/00-discovery/DISCOVERY-CHECKLIST.md", "docs/00-discovery/DISCOVERY-CHECKLIST.md")
    copy_file(target_dir, "docs/00-discovery/CHANGELOG.md", "docs/00-discovery/CHANGELOG.md")
    copy_file(target_dir, "docs/00-discovery/glossary/glossary.md", "docs/00-discovery/glossary/glossary.md")
    write_file(target_dir, "docs/00-discovery/requirements/.gitkeep", "")
    write_file(target_dir, "docs/00-discovery/functional/.gitkeep", "")
    write_file(target_dir, "docs/00-discovery/infrastructure/.gitkeep", "")
    write_file(target_dir, "docs/00-discovery/technical-review/.gitkeep", "")
    write_file(target_dir, "docs/00-discovery/estimation/.gitkeep", "")
    write_file(target_dir, "docs/00-discovery/audit/.gitkeep", "")
    write_file(target_dir, "docs/00-discovery/references/.gitkeep", "")
    print(f"  생성: docs/00-discovery/")

    # docs/01-requirements/
    content = render(read_template("docs/01-requirements/REQUIREMENTS.md"), variables)
    write_file(target_dir, "docs/01-requirements/REQUIREMENTS.md", content)

    # docs/02-design/ — 설계 문서 템플릿 (Architect가 REQ-NNN-Design.md로 복사하여 사용)
    copy_file(target_dir, "docs/02-design/REQ-NNN-Design.md", "docs/02-design/REQ-NNN-Design.md")
    print(f"  생성: docs/02-design/REQ-NNN-Design.md (Gate 2 설계 템플릿)")

    content = render(read_template("docs/03-test-plan/Test-Plan.md"), variables)
    write_file(target_dir, "docs/03-test-plan/Test-Plan.md", content)

    # docs/04-review/ — UX 리뷰·QA 리뷰 템플릿
    content = render(read_template("docs/04-review/UX-Review.md"), variables)
    write_file(target_dir, "docs/04-review/UX-Review.md", content)
    copy_file(target_dir, "docs/04-review/REQ-NNN-Review.md", "docs/04-review/REQ-NNN-Review.md")
    print(f"  생성: docs/04-review/ (UX-Review.md, REQ-NNN-Review.md 템플릿)")

    # docs/06-backlog/
    content = render(read_template("docs/06-backlog/BACKLOG.md"), variables)
    write_file(target_dir, "docs/06-backlog/BACKLOG.md", content)
    copy_file(target_dir, "docs/06-backlog/PROCESS.md", "docs/06-backlog/PROCESS.md")

    # TRACEABILITY
    content = render(read_template("docs/TRACEABILITY.md"), variables)
    write_file(target_dir, "docs/TRACEABILITY.md", content)

    # security
    copy_file(target_dir, "docs/05-security/baseline.md", "docs/05-security/baseline.md")
    write_file(target_dir, "docs/05-security/compliance/.gitkeep", "")

    # audit and agent coding document framework
    install_project_doc_framework(target_dir, variables, overwrite=True)

    # session.json
    create_session_json(target_dir, project_name)

    # vulcan.py 자신을 프로젝트에 복사
    shutil.copy2(__file__, os.path.join(target_dir, "vulcan.py"))
    print(f"  생성: vulcan.py")

    # .gitignore
    gitignore = "node_modules/\n.env\n.env.local\ndashboard/.next/\ndashboard/node_modules/\ndocs/ref-docs/\n"
    write_file(target_dir, ".gitignore", gitignore)

    # git init + 초기 커밋
    # 참고: dashboard/는 Vulcan-Anvil 루트에 단일 설치하여 재사용합니다 (REQ-007-01)
    try:
        subprocess.run(["git", "init"], cwd=target_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=target_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"init: {project_name} 프로젝트 초기화"],
            cwd=target_dir, check=True, capture_output=True
        )
        print(f"  생성: git 저장소 초기화 + 초기 커밋")
    except Exception as e:
        print(f"  경고: git 초기화 실패 - {e}")

    print(f"\n완료! {project_name} 프로젝트가 초기화되었습니다.")
    print(f"\n다음 단계:")
    print(f"  1. cd {target_dir}")
    print(f"  2. Claude Code 실행")
    print(f"  3. '상위설계 시작' (Phase 0) 또는 'Gate 1 시작해줘'로 프로세스 시작")
    print(f"\n대시보드 실행:")
    print(f"  cd <Vulcan-Anvil 경로>/dashboard && npm run dev")
    print(f"  브라우저: http://localhost:3001")
    print(f"\nGate 완료 시:")
    print(f"  python vulcan.py check-trace")
    print(f"  python vulcan.py session --gate gate1 --status done --feature '기능명'")


# ── main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vulcan-Anvil - 5-Gate AI 협업 개발 프레임워크",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
명령어:
  init         새 프로젝트 초기화 (Vulcan-Anvil 디렉토리에서 실행)
  check-trace  현재 Gate 정합성 검사 (프로젝트 디렉토리에서 실행)
  session      Gate 상태 업데이트 + git commit (프로젝트 디렉토리에서 실행)
  rollback     특정 Gate부터 재시작 (해당 Gate 이후 모두 pending 리셋)
  export       snapshot.json 생성 (프로젝트 디렉토리에서 실행)
  upgrade      프레임워크 파일 최신화 (프로젝트 디렉토리에서 실행)
  version      현재 프레임워크 버전 확인

예시:
  python vulcan.py init ../my-app "MyApp"
  python vulcan.py check-trace
  python vulcan.py session --gate gate1 --status done --feature "로그인 기능"
  python vulcan.py rollback --gate gate2 --reason "요구사항 추가"
  python vulcan.py export
  python vulcan.py upgrade
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    p_init = subparsers.add_parser("init", help="새 프로젝트 초기화")
    p_init.add_argument("target_dir", help="초기화할 프로젝트 폴더 경로")
    p_init.add_argument("project_name", help="프로젝트 이름")
    p_init.add_argument("--agent-name", default="VULCAN", help="메인 에이전트 이름 (기본값: VULCAN)")

    subparsers.add_parser("check-trace", help="현재 Gate 정합성 검사")

    p_session = subparsers.add_parser("session", help="Gate 상태 업데이트 + git commit")
    p_session.add_argument("--gate", required=True, choices=list(GATE_LABELS.keys()), help="Gate 이름")
    p_session.add_argument("--status", required=True, choices=["done", "pending"], help="상태")
    p_session.add_argument("--feature", default="", help="작업 기능명")

    p_rollback = subparsers.add_parser("rollback", help="특정 Gate부터 재시작 (이후 Gate 모두 pending 리셋)")
    p_rollback.add_argument("--gate", required=True, choices=list(GATE_LABELS.keys()), help="재시작할 Gate")
    p_rollback.add_argument("--reason", default="", help="롤백 사유 (선택)")
    p_rollback.add_argument("--scope", default="", help="증분 rollback scope (REQ-ID 콤마 구분, 예: REQ-003,NREQ-005)")

    p_run_new = subparsers.add_parser("run-new", help="Codex/GPT Run 초안 생성")
    p_run_new.add_argument("--adapter", default="codex-gpt", help="Adapter 이름")
    p_run_new.add_argument("--gate", default="gate1", choices=list(GATE_LABELS.keys()), help="Gate 이름")
    p_run_new.add_argument("--persona", default="", choices=[""] + sorted(RUN_PERSONAS.keys()), help="Run persona")
    p_run_new.add_argument("--skill", required=True, choices=sorted(RUN_SKILLS.keys()), help="Run skill")
    p_run_new.add_argument("--title", required=True, help="Run 제목")
    p_run_new.add_argument("--related-ids", default="", help="관련 ID 콤마 구분")

    p_run_check = subparsers.add_parser("run-check", help="Run 결과 문서 검사")
    p_run_check.add_argument("run_file", help="검사할 Run 문서 경로")

    p_backlog = subparsers.add_parser("backlog", help="백로그 관리 (list/add/done/reject)")
    backlog_sub = p_backlog.add_subparsers(dest="backlog_cmd")
    backlog_sub.add_parser("list", help="백로그 Active 항목 나열")
    bl_add = backlog_sub.add_parser("add", help="새 백로그 항목 추가")
    bl_add.add_argument("--title", required=True)
    bl_add.add_argument("--level", default="", help="🟢/🟡/🔴 (선택, 나중에 Triage)")
    bl_add.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"])
    bl_add.add_argument("--req", default="")
    bl_add.add_argument("--source", default="")
    bl_add.add_argument("--note", default="")
    bl_done = backlog_sub.add_parser("done", help="백로그 항목 완료 처리")
    bl_done.add_argument("--id", dest="bl_id", required=True)
    bl_done.add_argument("--commit", dest="commit_hash", default="")
    bl_rej = backlog_sub.add_parser("reject", help="백로그 항목 반려")
    bl_rej.add_argument("--id", dest="bl_id", required=True)
    bl_rej.add_argument("--reason", default="")

    p_export = subparsers.add_parser("export", help="snapshot.json 생성")
    p_export.add_argument("--output", default="snapshot.json", help="출력 파일명")

    subparsers.add_parser("upgrade", help="프레임워크 파일 최신화")
    subparsers.add_parser("version", help="현재 프레임워크 버전 확인")

    p_release = subparsers.add_parser("release", help="Vulcan-Anvil로 코드 배포")
    p_release.add_argument("--target", required=True, help="배포 대상 경로 (예: ../Vulcan-Anvil)")

    args = parser.parse_args()

    if args.command == "init":
        init(
            target_dir=os.path.abspath(args.target_dir),
            project_name=args.project_name,
            agent_name=args.agent_name,
        )
    elif args.command == "check-trace":
        check_trace()
    elif args.command == "session":
        cmd_session(gate=args.gate, status=args.status, feature=args.feature)
    elif args.command == "rollback":
        cmd_rollback(gate=args.gate, reason=args.reason, scope=args.scope or None)
    elif args.command == "run-new":
        cmd_run_new(
            adapter=args.adapter,
            gate=args.gate,
            skill=args.skill,
            title=args.title,
            related_ids=args.related_ids,
            persona=args.persona or None,
        )
    elif args.command == "run-check":
        cmd_run_check(args.run_file)
    elif args.command == "backlog":
        if args.backlog_cmd == "list":
            cmd_backlog_list()
        elif args.backlog_cmd == "add":
            cmd_backlog_add(
                title=args.title, level=args.level, priority=args.priority,
                req=args.req, source=args.source, note=args.note,
            )
        elif args.backlog_cmd == "done":
            cmd_backlog_done(bl_id=args.bl_id, commit_hash=args.commit_hash)
        elif args.backlog_cmd == "reject":
            cmd_backlog_reject(bl_id=args.bl_id, reason=args.reason)
        else:
            p_backlog.print_help()
    elif args.command == "export":
        cmd_export(output=args.output)
    elif args.command == "upgrade":
        cmd_upgrade()
    elif args.command == "version":
        cmd_version()
    elif args.command == "release":
        cmd_release(target=args.target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
