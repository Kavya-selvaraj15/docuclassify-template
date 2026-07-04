"""
Tier 3: Claude API fallback classification.
"""
import json
from django.conf import settings

try:
    import anthropic
except ImportError:
    anthropic = None

CATEGORIES = ["invoice", "contract", "policy", "other"]


def classify_by_llm(text: str):
    if not settings.ANTHROPIC_API_KEY or anthropic is None:
        return "other", 0.0

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = f"""Classify this document into exactly one category: {", ".join(CATEGORIES)}.

Document text:
{text[:2000]}

Respond ONLY with valid JSON: {{"category": "...", "reasoning": "..."}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        parsed = json.loads(raw)
        category = parsed.get("category", "other")
        if category not in CATEGORIES:
            category = "other"
        return category, 0.85
    except Exception:
        return "other", 0.0