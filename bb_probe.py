import os, json, requests

API = "https://api.browserbase.com/v1/sessions"
KEY = os.environ.get("BROWSERBASE_API_KEY", "")
PROJ = os.environ.get("BROWSERBASE_PROJECT_ID", "")

def show(name, val):
    # Don't print your whole key; just lengths and edge characters.
    masked = f"{val[:6]}...{val[-4:]}" if val else ""
    print(f"{name}: len={len(val)} {masked}")

print("== ENV ==")
show("BROWSERBASE_API_KEY", KEY)
show("BROWSERBASE_PROJECT_ID", PROJ)
print("\n== REQUEST ==")
print("POST", API)
print("Header x-bb-api-key present?", bool(KEY))
print("Body:", {"projectId": PROJ})

r = requests.post(API,
    headers={"x-bb-api-key": KEY, "Content-Type":"application/json"},
    json={"projectId": PROJ},
    timeout=30,
)
print("\n== RESPONSE ==")
print("Status:", r.status_code)
print("Body:", r.text)

if r.ok:
    data = r.json()
    print("connectUrl:", data.get("connectUrl"))
