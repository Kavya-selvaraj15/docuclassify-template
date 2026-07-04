"""
The cascading classification pipeline: regex -> TF-IDF/LogReg -> Claude API.

This is the core pattern of the whole template. Each tier only runs if
the previous tier didn't produce a confident answer, which keeps average
cost and latency low while still handling edge cases correctly.
"""
from django.conf import settings
from .rules import classify_by_rules
from .ml_classifier import classify_by_ml
from .llm_classifier import classify_by_llm


def classify_document(text: str) -> dict:
    """
    Returns a dict: {"category": str, "confidence": float, "tier": str}
    tier is one of "rules", "ml", "llm" — useful for logging/analytics
    on how much of your volume each tier is actually handling.
    """
    category, confidence = classify_by_rules(text)
    if category:
        return {"category": category, "confidence": confidence, "tier": "rules"}

    category, confidence = classify_by_ml(text)
    if confidence >= settings.CLASSIFIER_TFIDF_CONFIDENCE_THRESHOLD:
        return {"category": category, "confidence": confidence, "tier": "ml"}

    category, confidence = classify_by_llm(text)
    return {"category": category, "confidence": confidence, "tier": "llm"}
