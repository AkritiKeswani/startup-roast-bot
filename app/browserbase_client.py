import os, requests

BASE = "https://api.browserbase.com/v1"
BB_KEY = os.environ.get("BROWSERBASE_API_KEY","")
BB_PID = os.environ.get("BROWSERBASE_PROJECT_ID","")

def _hdr(): return {"x-bb-api-key": BB_KEY, "Content-Type":"application/json"}

def create_session(extra: dict = None):
    if not BB_KEY or not BB_PID:
        raise RuntimeError("Browserbase env missing (BROWSERBASE_API_KEY / BROWSERBASE_PROJECT_ID)")
    body = {"projectId": BB_PID}
    if extra: body.update(extra)
    r = requests.post(f"{BASE}/sessions", headers=_hdr(), json=body, timeout=30)
    if r.status_code == 401:
        raise RuntimeError("Browserbase 401 Unauthorized. Verify API key & projectId (same project), no whitespace.")
    r.raise_for_status()
    return r.json()

def connect_url(sess:dict) -> str:
    url = sess.get("connectUrl")
    if not url:
        sid = sess.get("id")
        if not sid: raise RuntimeError("Session missing id/connectUrl")
        r = requests.get(f"{BASE}/sessions/{sid}", headers=_hdr(), timeout=20)
        r.raise_for_status()
        url = r.json().get("connectUrl")
    if not url: raise RuntimeError("connectUrl not present on session")
    return url