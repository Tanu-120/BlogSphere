"""
Ask Anthropic or OpenAI for a short summary and a few tags.

If the key is missing, the call times out, or the body is unusable, fall
back to a local extract so the request still completes.
"""
import json
import re

import httpx

from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = (
    "You write a 2-sentence, non-clickbait summary of a blog post and suggest "
    "up to 5 short lowercase topic tags. Respond ONLY with compact JSON: "
    '{"summary": "...", "tags": ["tag1", "tag2"]}. No markdown, no preamble.'
)


def _fallback_summary(title: str, content: str) -> tuple[str, str]:
    """Extractive fallback used when no AI provider is configured/reachable."""
    plain = re.sub(r"\s+", " ", content).strip()
    summary = plain[:220] + ("…" if len(plain) > 220 else "")
    words = re.findall(r"[a-zA-Z]{5,}", plain.lower())
    common = [w for w, _ in sorted({w: words.count(w) for w in set(words)}.items(), key=lambda x: -x[1])][:5]
    return summary, ", ".join(common)


async def _call_anthropic(title: str, content: str) -> dict | None:
    if not settings.ANTHROPIC_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "max_tokens": 300,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": f"Title: {title}\n\nContent:\n{content[:4000]}"}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
            return json.loads(text)
    except Exception:
        return None


async def _call_openai(title: str, content: str) -> dict | None:
    if not settings.OPENAI_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "content-type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Title: {title}\n\nContent:\n{content[:4000]}"},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return json.loads(text)
    except Exception:
        return None


def expand_search_terms(query: str) -> tuple[str, str | None]:
    """Ask Claude or GPT for a few related words. ("", None) if no model is configured."""
    prompt = (
        "Give up to 4 related search words for a blog query. "
        'Reply with JSON only: {"terms": ["word"]}.'
    )
    try:
        if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            with httpx.Client(timeout=8) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": settings.AI_MODEL,
                        "max_tokens": 80,
                        "system": prompt,
                        "messages": [{"role": "user", "content": query[:200]}],
                    },
                )
                response.raise_for_status()
                body = response.json()
                raw = "".join(block.get("text", "") for block in body.get("content", []) if block.get("type") == "text")
                terms = json.loads(raw).get("terms", [])
                return (" ".join(terms) if isinstance(terms, list) else ""), "Claude"
        if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            with httpx.Client(timeout=8) as client:
                response = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "content-type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": query[:200]},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
                terms = json.loads(response.json()["choices"][0]["message"]["content"]).get("terms", [])
                return (" ".join(terms) if isinstance(terms, list) else ""), "GPT"
    except Exception:
        return "", None
    return "", None


async def generate_summary_and_tags(title: str, content: str) -> tuple[str, str, str]:
    """Returns (summary, comma_separated_tags, source)."""
    result = None
    source = "fallback"

    if settings.AI_PROVIDER == "anthropic":
        result = await _call_anthropic(title, content)
        source = "anthropic" if result else "fallback"
    elif settings.AI_PROVIDER == "openai":
        result = await _call_openai(title, content)
        source = "openai" if result else "fallback"

    if result and "summary" in result:
        tags = result.get("tags", [])
        return result["summary"], ", ".join(tags) if isinstance(tags, list) else str(tags), source

    summary, tags = _fallback_summary(title, content)
    return summary, tags, "fallback"
