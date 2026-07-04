"""
Tier 2: TF-IDF + Logistic Regression classification.

Statistical fallback for documents that don't match any regex rule.
No external API cost. Train once on labeled examples, then load the
saved model at runtime.

Train with:
    python manage.py shell -c "from apps.classifier.ml_classifier import train_and_save; train_and_save()"
"""
import joblib
from pathlib import Path
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_PATH = Path(settings.CLASSIFIER_ML_MODEL_DIR) / "tfidf_logreg.pkl"

# Replace with your real labeled training data (aim for 50-100+ examples
# per category minimum — this stub is just enough to prove the pipeline works).
SAMPLE_TRAINING_DATA = [
    ("employee handbook outlining company code of conduct", "policy"),
    ("purchase order for office supplies dated march", "invoice"),
    ("non disclosure agreement between two parties", "contract"),
    ("annual leave policy and remote work guidelines", "policy"),
    ("payment receipt for consulting services rendered", "invoice"),
    ("service level agreement outlining uptime commitments", "contract"),
]


def train_and_save():
    texts, labels = zip(*SAMPLE_TRAINING_DATA)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipeline.fit(texts, labels)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def load_model():
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            # Confirm it's actually fitted before trusting it
            model.predict_proba(["sanity check text"])
            return model
        except Exception:
            # Corrupted or incomplete file — retrain from scratch
            pass
    return train_and_save()


def classify_by_ml(text: str):
    """
    Returns (category, confidence). Confidence is the model's max
    predicted probability across classes.
    """
    model = load_model()
    proba = model.predict_proba([text])[0]
    classes = model.classes_
    best_idx = proba.argmax()
    return classes[best_idx], float(proba[best_idx])
