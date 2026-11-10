"""Read-only QA projection. Importing a result never executes or approves a test."""

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path, PureWindowsPath
import re
import unicodedata


MAX_BYTES = 8 * 1024 * 1024
MAX_CASES = 10000
STATUSES = ("Pass", "Fail", "Blocked", "Not Run", "Unknown")
DIAGNOSTICS = {
    "unknown_status": "해석할 수 없는 원본 상태",
    "evidence_unavailable_or_unresolved": "증적 파일 누락 또는 참조 미해결",
    "missing_evidence_reference": "판정의 증적 참조 없음",
    "missing_actual_observation": "판정의 실제 관측 기록 없음",
    "reported_observation_mismatch": "원본 판정과 필수 관측 요약 불일치",
    "incomplete_observation_support": "통과로 기록된 관측의 기대값·실제값·증적 부족",
}
FIELDS = {
    "title": ("title", "시나리오"), "group": ("group", "업무화면"),
    "requirement": ("requirement", "REQ"), "ac": ("ac", "AC"),
    "source": ("source", "원본"), "source_location": ("source_location", "페이지절"),
    "scope": ("scope", "적용범위"), "basis": ("basis", "근거구분"),
    "role": ("role", "역할"), "preconditions": ("preconditions", "사전상태"),
    "input": ("input", "입력값"), "steps": ("steps", "절차"),
    "expected": ("expected", "단계별기대결과"), "postconditions": ("postconditions", "사후조건"),
    "method": ("method", "판정방법증적"), "cleanup": ("cleanup", "정리방법"),
    "actual": ("actual", "실행메모"), "blocker": ("blocker", "차단코드"),
    "executed_at": ("executed_at", "실행일"), "executor": ("executor", "실행자"),
}
LABELS = ("제목", "업무", "요구", "AC", "원문", "원문 위치", "적용 범위", "근거",
          "역할", "사전조건", "입력", "절차", "기대값", "사후조건", "확인 방법", "정리",
          "실제 관측", "차단 사유", "실행 일시", "실행자")
LIMITATIONS = [
    "원본 판정의 조회입니다. 시험 실행·의미상 커버리지·제품 인수 승인이 아닙니다.",
    "문장형 기대값을 자동 분해하거나 새로운 TC/AC를 만들지 않습니다.",
    "증적은 허용 범위 안의 파일 존재만 확인합니다. 내용·앵커·실행 대상 일치는 검토가 필요합니다.",
    "단위·통합·UI 시험의 검증 범위는 다릅니다. 테스트 개수를 요구 충족률로 계산하지 않습니다.",
    "개인정보·비밀값은 자동으로 제거되지 않습니다. 공유 전 선택 입력과 결과를 검토하세요.",
]


def _text(value):
    if value is None:
        return ""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _get(row, *names):
    for name in names:
        if name in row:
            return row[name]
    return None


def _status(value):
    key = re.sub(r"[_\s-]+", " ", _text(value).strip().lower())
    return {"pass": "Pass", "passed": "Pass", "fail": "Fail", "failed": "Fail",
            "blocked": "Blocked", "environment blocked": "Blocked", "not run": "Not Run",
            "not executed": "Not Run", "planned": "Not Run", "pending": "Not Run"}.get(key, "Unknown")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _safe_file(root, relative):
    """Resolve Unicode-equivalent filenames, never links or paths outside root."""
    current = root
    for part in relative.parts:
        candidate = current / part
        if not candidate.exists() and not candidate.is_symlink() and current.is_dir():
            matches = [p for p in current.iterdir()
                       if unicodedata.normalize("NFC", p.name) == unicodedata.normalize("NFC", part)]
            if len(matches) > 1:
                raise ValueError("ambiguous Unicode path")
            if matches:
                candidate = matches[0]
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise ValueError("symlink/junction evidence is not supported")
        current = candidate
    if not current.resolve().is_relative_to(root):
        raise ValueError("path outside evidence root")
    return current


def _references(value):
    if value is None or value == "":
        return []
    if isinstance(value, list):
        if not all(isinstance(item, str) for item in value):
            raise ValueError("evidence must contain path strings")
        return value
    if not isinstance(value, str):
        raise ValueError("evidence must be a string or list of paths")
    value = re.sub(r"\[[^\]]*\]\(([^)]+)\)", r"\1", value)
    # Legacy reports use ' / ' between references; do not split path separators.
    return [part.strip().strip('`') for part in re.split(r"\s+/\s+|[;\n]", value) if part.strip()]


def _evidence(value, base, root):
    result = []
    for ref in _references(value):
        entry = {"ref": ref, "status": "unresolved"}
        name = ref.split("#", 1)[0]
        win = PureWindowsPath(name)
        if (not name or "\x00" in name or ":" in name or win.drive or win.is_absolute()
                or name.startswith(("/", "\\"))):
            entry["status"] = "unsafe"
        elif not Path(name).suffix:
            entry["status"] = "unresolved"  # A RUN-ID is not a file reference.
        else:
            try:
                # Normalize '..' lexically, then check each component for links.
                import os
                lexical = Path(os.path.abspath(base / name.replace("\\", "/")))
                relative = lexical.relative_to(root)
                if any(p in {".git", "node_modules", ".venv"} or p.startswith(".env")
                       for p in relative.parts):
                    raise ValueError("excluded evidence path")
                path = _safe_file(root, relative)
                entry["status"] = "available" if path.is_file() else "missing"
            except (ValueError, OSError):
                entry["status"] = "unsafe"
        result.append(entry)
    return result


def _observations(value, base, root):
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 500:
        raise ValueError("observations must be a list of at most 500 entries")
    result, seen = [], set()
    for row in value:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError("observation requires a nonempty local id")
        key = row["id"].strip()
        if key in seen or type(row.get("required", True)) is not bool:
            raise ValueError("duplicate observation id or non-boolean required")
        seen.add(key)
        result.append({"id": key, "required": row.get("required", True),
                       "step": _text(row.get("step")), "expected": _text(row.get("expected")),
                       "actual": _text(row.get("actual")), "status": _status(row.get("status")),
                       "evidence": _evidence(row.get("evidence"), base, root)})
    return result


def _observation_summary(rows):
    required = [r for r in rows if r["required"]]
    if not required:
        return "Not structured"
    statuses = {r["status"] for r in required}
    if "Fail" in statuses:
        return "Fail"
    if "Blocked" in statuses:
        return "Blocked"
    if statuses != {"Pass"} or any(not r["actual"].strip() or not r["expected"].strip() for r in required):
        return "Not Run"
    return "Pass"


def collect(input_file, evidence_root=None):
    source = Path(input_file).resolve(strict=True)
    root = Path(evidence_root).resolve(strict=True) if evidence_root else source.parent
    if not root.is_dir() or not source.is_relative_to(root):
        raise ValueError("input must be inside the explicitly selected evidence root")
    if not source.is_file() or source.suffix.lower() != ".json" or source.stat().st_size > MAX_BYTES:
        raise ValueError("input must be a JSON file of at most 8 MiB")
    raw = source.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    if isinstance(data, dict):
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1 or not isinstance(data.get("cases"), list):
            raise ValueError("expected a case array or schema_version: 1 with cases")
        data = data["cases"]
    if not isinstance(data, list) or len(data) > MAX_CASES:
        raise ValueError("input must contain at most 10000 cases")
    cases, seen = [], set()
    for row in data:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError("every case requires a nonempty string id")
        key = row["id"].strip()
        canonical = unicodedata.normalize("NFC", key)
        if canonical in seen:
            raise ValueError("duplicate case id: " + key)
        seen.add(canonical)
        case = {name: _text(_get(row, *aliases)) for name, aliases in FIELDS.items()}
        original = _text(_get(row, "status", "상태"))
        case.update(id=key, original_status=original, reported_status=_status(original),
                    evidence=_evidence(_get(row, "evidence", "실행증적"), source.parent, root),
                    observations=_observations(row.get("observations"), source.parent, root))
        case["observation_summary"] = _observation_summary(case["observations"])
        diagnostics = []
        if case["reported_status"] == "Unknown":
            diagnostics.append("unknown_status")
        refs = case["evidence"] + [e for o in case["observations"] for e in o["evidence"]]
        if any(e["status"] != "available" for e in refs):
            diagnostics.append("evidence_unavailable_or_unresolved")
        if case["reported_status"] in {"Pass", "Fail"} and not refs:
            diagnostics.append("missing_evidence_reference")
        if case["reported_status"] in {"Pass", "Fail"} and not case["actual"].strip() and not any(
                o["actual"].strip() for o in case["observations"]):
            diagnostics.append("missing_actual_observation")
        if (case["observation_summary"] != "Not structured"
                and case["observation_summary"] != case["reported_status"]):
            diagnostics.append("reported_observation_mismatch")
        if any(o["required"] and o["status"] == "Pass" and (
                not o["expected"].strip() or not o["actual"].strip() or not o["evidence"]
                or any(e["status"] != "available" for e in o["evidence"])) for o in case["observations"]):
            diagnostics.append("incomplete_observation_support")
        case["diagnostics"] = diagnostics
        cases.append(case)
    counts = Counter(c["reported_status"] for c in cases)
    return {"schema_version": 1, "kind": "qa_readonly_projection",
            "generated_at": datetime.now(timezone.utc).isoformat(), "source": source.name,
            "source_count": len(cases), "tests_executed": False, "acceptance_authorized": False,
            "summary": {"reported": {s: counts[s] for s in STATUSES},
                        "scopes": dict(Counter(c["scope"] or "Unspecified" for c in cases)),
                        "blockers": dict(Counter(c["blocker"] or "Unspecified" for c in cases if c["reported_status"] == "Blocked")),
                        "diagnostic_cases": sum(bool(c["diagnostics"]) for c in cases),
                        "unstructured_cases": sum(c["observation_summary"] == "Not structured" for c in cases)},
            "limitations": LIMITATIONS, "cases": cases}


def render_html(report):
    def cell(value):
        return escape(_text(value), quote=True)

    def refs(values):
        labels = {"available": "파일 있음·내용 미검증", "missing": "파일 없음",
                  "unresolved": "파일 참조 확인 필요", "unsafe": "허용 범위 밖 또는 지원하지 않는 경로"}
        return "<br>".join(cell(e["ref"]) + " [" + cell(labels[e["status"]]) + "]" for e in values) or "없음"

    items = []
    for case in report["cases"]:
        fields = "".join(f"<tr><th>{label}</th><td>{cell(case[name])}</td></tr>"
                         for name, label in zip(FIELDS, LABELS) if case[name])
        observations = "".join("<tr><td>" + ("필수" if o["required"] else "참고") + "</td>" + "".join(f"<td>{cell(o[k])}</td>" for k in (
            "id", "step", "expected", "actual", "status")) + f"<td>{refs(o['evidence'])}</td></tr>"
                               for o in case["observations"])
        obs = ("<div class='scroll'><table><thead><tr>" + "".join(f"<th>{s}</th>" for s in (
            "구분", "확인 항목", "단계", "기대값", "실제 관측", "기록 결과", "증적")) +
               "</tr></thead><tbody>" + observations + "</tbody></table></div>" if observations else
               "<p>단계별 구조화 결과 없음. 원문 절차·기대값을 그대로 확인하세요. 새 표 작성 의무는 아닙니다.</p>")
        search = " ".join(case[k] for k in ("id", *FIELDS))
        items.append(f"<details data-status='{cell(case['reported_status'])}' data-diagnostic='{int(bool(case['diagnostics']))}' data-search='{cell(search.lower())}'>"
                     f"<summary><strong>{cell(case['id'])}</strong> {cell(case['title'])} <span>{cell(case['reported_status'])}</span></summary>"
                     f"<div class='detail'><p>원본 판정: {cell(case['original_status'])} / 필수 관측 요약: {cell(case['observation_summary'])}</p>"
                     f"<p class='notice'>진단: {cell(', '.join(DIAGNOSTICS[d] for d in case['diagnostics']) or '기계적 진단 없음. 완전성 보증 아님')}</p>"
                     f"<table><tbody>{fields}</tbody></table><h3>실행 증적 경로</h3><p>{refs(case['evidence'])}</p>"
                     f"<h3>단계별 확인 항목</h3>{obs}</div></details>")
    totals = " / ".join(f"{s} {report['summary']['reported'][s]}" for s in STATUSES)
    return """<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>QA 결과 검토</title><style>
*{box-sizing:border-box}body{margin:0;font:15px/1.6 system-ui,sans-serif;color:#20252b;background:#fafbfc;letter-spacing:0}
main{max-width:1180px;margin:auto;padding:24px}h1{font-size:25px;margin:0}h2{font-size:19px}h3{font-size:16px}p{overflow-wrap:anywhere}
header{border-bottom:2px solid #087f72;padding-bottom:16px}header p{margin:8px 0}.notice{color:#85550b;background:#fff5de;padding:8px}
.filters{display:flex;gap:12px;flex-wrap:wrap;background:#fafbfc;padding:16px 0;align-items:end}
label{display:grid;gap:4px}input,select{font:inherit;padding:8px;min-height:42px;max-width:100%;border:1px solid #8c969f;border-radius:4px}
input[type=search]{width:360px}input[type=checkbox]{min-height:auto}label.check{display:flex;align-items:center}
details{border-bottom:1px solid #d1d9df}summary{cursor:pointer;padding:14px 4px;overflow-wrap:anywhere}summary strong{color:#066b60}summary span{font-weight:600;margin-left:12px}
.detail{padding:0 12px 20px}table{width:100%;border-collapse:collapse;table-layout:fixed}td,th{text-align:left;vertical-align:top;border:1px solid #d1d9df;padding:8px;white-space:pre-wrap;overflow-wrap:anywhere}th{background:#edf3f3}tbody th{width:130px}.scroll{overflow:auto}.scroll table{min-width:720px}
[hidden]{display:none!important}@media(max-width:600px){main{padding:14px}.filters>label{width:100%}input[type=search]{width:100%}tbody th{width:90px}.detail{padding:0 0 16px}}
</style><main><header><h1>QA 결과 검토</h1>""" + (
        f"<p>{cell(report['source'])} / 생성: {cell(report['generated_at'])}</p>"
        f"<p>원본 전체 {report['source_count']}건 · {cell(totals)}</p>"
        f"<p>진단 대상 {report['summary']['diagnostic_cases']}건 / 단계별 결과 미구조화 {report['summary']['unstructured_cases']}건</p>"
        f"<p>적용 범위: {cell(' / '.join(f'{k}: {v}' for k, v in report['summary']['scopes'].items()))}</p>"
        f"<p>차단 사유: {cell(' / '.join(f'{k}: {v}' for k, v in report['summary']['blockers'].items())) or '없음'}</p>"
        "<p class='notice'>읽기 전용 스냅샷 · 시험을 실행하거나 원본 판정·인수 상태를 변경하지 않습니다.</p></header>"
        "<div class='filters'><label>검색<input id='search' type='search' placeholder='TC, REQ, AC, 제목, 관측'></label>"
        "<label>원본 결과<select id='status'><option value=''>전체</option>" +
        "".join(f"<option>{s}</option>" for s in STATUSES) +
        "</select></label><label class='check'><input id='diagnostic' type='checkbox'>진단 있는 항목만</label></div>"
        f"<p id='count' aria-live='polite'>표시 {report['source_count']} / 전체 {report['source_count']}</p>" +
        "".join(items) + "<h2>해석 범위</h2><ul>" +
        "".join(f"<li>{cell(item)}</li>" for item in report["limitations"]) + "</ul></main>" +
        """<script>
const search=document.getElementById('search'),status=document.getElementById('status'),diagnostic=document.getElementById('diagnostic');
const cases=[...document.querySelectorAll('details')];
function filter(){let n=0;for(const item of cases){const show=(!status.value||item.dataset.status===status.value)&&(!diagnostic.checked||item.dataset.diagnostic==='1')&&item.dataset.search.includes(search.value.toLowerCase());item.hidden=!show;if(show)n++;}document.getElementById('count').textContent=`표시 ${n} / 전체 ${cases.length}`;}
for(const input of [search,status,diagnostic])input.addEventListener('input',filter);
</script></html>""")


def export(input_file, output, format="json", evidence_root=None):
    if format not in {"json", "html"}:
        raise ValueError("QA export format must be json or html")
    report = collect(input_file, evidence_root)
    target = Path(output)
    if target.suffix.lower() != "." + format or not target.parent.is_dir():
        raise ValueError("output must be a new matching file in an existing directory")
    content = json.dumps(report, ensure_ascii=False, indent=2) if format == "json" else render_html(report)
    # Exclusive creation also protects the input and all prior results from replacement.
    with target.open("x", encoding="utf-8") as stream:
        stream.write(content)
    return report
