"""Real application checks in two processes sharing one disposable SQLite file."""

from contextlib import ExitStack
import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app


def run(stage):
    runtime = ROOT / "runtime"
    runtime.mkdir(exist_ok=True)
    app = create_app(runtime / "requests.sqlite3", demo_enabled=True)
    with ExitStack() as stack:
        def client(actor):
            value = stack.enter_context(TestClient(app, base_url="http://127.0.0.1",
                headers={"Origin": "http://127.0.0.1"}))
            assert value.post("/api/demo/session", json={"userId": actor}).status_code == 200
            return value

        alice, bob, reviewer = client("alice"), client("bob"), client("carol")

        def post(who, path, body, expected=200):
            response = who.post(path, json=body)
            assert response.status_code == expected, response.text
            return response.json()

        def decide(row, decision):
            return post(reviewer, f"/api/requests/{row['id']}/decision", {
                "decision": decision, "reason": "Specify quantity" if decision == "rejected" else "",
                "version": row["version"]})

        if stage == "baseline":
            rows = []
            for state in ("submitted", "rejected", "approved"):
                row = post(alice, "/api/requests", {"content": "Equipment: " + state}, 201)
                rows.append(row if state == "submitted" else decide(row, state))
            rejected = rows[1]
            amended = post(alice, f"/api/requests/{rejected['id']}/resubmit", {
                "content": "Equipment: two units (baseline)", "version": rejected["version"]})
            assert amended["id"] == rejected["id"] and amended["status"] == "submitted"
            assert amended["content"] == "Equipment: two units (baseline)"
            assert amended["history"] == rejected["history"]
            rows[1] = decide(amended, "rejected")
            assert rows[1]["history"][:-1] == rejected["history"]
            for who, expected in ((bob, 404), (reviewer, 403)):
                response = who.post(f"/api/requests/{rows[1]['id']}/resubmit", json={
                    "content": "Unauthorized amendment", "version": rows[1]["version"]})
                assert response.status_code == expected
            assert bob.get(f"/api/requests/{rows[1]['id']}").status_code == 404
            assert alice.get(f"/api/requests/{rows[1]['id']}").json() == rows[1]
            foreign = decide(post(bob, "/api/requests", {"content": "Other owner's equipment"}, 201), "rejected")
            assert [r["id"] for r in alice.get("/api/requests").json()["requests"]] == [r["id"] for r in reversed(rows)]
            assert alice.get(f"/api/requests/{foreign['id']}").status_code == 404
            assert rows[1]["history"][0]["content"] == "Equipment: rejected"
            assert rows[1]["history"][0]["reason"] == "Specify quantity"
            (runtime / "baseline.json").write_text(json.dumps({"rows": rows, "foreign": foreign}), encoding="utf-8")
        else:
            saved = json.loads((runtime / "baseline.json").read_text(encoding="utf-8"))
            rows, foreign = saved["rows"], saved["foreign"]
            for row in rows:
                assert alice.get(f"/api/requests/{row['id']}").json() == row
                result = alice.get("/api/requests", params={"status": row["status"]})
                assert result.status_code == 200
                assert [r["id"] for r in result.json()["requests"]] == [row["id"]]
            assert [r["id"] for r in bob.get("/api/requests?status=rejected").json()["requests"]] == [foreign["id"]]
            assert {r["id"] for r in reviewer.get("/api/requests?status=rejected").json()["requests"]} == {rows[1]["id"], foreign["id"]}
            for invalid in ("", "deleted", "rejected' OR 1=1 --"):
                response = alice.get("/api/requests", params={"status": invalid})
                assert response.status_code == 422 and response.json()["error"]["code"] == "INVALID_INPUT"
            original = rows[1]
            assert alice.get(f"/api/requests/{original['id']}").json() == original
            amended = post(alice, f"/api/requests/{original['id']}/resubmit", {
                "content": "Equipment: three units", "version": original["version"]})
            assert amended["id"] == original["id"] and amended["history"] == original["history"]
            assert amended["content"] == "Equipment: three units" and amended["status"] == "submitted"
            assert alice.get("/api/requests?status=rejected").json()["requests"] == []
            assert {r["id"] for r in alice.get("/api/requests?status=submitted").json()["requests"]} == {rows[0]["id"], original["id"]}
            rejected = decide(amended, "rejected")
            assert rejected["history"][:-1] == original["history"]
            assert rejected["history"][-1]["content"] == "Equipment: three units"
            assert [h["round"] for h in rejected["history"]] == [1, 2, 3]
            (runtime / "extension.json").write_text(json.dumps(rejected), encoding="utf-8")
    print(json.dumps({"stage": stage, "status": "passed", "shared_database": True}))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"baseline", "extension"}:
        raise SystemExit("Expected baseline or extension")
    run(sys.argv[1])
