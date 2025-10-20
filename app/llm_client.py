import os, requests, json

GROK_API_KEY = os.environ.get("GROK_API_KEY","")
GROK_MODEL = os.environ.get("GROK_MODEL","grok-2")
GROK_BASE = os.environ.get("GROK_BASE_URL","https://api.x.ai/v1")

SYSTEM = """You are "LandingPageRoaster"—a witty but constructive copy editor.
One short sentence roasting a startup's LANDING PAGE ONLY.
- Focus: hero clarity, value prop, CTA, legibility, nav clutter, jargon.
- No personal attacks, no accusations, no profanity.
- ≤ 180 chars. Exactly one sentence. One emoji max if helpful. Return only the sentence.
"""

USER_TPL = """Tone: {style}
Summary JSON:
{summary}
"""

def generate_roast(summary: dict, style: str = "spicy") -> str:
    if not GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY is required. Please set it in your environment variables.")
    
    payload = {
        "model": GROK_MODEL,
        "temperature": 0.9 if style=="spicy" else 0.6 if style=="kind" else 0.7,
        "max_tokens": 80,
        "messages": [
            {"role":"system","content":SYSTEM},
            {"role":"user","content":USER_TPL.format(style=style, summary=json.dumps(summary, ensure_ascii=False))}
        ]
    }
    r = requests.post(f"{GROK_BASE}/chat/completions",
                      headers={"Authorization": f"Bearer {GROK_API_KEY}"},
                      json=payload, timeout=60)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    one = " ".join(text.splitlines())
    return one[:180] if len(one)>180 else one