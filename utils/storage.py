import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
ASSETS_DIR = DATA_DIR / "assets"

DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

def read_json(name: str, default: Any):
    path = DATA_DIR / name
    if not path.exists():
        write_json(name, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        write_json(name, default)
        return default

def write_json(name: str, content: Any):
    path = DATA_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

def path_asset(filename: str):
    return ASSETS_DIR / filename
