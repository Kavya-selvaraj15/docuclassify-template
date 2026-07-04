"""
Tier 1: Regex-based classification.

Fast, free, zero false-positive-prone patterns first. Anything that
matches here never touches the ML model or the API — keeps cost and
latency down for the "obvious" cases (which in most document sets is
60-80% of volume).
"""
import re

# Map: category -> list of compiled patterns.
# Extend this dict with your own document categories.
RULES = {
    "invoice": [
        re.compile(r"\binvoice\s*(no|number|#)\b", re.I),
        re.compile(r"\bbill\s*to\b", re.I),
        re.compile(r"\btotal\s*due\b", re.I),
    ],
    "contract": [
        re.compile(r"\bthis\s+agreement\b", re.I),
        re.compile(r"\bparties\s+hereto\b", re.I),
        re.compile(r"\btermination\s+clause\b", re.I),
    ],
    "policy": [
        re.compile(r"\bpolicy\s+number\b", re.I),
        re.compile(r"\bcoverage\s+(period|amount)\b", re.I),
    ],
}


def classify_by_rules(text: str):
    """
    Returns (category, confidence) if a rule matches, else (None, 0.0).
    Confidence is fixed at 0.99 for rule matches since regex hits are
    treated as near-certain for this tier.
    """
    for category, patterns in RULES.items():
        for pattern in patterns:
            if pattern.search(text):
                return category, 0.99
    return None, 0.0
