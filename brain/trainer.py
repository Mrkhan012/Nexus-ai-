"""
brain/trainer.py — Train & save the Nexus intent classifier.

Run this script once (and again whenever you add new training data):
    python brain/trainer.py

Output: model/nexus_model.pkl
"""

import os
import sys
import joblib
import random
import nltk

from sklearn.pipeline           import Pipeline
from sklearn.linear_model       import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection    import train_test_split
from sklearn.metrics            import classification_report

# Ensure imports work from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from brain.intent_data import TRAINING_DATA
from config            import MODEL_PATH

# ─── Download NLTK data (only needed once) ────────────────────────────────────
def _download_nltk():
    for resource in ["punkt", "stopwords", "wordnet", "omw-1.4"]:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)

_download_nltk()

from nltk.corpus        import stopwords
from nltk.stem          import WordNetLemmatizer
from nltk.tokenize      import word_tokenize

_stop_words  = set(stopwords.words("english"))
_lemmatizer  = WordNetLemmatizer()

# Keep these filler words as they can appear in commands
_keep_words  = {"open", "close", "find", "save", "create", "run", "make",
                "launch", "start", "stop", "search", "show", "go"}

def clean_text(text: str) -> str:
    """Lowercase, tokenize, remove stopwords (except command words), lemmatize."""
    tokens   = word_tokenize(text.lower())
    filtered = [
        _lemmatizer.lemmatize(t)
        for t in tokens
        if t.isalpha() and (t not in _stop_words or t in _keep_words)
    ]
    return " ".join(filtered)


def train():
    # Shuffle for reproducibility
    data = list(TRAINING_DATA)
    random.seed(42)
    random.shuffle(data)

    texts  = [clean_text(phrase) for phrase, _ in data]
    labels = [intent              for _, intent in data]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=1,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=5.0,
            solver="lbfgs",
        )),
    ])

    print("🧠  Training Nexus ML model...")
    pipeline.fit(X_train, y_train)

    y_pred   = pipeline.predict(X_test)
    accuracy = (y_pred == y_test.copy().__class__(y_test)).mean() if False else \
               sum(p == t for p, t in zip(y_pred, y_test)) / len(y_test)

    print(f"\n✅  Training complete. Holdout accuracy: {accuracy * 100:.1f}%\n")
    print(classification_report(y_test, y_pred))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"💾  Model saved → {MODEL_PATH}")


if __name__ == "__main__":
    train()
