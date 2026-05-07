from functools import lru_cache
from pathlib import Path

MESSAGE_PATH = Path(__file__).resolve().parents[1] / "resources" / "messages.ko.yml"


@lru_cache(maxsize=1)
def load_messages() -> dict[str, str]:
    messages: dict[str, str] = {}
    for raw_line in MESSAGE_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        messages[key.strip()] = value.strip().strip('"')
    return messages


def get_message(code: str) -> str:
    return load_messages().get(code, load_messages()["ERR-007"])
