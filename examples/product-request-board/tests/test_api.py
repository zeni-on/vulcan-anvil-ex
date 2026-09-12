"""API/SQLite assertions for the agreed local sample, using disposable databases."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app import COOKIE, create_app


class RequestFlowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db_path = Path(temp.name) / "requests.sqlite3"
        self.app = create_app(self.db_path, demo_enabled=True)
        self.alice = self.client("alice")
        self.carol = self.client("carol")

    def client(self, name=None, app=None):
        client = TestClient(app or self.app, base_url="http://127.0.0.1", headers={"Origin": "http://127.0.0.1"})
        self.addCleanup(client.close)
        if name:
            response = client.post("/api/demo/session", json={"userId": name})
            self.assertEqual(response.status_code, 200, response.text)
        return client

    def create(self, content="장비 필요", client=None):
        response = (client or self.alice).post("/api/requests", json={"content": content})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def decide(self, row, reason="수량을 알려주세요", *, client=None, decision="rejected"):
        response = (client or self.carol).post(f"/api/requests/{row['id']}/decision",
            json={"decision": decision, "reason": reason, "version": row["version"]})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def resubmit(self, row, content="장비 2대 필요"):
        response = self.alice.post(f"/api/requests/{row['id']}/resubmit", json={"content": content, "version": row["version"]})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def stored(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            return (db.execute("SELECT * FROM requests ORDER BY id").fetchall(),
                    db.execute("SELECT * FROM decisions ORDER BY request_id,round").fetchall())

    def test_reg_001_preserves_original_content_and_reason_after_resubmit(self):
        original = self.create()
        rejected = self.decide(original)
        updated = self.resubmit(rejected)
        self.assertEqual((updated["id"], updated["content"], updated["status"]), (original["id"], "장비 2대 필요", "submitted"))
        self.assertEqual(updated["history"], rejected["history"])
        self.assertEqual(updated["history"][0]["content"], "장비 필요")
        self.assertEqual(updated["history"][0]["reason"], "수량을 알려주세요")
        self.assertIsNone(updated["reason"])

    def test_reg_002_repeated_rejection_survives_new_application_instance(self):
        row = self.resubmit(self.decide(self.create()))
        row = self.decide(row, "예산을 확인하세요", client=self.client("dana"))
        row = self.resubmit(row, "장비 2대, 예산 확인 완료")
        row = self.decide(row, reason="", decision="approved")
        restarted = self.client("alice", create_app(self.db_path, demo_enabled=True))
        saved = restarted.get(f"/api/requests/{row['id']}").json()
        self.assertEqual(saved, row)
        self.assertEqual([h["round"] for h in saved["history"]], [1, 2, 3])
        self.assertEqual([h["content"] for h in saved["history"]], ["장비 필요", "장비 2대 필요", "장비 2대, 예산 확인 완료"])
        self.assertEqual(saved["history"][1]["reason"], "예산을 확인하세요")
        self.assertEqual(saved["history"][1]["reviewer"]["id"], "dana")

    def test_sec_reg_001_visibility_and_other_actors_cannot_mutate(self):
        row = self.decide(self.create())
        bob = self.client("bob")
        before = self.stored()
        self.assertEqual(bob.get("/api/requests").json(), {"requests": []})
        self.assertEqual(bob.get(f"/api/requests/{row['id']}").status_code, 404)
        self.assertEqual(bob.post(f"/api/requests/{row['id']}/resubmit", json={"content": "stolen", "version": row["version"]}).status_code, 404)
        self.assertEqual(self.carol.post(f"/api/requests/{row['id']}/resubmit", json={"content": "changed", "version": row["version"]}).status_code, 403)
        self.assertEqual(self.stored(), before)

    def test_sec_reg_002_self_review_and_requester_review_are_forbidden(self):
        own = self.create(client=self.carol)
        other = self.create()
        before = self.stored()
        for client, row in ((self.carol, own), (self.alice, other)):
            result = client.post(f"/api/requests/{row['id']}/decision", json={"decision": "approved", "version": row["version"]})
            self.assertEqual(result.status_code, 403)
        self.assertEqual(self.stored(), before)

    def test_reg_003_stale_duplicate_and_invalid_state_are_nonmutating(self):
        initial = self.create()
        rejected = self.decide(initial)
        before = self.stored()
        self.assertEqual(self.carol.post(f"/api/requests/{initial['id']}/decision",
            json={"decision": "approved", "version": initial["version"]}).status_code, 409)
        self.assertEqual(self.stored(), before)
        updated = self.resubmit(rejected)
        before = self.stored()
        for version in (rejected["version"], updated["version"]):
            result = self.alice.post(f"/api/requests/{updated['id']}/resubmit", json={"content": "changed", "version": version})
            self.assertEqual(result.status_code, 409)
        self.assertEqual(self.stored(), before)
        approved = self.decide(updated, "", decision="approved")
        self.assertEqual(self.alice.post(f"/api/requests/{approved['id']}/resubmit", json={"content": "changed", "version": approved["version"]}).status_code, 409)

    def test_reg_004_concurrent_review_has_one_winner_and_one_snapshot(self):
        row = self.create()
        dana = self.client("dana")
        def post(client):
            return client.post(f"/api/requests/{row['id']}/decision", json={"decision": "rejected", "reason": "review", "version": row["version"]}).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertCountEqual(list(pool.map(post, (self.carol, dana))), [200, 409])
        self.assertEqual(len(self.stored()[1]), 1)

    def test_sec_reg_003_invalid_input_and_actor_override_do_not_write(self):
        row = self.create()
        before = self.stored()
        for body in ({"content": " "}, {"content": "x" * 4001}, {"content": "a", "owner": "bob"}):
            self.assertEqual(self.alice.post("/api/requests", json=body).status_code, 422)
        for body in ({"decision": "rejected", "reason": " ", "version": 1},
                     {"decision": "approved", "version": True}, {"decision": "approved", "version": "1"},
                     {"decision": "approved", "version": 1, "actor": "dana"}):
            self.assertEqual(self.carol.post(f"/api/requests/{row['id']}/decision", json=body).status_code, 422)
        self.assertEqual(self.carol.get("/api/requests/abc").status_code, 422)
        self.assertEqual(self.stored(), before)

    def test_sec_reg_004_session_origin_and_host_boundaries(self):
        anonymous = self.client()
        self.assertEqual(anonymous.get("/api/requests").status_code, 401)
        response = self.alice.post("/api/requests", headers={"Origin": "https://attacker.invalid"}, json={"content": "injected"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.alice.get("/api/requests", headers={"Host": "attacker.invalid"}).status_code, 400)
        old_token = self.alice.cookies.get(COOKIE)
        result = self.alice.post("/api/demo/session", json={"userId": "bob"})
        self.assertIn("HttpOnly", result.headers["set-cookie"])
        self.assertIn("SameSite=strict", result.headers["set-cookie"])
        anonymous.cookies.set(COOKIE, old_token)
        self.assertEqual(anonymous.get("/api/requests").status_code, 401)
        self.assertEqual(self.stored(), ([], []))

    def test_sec_reg_004_stale_tab_identity_cannot_write_as_new_actor(self):
        self.alice.post("/api/demo/session", json={"userId": "carol"})
        response = self.alice.post("/api/requests", headers={"X-Demo-User": "alice"}, json={"content": "private draft"})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "IDENTITY_CHANGED")
        self.assertEqual(self.stored(), ([], []))

    def test_sec_reg_003_out_of_range_ids_return_structured_input_error(self):
        self.create()
        before = self.stored()
        for invalid in (0, -1, 9223372036854775808, -9223372036854775809):
            responses = [self.carol.get(f"/api/requests/{invalid}"),
                self.carol.post(f"/api/requests/{invalid}/decision", json={"decision": "approved", "version": 1}),
                self.alice.post(f"/api/requests/{invalid}/resubmit", json={"content": "updated", "version": 1})]
            for response in responses:
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["error"]["code"], "INVALID_INPUT")
        self.assertEqual(self.stored(), before)

    def test_reg_004_read_row_and_history_share_snapshot_during_commit(self):
        connect = sqlite3.connect
        with closing(connect(self.db_path)) as db:
            db.execute("PRAGMA journal_mode=WAL")
        for route in ("detail", "list"):
            row = self.create()
            injected = []
            db_path = self.db_path

            class ReadHook(sqlite3.Connection):
                def execute(self, sql, parameters=()):
                    if sql.startswith("SELECT * FROM decisions") and not injected:
                        injected.append(True)
                        # Commit between the real endpoint's row and history SELECTs.
                        with closing(connect(db_path)) as writer, writer:
                            writer.execute("INSERT INTO decisions VALUES(?,1,?,'rejected','reason','carol','2026-09-12T00:00:00Z')", (row["id"], row["content"]))
                            writer.execute("UPDATE requests SET status='rejected',reason='reason',version=2 WHERE id=?", (row["id"],))
                    return super().execute(sql, parameters)

            def hooked_connect(*args, **kwargs):
                return connect(*args, **kwargs, factory=ReadHook)

            with patch("app.sqlite3.connect", side_effect=hooked_connect):
                path = f"/api/requests/{row['id']}" if route == "detail" else "/api/requests"
                response = self.alice.get(path)
            self.assertEqual(response.status_code, 200)
            result = response.json() if route == "detail" else response.json()["requests"][0]
            self.assertEqual((result["status"], result["version"], result["history"]), ("submitted", 1, []))
            self.assertEqual(self.alice.get(f"/api/requests/{row['id']}").json()["status"], "rejected")

    def test_status_filter_all_statuses_access_order_and_read_only_restart(self):
        bob = self.client("bob")
        rows = []
        for owner in (self.alice, bob, self.carol):
            for status in ("submitted", "rejected", "approved"):
                row = self.create(f"{status} request", client=owner)
                if status != "submitted":
                    row = self.decide(row, client=self.client("dana"), decision=status)
                rows.append(row)
        before = self.stored()
        database_bytes = self.db_path.read_bytes()
        for app in (self.app, create_app(self.db_path, demo_enabled=True)):
            for name in ("alice", "bob", "carol", "dana"):
                client = self.client(name, app)
                authorized = [row for row in reversed(rows)
                              if name in ("carol", "dana") or row["owner"]["id"] == name]
                for status in (None, "submitted", "rejected", "approved"):
                    with self.subTest(restarted=app is not self.app, user=name, status=status):
                        response = client.get("/api/requests", params={} if status is None else {"status": status})
                        self.assertEqual(response.status_code, 200, response.text)
                        expected = [row for row in authorized if status is None or row["status"] == status]
                        self.assertEqual(response.json(), {"requests": expected})
            anonymous = self.client(app=app)
            for status in ("submitted", "rejected", "approved"):
                self.assertEqual(anonymous.get("/api/requests", params={"status": status}).status_code, 401)
            self.assertEqual(self.stored(), before)
            self.assertEqual(self.db_path.read_bytes(), database_bytes)

    def test_status_filter_invalid_input_is_read_only(self):
        self.decide(self.create())
        before = self.stored()
        for status in ("", "all", "pending", "Submitted", " approved", "approved' OR 1=1--"):
            with self.subTest(status=status):
                response = self.alice.get("/api/requests", params={"status": status})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["error"]["code"], "INVALID_INPUT")
        response = self.alice.get("/api/requests?status=rejected", headers={"X-Demo-User": "bob"})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "IDENTITY_CHANGED")
        self.assertEqual(self.stored(), before)

    def test_status_filter_resubmission_moves_buckets_preserving_history(self):
        rejected = self.decide(self.resubmit(self.decide(self.create())), "Second review")
        self.assertEqual(self.alice.get("/api/requests?status=rejected").json(), {"requests": [rejected]})
        updated = self.resubmit(rejected, "Final amendment")
        self.assertEqual(updated["history"], rejected["history"])
        before = self.stored()
        restarted = self.client("alice", create_app(self.db_path, demo_enabled=True))
        for client in (self.alice, restarted):
            self.assertEqual(client.get("/api/requests?status=rejected").json(), {"requests": []})
            self.assertEqual(client.get("/api/requests?status=approved").json(), {"requests": []})
            self.assertEqual(client.get("/api/requests?status=submitted").json(), {"requests": [updated]})
            self.assertEqual(client.get("/api/requests").json(), {"requests": [updated]})
        self.assertEqual(self.stored(), before)

    def test_demo_identity_switch_is_explicitly_opt_in(self):
        disabled = self.client(app=create_app(self.db_path))
        self.assertEqual(disabled.get("/api/demo/users").status_code, 404)
        self.assertEqual(disabled.post("/api/demo/session", json={"userId": "alice"}).status_code, 404)
        self.assertEqual(disabled.get("/api/requests").status_code, 401)


if __name__ == "__main__":
    unittest.main()
