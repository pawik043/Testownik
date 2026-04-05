import json
import os


def load_session(config_path: str):
    """
    Load session JSON from disk.

    Returns:
        dict | None
    """
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_session(config_path: str, state: dict, queue: list):
    """
    Save session state and queue to disk.
    """
    payload = dict(state)
    payload["queue"] = queue

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)