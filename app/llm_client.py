"""
Grok LLM client for roast generation.
"""

import os
import json
import requests
from typing import Dict
from logutil import setup_logger

logger = setup_logger(__name__)

GROK_API_KEY = os.environ["GROK_API_KEY"]
GROK_MODEL = os.environ.get("GROK_MODEL", "grok-3")
GROK_BASE = os.environ.get("GROK_BASE_URL", "https://api.x.ai/v1")

SYSTEM_PROMPT = """You are "LandingPageRoaster"—a witty but constructive copy editor.
Your job: write ONE short sentence that roasts a startup's LANDING PAGE ONLY.

Rules:
- Focus purely on the page UX/copy: hero clarity, value prop, visual hierarchy, CTA, contrast/legibility, nav clutter, jargon.
- No attacks on people, founders, or sensitive attributes.
- No company-level accusations (e.g., "scam", "fraud", "stealing data").
- No profanity or slurs. Be playful, not mean.
- Don't invent facts beyond the provided summary.
- Output MUST be ≤ 180 characters and exactly one sentence (no lists, no line breaks).
- Add ONE tasteful emoji max if it strengthens the punch; otherwise none.

Tone presets:
- spicy: playful jab with edge; still professional.
- kind: gentle nudge, encouraging.
- deadpan: dry, minimal, slightly ironic.

Return ONLY the sentence—no preamble, no quotes.
"""

USER_TEMPLATE = """Write a one-sentence roast of this startup's LANDING PAGE using the tone: {style}.
Base it ONLY on this extracted summary (title/hero/cta may be empty strings):

Summary JSON:
{summary_json}

Remember: ≤ 180 chars; exactly one sentence; landing page only.
"""


def generate_roast(summary: Dict[str, str], style: str = "spicy") -> str:
    """Generate a roast using Grok LLM."""
    try:
        payload = {
            "model": GROK_MODEL,
            "temperature": 0.9 if style == "spicy" else 0.6 if style == "kind" else 0.7,
            "max_tokens": 80,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE.format(
                    style=style, summary_json=json.dumps(summary, ensure_ascii=False)
                )},
            ],
        }
        
        logger.info("Generating roast with Grok", style=style, summary_keys=list(summary.keys()))
        
        response = requests.post(
            f"{GROK_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json=payload, 
            timeout=60
        )
        response.raise_for_status()
        
        text = response.json()["choices"][0]["message"]["content"].strip()
        
        # Guardrails: 1 sentence, <= 180 chars
        text = " ".join(text.splitlines()).strip()
        if len(text) > 180:
            text = text[:177].rstrip() + "…"
        
        # Remove trailing punctuation spam
        while text.endswith(("..", "!!", "??")):
            text = text[:-1]
        
        logger.info("Generated roast", length=len(text), style=style)
        return text
        
    except Exception as e:
        logger.error("Failed to generate roast", extra={'error': str(e), 'style': style})
        # Fallback roast
        return f"Your landing page needs work, but at least it loads!"
