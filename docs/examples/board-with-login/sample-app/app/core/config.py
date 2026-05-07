from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'board_sample.db'}"
TOKEN_SECRET = "board-with-login-sample-secret"
TOKEN_EXPIRE_SECONDS = 60 * 60
