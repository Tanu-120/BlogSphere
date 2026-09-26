"""
Safety check for new posts and comments.

When an API key is set, an LLM returns allow/block. Otherwise a local linear
model scores the text: each phrase has a weight, the weights are summed, and
a score past the threshold is blocked. Normal writing stays under that line.
"""
import json
import re

import httpx
from fastapi import HTTPException, status

from app.config import get_settings

settings = get_settings()

# Fixed weights for the local linear model. Higher means more likely to block.
_WEIGHTS = {
    "kill yourself": 2.4,
    "kys": 2.2,
    "i will kill you": 2.4,
    "rape": 2.0,
    "child porn": 3.0,
    "nigger": 2.6,
    "faggot": 2.2,
}
_THRESHOLD = 1.5
_PROMPT = (
    "You moderate a public blog. Block threats, slurs, sexual content involving minors, "
    "and requests for violent crime. Allow ordinary writing, criticism, and technical discussion. "
    'Reply with JSON only: {"allow": true, "reason": "short"}.'
)


def _local_score(text: str) -> float:
    folded = re.sub(r"\s+", " ", (text or "").lower())
    score = 0.0
    for phrase, weight in _WEIGHTS.items():
        if phrase in folded:
            score += weight
    return score


def _ask_model(text: str) -> dict | None:
    snippet = text[:4000]
    try:
        if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            with httpx.Client(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": settings.AI_MODEL,
                        "max_tokens": 120,
                        "system": _PROMPT,
                        "messages": [{"role": "user", "content": snippet}],
                    },
                )
                response.raise_for_status()
                body = response.json()
                raw = "".join(block.get("text", "") for block in body.get("content", []) if block.get("type") == "text")
                return json.loads(raw)
        if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            with httpx.Client(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
                response = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "content-type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": _PROMPT},
                            {"role": "user", "content": snippet},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
                raw = response.json()["choices"][0]["message"]["content"]
                return json.loads(raw)
    except Exception:
        return None
    return None


def screen_text(text: str) -> None:
    """Raise 422 when the text should not be stored."""
    verdict = _ask_model(text)
    if verdict is not None and "allow" in verdict:
        if not verdict.get("allow"):
            reason = verdict.get("reason") or "It was blocked by the safety check."
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(reason))
        return

    if _local_score(text) >= _THRESHOLD:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This text was blocked by the safety check.",
        )
