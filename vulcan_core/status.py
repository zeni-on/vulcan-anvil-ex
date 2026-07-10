"""Read-only status composition and rendering for Vulcan-Anvil Ex."""

import json
import os


def implementation_display_counts(implementation):
    implementation = implementation or {}
    reqs = implementation.get("requirements", {}) if isinstance(implementation, dict) else {}
    waves = implementation.get("waves", {}) if isinstance(implementation, dict) else {}
    implemented = reqs.get("implemented", implementation.get("implemented", 0) if isinstance(implementation, dict) else 0)
    total = reqs.get("total", implementation.get("total", 0) if isinstance(implementation, dict) else 0)
    percent = implementation.get("percent", 0) if isinstance(implementation, dict) else 0
    if not percent and total:
        percent = int((implemented / total) * 100)
    return {
        "implemented": implemented,
        "total": total,
        "percent": percent,
        "waves_completed": waves.get("completed", implementation.get("waves_completed", 0) if isinstance(implementation, dict) else 0),
        "waves_total": waves.get("total", implementation.get("waves_total", 0) if isinstance(implementation, dict) else 0),
        "waves_current": waves.get("current", ""),
    }


def collect_model_fallbacks(project_dir="."):
    exec_dir = os.path.join(os.path.abspath(project_dir), "docs", "runs", "_exec")
    if not os.path.isdir(exec_dir):
        return []

    candidates = []
    try:
        for name in os.listdir(exec_dir):
            if not name.endswith((".json", ".jsonl")):
                continue
            path = os.path.join(exec_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as file_obj:
                    if name.endswith(".jsonl"):
                        rows = [
                            json.loads(line)
                            for line in file_obj
                            if line.strip().startswith("{")
                        ]
                        payload = rows[-1] if rows else {}
                    else:
                        payload = json.load(file_obj)
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            reason = str(payload.get("model_fallback_reason") or "").strip()
            if not reason:
                continue
            target_id = (
                payload.get("target_id")
                or payload.get("run_id")
                or payload.get("review_id")
                or "-"
            )
            candidates.append({
                "target_id": target_id,
                "runner": payload.get("runner") or "-",
                "model": payload.get("model") or "-",
                "reasoning_effort": payload.get("reasoning_effort") or "",
                "model_source": payload.get("model_source") or "",
                "model_fallback_reason": reason,
                "status": payload.get("status") or "",
                "path": os.path.relpath(path, os.path.abspath(project_dir)).replace("\\", "/"),
                "mtime": os.path.getmtime(path),
            })
    except Exception:
        return []

    seen = set()
    deduped = []
    for item in sorted(candidates, key=lambda value: value.get("mtime") or 0, reverse=True):
        key = (item.get("target_id"), item.get("runner"), item.get("model_fallback_reason"))
        if key in seen:
            continue
        seen.add(key)
        item.pop("mtime", None)
        deduped.append(item)
        if len(deduped) >= 5:
            break
    return deduped


def _truncate_message(value, limit=90):
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def collect_dashboard_comments(project_dir="."):
    comments_path = os.path.join(os.path.abspath(project_dir), ".vulcan", "comments", "comments.jsonl")
    summary = {
        "path": ".vulcan/comments/comments.jsonl",
        "total": 0,
        "open": 0,
        "closed": 0,
        "items": [],
    }
    if not os.path.exists(comments_path):
        return summary

    try:
        with open(comments_path, "r", encoding="utf-8") as file_obj:
            for line in file_obj:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except Exception:
                    continue
                status = str(item.get("status") or "open").strip().lower()
                if status in ("resolved", "converted", "stale"):
                    status = "closed"
                if status not in ("open", "closed"):
                    status = "open"
                summary["total"] += 1
                summary[status] += 1
                if status == "open":
                    anchor = item.get("anchor") if isinstance(item.get("anchor"), dict) else {}
                    summary["items"].append({
                        "comment_id": item.get("comment_id") or "",
                        "document": item.get("document") or "",
                        "category": item.get("category") or "note",
                        "line": anchor.get("start_line") or "",
                        "body": _truncate_message(item.get("body") or "", limit=90),
                    })
    except Exception:
        summary["read_error"] = True
    return summary


def status_next_actions(
    *,
    session_exists,
    current_gate,
    current_branch,
    integration_branch,
    active_waves,
    known_gates,
    profile_gap=None,
    gap_target="product",
    qa_workspace_followup=None,
):
    next_actions = []
    if not session_exists:
        next_actions.extend([
            "python vulcan.py init <target-dir> <project-name>",
            "python vulcan.py version",
        ])
    elif current_gate == "completed":
        next_actions.append("프로젝트 완료: 추가 Gate 전환 없음")
    else:
        next_actions.append("python vulcan.py status --check")

    if current_gate == "impl":
        if current_branch != integration_branch:
            next_actions.insert(0, "python vulcan.py branch-start impl")
        elif active_waves:
            next_actions.insert(0, "python vulcan.py wave-complete <BW-ID> --status Verified")
        else:
            next_actions.insert(0, "python vulcan.py wave-start <BW-ID> --trace-seed <ID>")
    elif current_gate in ("gate4", "gate5"):
        next_actions.insert(0, "python vulcan.py prepare-transition")
    elif current_gate in known_gates:
        next_actions.insert(0, f"python vulcan.py session --gate {current_gate} --status done --approved --approval-evidence \"<승인 근거>\"")

    gap_summary = profile_gap.get("summary", {}) if isinstance(profile_gap, dict) else {}
    if current_gate in known_gates and (
        gap_summary.get("content_issues", 0) > 0 or gap_summary.get("missing", 0) > 0
    ):
        preferred_actions = [
            "python vulcan.py status --check",
            f"python vulcan.py profile-gap --to {gap_target}",
        ]
        next_actions = preferred_actions + [
            action for action in next_actions
            if action not in preferred_actions and not action.startswith("python vulcan.py session --gate")
        ]

    if qa_workspace_followup:
        preferred_actions = [
            "QA-000 doctor JSON/evidence 확인",
            "환경 문제는 ISSUE/environment_blocked로 보류",
            "제품 수정 필요 시 qa-fix-loop 생성",
        ]
        next_actions = preferred_actions + [
            action for action in next_actions
            if action not in preferred_actions
        ]
    return next_actions[:3]


def compose_status_summary(
    *,
    project,
    profile,
    current_gate,
    gate_status,
    current_branch,
    main_branch,
    integration_branch,
    branch_mode,
    impl_uses_integration_branch,
    session_branch_role,
    qa_workspace,
    qa_workspace_followup,
    dirty_blocking,
    integration_exists,
    implementation,
    active_runs,
    active_waves,
    profile_gap,
    dashboard_comments,
    model_fallbacks,
    session_exists,
    known_gates,
    gap_target,
):
    return {
        "project": project,
        "profile": profile,
        "current_gate": current_gate,
        "gate_status": gate_status,
        "current_branch": current_branch,
        "main_branch": main_branch,
        "integration_branch": integration_branch,
        "branch_mode": branch_mode,
        "impl_uses_integration_branch": impl_uses_integration_branch,
        "session_branch_role": session_branch_role,
        "qa_workspace": qa_workspace,
        "qa_workspace_followup": qa_workspace_followup,
        "dirty_blocking": dirty_blocking,
        "integration_exists": integration_exists,
        "implementation": implementation,
        "active_runs": active_runs,
        "active_waves": active_waves,
        "profile_gap": profile_gap,
        "dashboard_comments": dashboard_comments,
        "model_fallbacks": model_fallbacks,
        "next_actions": status_next_actions(
            session_exists=session_exists,
            current_gate=current_gate,
            current_branch=current_branch,
            integration_branch=integration_branch,
            active_waves=active_waves,
            known_gates=known_gates,
            profile_gap=profile_gap,
            gap_target=gap_target,
            qa_workspace_followup=qa_workspace_followup,
        ),
    }


def render_status_report(summary):
    lines = [
        "==================================================",
        " [status] Vulcan Orchestrator status",
        "==================================================",
        f" project: {summary['project']}",
        f" profile: {summary['profile']}",
        f" current_gate: {summary['current_gate']}",
        f" gate_status: {summary['gate_status']}",
        "",
        " branch",
        f"  current_branch: {summary['current_branch']}",
        f"  main_branch: {summary['main_branch']}",
        f"  integration_branch: {summary['integration_branch']}",
        f"  integration_exists: {summary['integration_exists']}",
        f"  dirty_blocking: {summary['dirty_blocking']}",
        f"  session_branch_role: {summary['session_branch_role']}",
    ]
    qa_state = summary.get("qa_workspace") or {}
    if qa_state:
        lines.extend([
            " qa_workspace",
            f"  path: {qa_state.get('path') or '-'}",
            f"  mode: {qa_state.get('mode') or '-'}",
            f"  status: {qa_state.get('status') or '-'}",
            f"  last_stage: {qa_state.get('last_stage') or '-'}",
        ])
        followup = summary.get("qa_workspace_followup") or []
        if followup:
            lines.append("  followup")
            lines.extend(f"   - {item}" for item in followup)
    lines.append("")

    implementation = summary.get("implementation") or {}
    if implementation:
        impl_counts = implementation_display_counts(implementation)
        lines.extend([
            " implementation",
            f"  implemented: {impl_counts['implemented']} / {impl_counts['total']}",
            f"  percent: {impl_counts['percent']}",
            f"  waves: {impl_counts['waves_completed']} / {impl_counts['waves_total']}",
        ])
        if impl_counts["waves_current"]:
            lines.append(f"  current_wave: {impl_counts['waves_current']}")
        lines.append("")

    active_runs = summary.get("active_runs") or []
    lines.append(f" active_runs: {len(active_runs)}")
    lines.extend(f"  - {run['path']} ({run['status']})" for run in active_runs[:5])
    if len(active_runs) > 5:
        lines.append(f"  ... 외 {len(active_runs) - 5}건")

    active_waves = summary.get("active_waves") or []
    lines.append(f" active_waves: {len(active_waves)}")
    for wave in active_waves[:5]:
        run_suffix = f" / {wave.get('run')}" if wave.get("run") else ""
        lines.append(f"  - {wave.get('id')} ({wave.get('status')}){run_suffix}")
    if len(active_waves) > 5:
        lines.append(f"  ... 외 {len(active_waves) - 5}건")
    lines.append("")

    model_fallbacks = summary.get("model_fallbacks") or []
    if model_fallbacks:
        lines.append(" model_fallbacks")
        for item in model_fallbacks[:5]:
            effort = f" / {item.get('reasoning_effort')}" if item.get("reasoning_effort") else ""
            source = f" ({item.get('model_source')})" if item.get("model_source") else ""
            lines.append(f"  - {item.get('target_id')} {item.get('runner')}: {item.get('model')}{effort}{source}")
            lines.append(f"    reason: {item.get('model_fallback_reason')}")
        lines.append("")

    profile_gap = summary.get("profile_gap") or {}
    if profile_gap:
        gap_summary = profile_gap.get("summary") or {}
        lines.extend([
            " profile_gap",
            f"  target_profile: {profile_gap.get('target_profile') or '-'}",
            "  docs: "
            f"ok {gap_summary.get('ok', 0)}, "
            f"partial {gap_summary.get('partial', 0)}, "
            f"missing {gap_summary.get('missing', 0)}",
            "  content: "
            f"issues {gap_summary.get('content_issues', 0)}, "
            f"warnings {gap_summary.get('content_warnings', 0)}",
        ])
        if profile_gap.get("read_error"):
            lines.append(f"  read_error: {profile_gap.get('read_error')}")
        lines.append("")

    comments = summary.get("dashboard_comments") or {}
    if comments.get("total"):
        lines.extend([
            " dashboard_comments",
            f"  path: {comments.get('path')}",
            f"  open: {comments.get('open', 0)} / total: {comments.get('total', 0)} (closed {comments.get('closed', 0)})",
        ])
        for item in (comments.get("items") or [])[:5]:
            line = f":L{item.get('line')}" if item.get("line") else ""
            lines.append(f"  - {item.get('comment_id') or '-'} [{item.get('category')}] {item.get('document')}{line} - {item.get('body')}")
        if comments.get("open", 0) > 5:
            lines.append(f"  ... 외 {comments.get('open', 0) - 5}건")
        lines.append("")

    lines.append(" next_actions")
    lines.extend(f"  - {action}" for action in summary.get("next_actions") or [])
    lines.append("==================================================")
    return "\n".join(lines)
