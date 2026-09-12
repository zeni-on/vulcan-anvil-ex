"""Prove the preservation test detects a real temporary implementation defect."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    needle = """                       (body.content, request_id))
            result = view(db, row_for(db, request_id, user))"""
    if source.count(needle) != 1:
        raise RuntimeError("Mutation target changed; review the negative probe")
    changed = source.replace(needle, """                       (body.content, request_id))
            db.execute("UPDATE decisions SET content=? WHERE request_id=?", (body.content, request_id))
            result = view(db, row_for(db, request_id, user))""")
    with tempfile.TemporaryDirectory(prefix="request-board-negative-") as folder:
        root = Path(folder)
        (root / "app.py").write_text(changed, encoding="utf-8")
        shutil.copyfile(ROOT / "tests/test_api.py", root / "test_api.py")
        result = subprocess.run([sys.executable, "-B", "-m", "unittest",
            "test_api.RequestFlowTests.test_reg_001_preserves_original_content_and_reason_after_resubmit", "-v"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        print(result.stdout, end="")
        print(result.stderr, end="")
        if result.returncode != 1 or "AssertionError" not in result.stderr or "FAILED (failures=1)" not in result.stderr:
            raise RuntimeError("Expected the history-preservation assertion to fail, not an environment or import error")
    print("Expected history regression detected; application source and user databases unchanged.")


if __name__ == "__main__":
    main()
