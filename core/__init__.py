import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

with open(ROOT / "config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)
