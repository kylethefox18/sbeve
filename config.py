import json
from pathlib import Path

config_path = Path(__file__).resolve().parent / "config" / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)
