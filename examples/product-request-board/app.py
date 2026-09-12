"""Loopback demonstration of a request workflow, not production authentication."""

import argparse
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import logging
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Path as PathParam, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware


ROOT = Path(__file__).resolve().parent
LOG = logging.getLogger("request_board")
USERS = {
    "alice": {"id": "alice", "name": "민수", "role": "requester"},
    "bob": {"id": "bob", "name": "지수", "role": "requester"},
    "carol": {"id": "carol", "name": "영희", "role": "reviewer"},
    "dana": {"id": "dana", "name": "준호", "role": "reviewer"},
}
COOKIE = "request_board_demo"
RequestId = Annotated[int, PathParam(gt=0, le=9223372036854775807)]
SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY,
    owner TEXT NOT NULL,
    content TEXT NOT NULL CHECK(length(trim(content)) BETWEEN 1 AND 4000),
    status TEXT NOT NULL CHECK(status IN ('submitted','rejected','approved')),
    reason TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0)
);
CREATE TABLE IF NOT EXISTS decisions (
    request_id INTEGER NOT NULL REFERENCES requests(id),
    round INTEGER NOT NULL,
    content TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('rejected','approved')),
    reason TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    PRIMARY KEY(request_id, round)
);
"""


class APIError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Content(Input):
    content: str = Field(min_length=1, max_length=4000, strict=True)

    @field_validator("content")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("content cannot be blank")
        return value


class Resubmission(Content):
    version: StrictInt = Field(gt=0)


class Decision(Input):
    decision: Literal["approved", "rejected"]
    reason: str = Field(default="", max_length=4000, strict=True)
    version: StrictInt = Field(gt=0)


class Identity(Input):
    userId: Literal["alice", "bob", "carol", "dana"]


def create_app(db_path, *, demo_enabled=False):
    db_path = Path(db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as db:
        db.executescript(SCHEMA)
    app = FastAPI(docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    sessions = {}

    @contextmanager
    def connection(write=False):
        with closing(sqlite3.connect(db_path, timeout=5)) as db:
            with db:
                db.row_factory = sqlite3.Row
                db.execute("PRAGMA foreign_keys = ON")
                # Writers serialize state changes; readers see one row/history snapshot.
                db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
                yield db

    @app.exception_handler(APIError)
    async def api_error(_request, error):
        return JSONResponse({"error": {"code": error.code, "message": error.message}}, status_code=error.status)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(_request, _error):
        return JSONResponse({"error": {"code": "INVALID_INPUT", "message": "입력값을 확인하세요."}}, status_code=422)

    @app.exception_handler(sqlite3.Error)
    async def storage_error(_request, _error):
        LOG.error("request storage operation failed")
        return JSONResponse({"error": {"code": "STORAGE_ERROR", "message": "저장소 작업에 실패했습니다."}}, status_code=500)

    @app.middleware("http")
    async def origin_guard(request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            expected = str(request.base_url).rstrip("/")
            if request.headers.get("origin") != expected:
                return JSONResponse({"error": {"code": "ORIGIN_DENIED", "message": "허용되지 않은 요청 출처입니다."}}, status_code=403)
            if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
                return JSONResponse({"error": {"code": "JSON_REQUIRED", "message": "JSON 요청이 필요합니다."}}, status_code=415)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'"
        return response

    def current_user(request: Request):
        if not demo_enabled:
            return None
        session = sessions.get(request.cookies.get(COOKIE))
        if session and session[1] > time.monotonic():
            return USERS[session[0]]
        return None

    def actor(request: Request, user=Depends(current_user)):
        if user is None:
            raise APIError(401, "IDENTITY_REQUIRED", "테스트 계정을 선택하세요.")
        expected = request.headers.get("x-demo-user")
        if expected is not None and expected != user["id"]:
            raise APIError(409, "IDENTITY_CHANGED", "다른 탭에서 계정이 변경되었습니다.")
        return user

    def row_for(db, request_id, user):
        row = db.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
        if row is None or (row["owner"] != user["id"] and user["role"] != "reviewer"):
            raise APIError(404, "NOT_FOUND", "요청을 찾을 수 없습니다.")
        return row

    def view(db, row):
        history = db.execute("SELECT * FROM decisions WHERE request_id=? ORDER BY round", (row["id"],)).fetchall()
        return {**dict(row), "owner": USERS[row["owner"]], "history": [
            {"round": h["round"], "content": h["content"], "decision": h["decision"],
             "reason": h["reason"], "reviewer": USERS[h["reviewer"]], "decidedAt": h["decided_at"]}
            for h in history]}

    def version_and_state(row, expected, status):
        if row["version"] != expected:
            raise APIError(409, "STALE_VERSION", "다른 변경이 있습니다. 새로 확인하세요.")
        if row["status"] != status:
            raise APIError(409, "INVALID_STATE", "현재 상태에서는 처리할 수 없습니다.")

    @app.get("/api/demo/users")
    def demo_users():
        if not demo_enabled:
            raise APIError(404, "DEMO_DISABLED", "테스트 계정 전환이 비활성화되어 있습니다.")
        return {"users": list(USERS.values())}

    @app.post("/api/demo/session")
    def switch_identity(body: Identity, request: Request):
        if not demo_enabled:
            raise APIError(404, "DEMO_DISABLED", "테스트 계정 전환이 비활성화되어 있습니다.")
        sessions.pop(request.cookies.get(COOKIE), None)
        if len(sessions) >= 512:
            sessions.pop(next(iter(sessions)))
        token = secrets.token_urlsafe(32)
        sessions[token] = (body.userId, time.monotonic() + 8 * 3600)
        response = JSONResponse({"user": USERS[body.userId]})
        response.set_cookie(COOKIE, token, httponly=True, samesite="strict", max_age=8 * 3600)
        return response

    @app.get("/api/me")
    def me(user=Depends(current_user)):
        return {"user": user}

    @app.get("/api/requests")
    def list_requests(user=Depends(actor)):
        with connection() as db:
            rows = db.execute("SELECT * FROM requests WHERE owner=? OR ?='reviewer' ORDER BY id DESC",
                              (user["id"], user["role"])).fetchall()
            return {"requests": [view(db, row) for row in rows]}

    @app.post("/api/requests", status_code=201)
    def create(body: Content, user=Depends(actor)):
        with connection(True) as db:
            cursor = db.execute("INSERT INTO requests(owner,content,status) VALUES(?,?,'submitted')", (user["id"], body.content))
            result = view(db, row_for(db, cursor.lastrowid, user))
        return result

    @app.get("/api/requests/{request_id}")
    def get_request(request_id: RequestId, user=Depends(actor)):
        with connection() as db:
            return view(db, row_for(db, request_id, user))

    @app.post("/api/requests/{request_id}/decision")
    def decide(request_id: RequestId, body: Decision, user=Depends(actor)):
        with connection(True) as db:
            row = row_for(db, request_id, user)
            if user["role"] != "reviewer" or row["owner"] == user["id"]:
                raise APIError(403, "REVIEW_FORBIDDEN", "본인 요청은 검토할 수 없습니다.")
            version_and_state(row, body.version, "submitted")
            if body.decision == "rejected" and not body.reason.strip():
                raise APIError(422, "REASON_REQUIRED", "반려 사유를 입력하세요.")
            round_number = db.execute("SELECT count(*)+1 FROM decisions WHERE request_id=?", (request_id,)).fetchone()[0]
            db.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?,?)",
                       (request_id, round_number, row["content"], body.decision, body.reason,
                        user["id"], datetime.now(timezone.utc).isoformat()))
            db.execute("UPDATE requests SET status=?,reason=?,version=version+1 WHERE id=?",
                       (body.decision, body.reason, request_id))
            result = view(db, row_for(db, request_id, user))
        LOG.info("request decision committed: id=%s version=%s", request_id, result["version"])
        return result

    @app.post("/api/requests/{request_id}/resubmit")
    def resubmit(request_id: RequestId, body: Resubmission, user=Depends(actor)):
        with connection(True) as db:
            row = row_for(db, request_id, user)
            if row["owner"] != user["id"]:
                raise APIError(403, "RESUBMIT_FORBIDDEN", "작성자만 재제출할 수 있습니다.")
            version_and_state(row, body.version, "rejected")
            db.execute("UPDATE requests SET content=?,status='submitted',reason=NULL,version=version+1 WHERE id=?",
                       (body.content, request_id))
            result = view(db, row_for(db, request_id, user))
        LOG.info("request resubmitted: id=%s version=%s", request_id, result["version"])
        return result

    @app.get("/")
    def index():
        return FileResponse(ROOT / "static/index.html")

    @app.get("/icons.js")
    def icons():
        file = ROOT / "node_modules/lucide/dist/umd/lucide.min.js"
        if not file.is_file():
            raise APIError(503, "ICONS_UNAVAILABLE", "npm ci로 로컬 자산을 준비하세요.")
        return FileResponse(file, media_type="text/javascript")

    if (ROOT / "static").exists():
        app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
    return app


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Enable local test identity switching")
    parser.add_argument("--db", type=Path, default=ROOT / ".local/requests.sqlite3")
    parser.add_argument("--port", type=int, default=8157)
    args = parser.parse_args()
    if not args.demo:
        parser.error("Use --demo only for a local, non-production test")
    uvicorn.run(create_app(args.db, demo_enabled=True), host="127.0.0.1", port=args.port)
