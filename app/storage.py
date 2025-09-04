import os
import json
import time
import uuid
import hashlib

DATA_DIR = os.getenv("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _url_to_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]

def save_analysis(url: str, text: str, insights: dict, meta: dict) -> str:
    key = _url_to_key(url)
    session_id = str(uuid.uuid4())
    payload = {
        "session_id": session_id,
        "url": url,
        "text": text,
        "insights": insights,
        "meta": meta,
        "created_at": time.time(),
        "conversations": []
    }
    path = os.path.join(DATA_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return session_id

def get_by_url(url: str):
    key = _url_to_key(url)
    path = os.path.join(DATA_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_by_session(session_id: str):
    for fn in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, fn)
        with open(path, "r", encoding="utf-8") as f:
            j = json.load(f)
            if j.get("session_id") == session_id:
                return j
    return None

def append_conversation(session_id: str, role: str, text: str):
    obj = get_by_session(session_id)
    if not obj:
        return
    obj.setdefault("conversations", []).append({"role": role, "text": text, "ts": time.time()})
    key = hashlib.sha256(obj["url"].encode("utf-8")).hexdigest()[:24]
    path = os.path.join(DATA_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)