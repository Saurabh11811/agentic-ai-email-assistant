import json
from pathlib import Path

# Set base path relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TIMESTAMP_DIR = SCRIPT_DIR.parent  # Adjust if timestamps live elsewhere

def get_last_timestamp(file_path: str):
    path = Path(file_path)
    if not path.is_absolute():
        path = DEFAULT_TIMESTAMP_DIR / file_path
    if path.exists():
        return path.read_text().strip()
    return None

def update_timestamp(file_path: str, timestamp: str):
    path = Path(file_path)
    if not path.is_absolute():
        path = DEFAULT_TIMESTAMP_DIR / file_path
    path.write_text(timestamp)  # ✅ NOT json.dump or anything else

