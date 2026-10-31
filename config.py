import tomllib
from pathlib import Path

config_path = Path(__file__).resolve().parent / "config" / "config.toml"
with open(config_path, "rb") as f:
    config = tomllib.load(f)
