import json
import os


def read_text_file(path: str):
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def write_text_file(path: str, content: str) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def delete_file(path: str) -> bool:
    if not os.path.exists(path):
        return True

    try:
        os.remove(path)
        return True
    except Exception:
        return False


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


def save_json_file(path: str, payload: dict) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def save_session(config_path: str, state: dict, queue: list):
    """
    Save session state and queue to disk.
    """
    payload = dict(state)
    payload["queue"] = queue

    save_json_file(config_path, payload)
