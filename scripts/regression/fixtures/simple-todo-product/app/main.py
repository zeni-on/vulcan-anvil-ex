from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


APP_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = APP_ROOT / "static"
DEFAULT_DB_PATH = APP_ROOT / "data" / "todos.db"


def get_db_path() -> Path:
    return Path(os.environ.get("TODO_DB_PATH", DEFAULT_DB_PATH))


def connect() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL CHECK(length(trim(text)) > 0),
                completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def row_to_todo(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "text": row["text"],
        "completed": bool(row["completed"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


class TodoCreate(BaseModel):
    text: str = Field(min_length=1, max_length=140)


class TodoUpdate(BaseModel):
    completed: bool


app = FastAPI(title="Product TODO v0.4.8 Replay")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/todos")
def list_todos() -> dict[str, list[dict[str, Any]]]:
    """SCN-001~003/API-001: return all Todo rows in stable newest-last order."""
    init_db()
    with connect() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id ASC").fetchall()
    return {"data": [row_to_todo(row) for row in rows]}


@app.post("/api/todos", status_code=201)
def create_todo(payload: TodoCreate) -> dict[str, dict[str, Any]]:
    """SCN-001/API-002/DATA-001: create one non-empty Todo item."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail={"code": "TODO_TEXT_INVALID", "message": "할 일을 입력하세요."})
    init_db()
    with connect() as conn:
        cursor = conn.execute("INSERT INTO todos (text) VALUES (?)", (text,))
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {"data": row_to_todo(row)}


@app.patch("/api/todos/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate) -> dict[str, dict[str, Any]]:
    """SCN-002/API-003/DATA-001: update completed state for an existing Todo."""
    init_db()
    with connect() as conn:
        conn.execute(
            "UPDATE todos SET completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (1 if payload.completed else 0, todo_id),
        )
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "TODO_NOT_FOUND", "message": "할 일을 찾을 수 없습니다."})
    return {"data": row_to_todo(row)}


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int) -> dict[str, dict[str, bool]]:
    """SCN-003/API-004/DATA-001: delete an existing Todo item."""
    init_db()
    with connect() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail={"code": "TODO_NOT_FOUND", "message": "할 일을 찾을 수 없습니다."})
    return {"data": {"deleted": True}}
