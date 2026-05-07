# Board With Login Sample App

This sample verifies that Vulcan-Anvil Ex documents can drive a small implementation.

Trace scope:

- `REQ-001` signup
- `REQ-002` login
- `REQ-003` post list
- `REQ-004` post detail
- `REQ-005` post creation
- `REQ-006` post update/delete
- `SEC-001` password storage
- `SEC-002` authenticated post creation
- `SEC-003` author-only update/delete
- `SEC-004` server-side input validation

## Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- pytest

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```powershell
pytest
```

## Message Rule

User-facing messages are loaded from `app/resources/messages.ko.yml`.
Implementation code should raise or return message codes such as `ERR-001` and `MSG-001`.
