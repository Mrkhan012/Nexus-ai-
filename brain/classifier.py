"""
brain/classifier.py — Load the trained model and classify user text into intents.
Also extracts named entities (file names, folder names, command strings).
"""

import re
import os
import sys
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import MODEL_PATH, CONFIDENCE_THRESHOLD

# ─── Load model lazily ────────────────────────────────────────────────────────
_model_data = None


def _load_model():
    global _model_data
    if _model_data is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}.\n"
                "Please run:  python brain/trainer.py"
            )
        _model_data = joblib.load(MODEL_PATH)
    return _model_data


# ─── Text Cleaning (reuse trainer's logic without importing trainer) ──────────
def _clean(text: str) -> str:
    """Basic clean for inference (mirrors trainer's clean_text)."""
    import nltk
    try:
        from nltk.tokenize  import word_tokenize
        from nltk.corpus    import stopwords
        from nltk.stem      import WordNetLemmatizer
    except LookupError:
        for r in ["punkt", "stopwords", "wordnet"]:
            nltk.download(r, quiet=True)
        from nltk.tokenize  import word_tokenize
        from nltk.corpus    import stopwords
        from nltk.stem      import WordNetLemmatizer

    _stop   = set(stopwords.words("english"))
    _keep   = {"open", "close", "find", "save", "create", "run", "make",
               "launch", "start", "stop", "search", "show", "go"}
    _lem    = WordNetLemmatizer()

    tokens  = word_tokenize(text.lower())
    return " ".join(
        _lem.lemmatize(t)
        for t in tokens
        if t.isalpha() and (t not in _stop or t in _keep)
    )


# ─── Entity Extraction ────────────────────────────────────────────────────────
# Patterns for extracting "payload" values from spoken text.
_ENTITY_PATTERNS = [
    # "save this to <name>"  /  "folder called <name>"  /  "named <name>"
    r"called\s+([a-zA-Z0-9_\-\s]+)",
    r"named\s+([a-zA-Z0-9_\-\s]+)",
    r"save this to\s+([a-zA-Z0-9_\-\s]+)",
    r"save this as\s+([a-zA-Z0-9_\-\s]+)",
    r"find\s+(?:my\s+)?([a-zA-Z0-9_\-\s]+)",
    r"search for\s+([a-zA-Z0-9_\-\s]+)",
    r"where (?:is|did I put)\s+(?:my\s+)?([a-zA-Z0-9_\-\s]+)",
    r"run\s+([a-zA-Z0-9_\-\s\.]+)",
    r"execute\s+([a-zA-Z0-9_\-\s\.]+)",
    r"open\s+(?:my\s+)?([a-zA-Z0-9_\-\s]+)\s+folder",
    r"go to\s+(?:my\s+)?([a-zA-Z0-9_\-\s]+)",
    # Search patterns
    r"search\s+(?:for\s+)?(?:on\s+youtube\s+for\s+)?([a-zA-Z0-9_\-\s]+)",
    r"google\s+(?:for\s+)?(?:search\s+)?([a-zA-Z0-9_\-\s]+)",
    r"look up\s+([a-zA-Z0-9_\-\s]+)",
    r"how (?:do|to)\s+([a-zA-Z0-9_\-\s]+)",
    r"what is\s+([a-zA-Z0-9_\-\s]+)",
    r"play\s+([a-zA-Z0-9_\-\s]+)\s+(?:on\s+youtube|music|video)",
    r"watch\s+([a-zA-Z0-9_\-\s]+)\s+(?:on\s+youtube|video)",
]

def extract_entity(text: str) -> str | None:
    """Try to extract a name/target entity from the user's text."""
    for pattern in _ENTITY_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
    return None


# ─── Main Classify Function ───────────────────────────────────────────────────
def classify(text: str) -> tuple[str, float, str | None]:
    """
    Classify the given text into an intent.

    Args:
        text: Raw user speech text.

    Returns:
        (intent, confidence, entity)
        - intent     : e.g. "OPEN_BROWSER"
        - confidence : float 0–1
        - entity     : extracted name/target, or None
    """
    pipeline   = _load_model()

    cleaned     = _clean(text)
    proba       = pipeline.predict_proba([cleaned])[0]
    confidence  = float(proba.max())
    intent      = pipeline.classes_[proba.argmax()]
    entity      = extract_entity(text)

    if confidence < CONFIDENCE_THRESHOLD:
        return "UNKNOWN", confidence, entity

    return intent, confidence, entity


if __name__ == "__main__":
    tests = [
        "open chrome",
        "I need to crunch some numbers",
        "save this to my ideas",
        "where did I put my presentation",
        "create a folder called Vacation",
        "open my downloads folder",
        "run my python script",
        "bye nexus",
        "blah blah blah nonsense",
    ]
    # Train first if model missing
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Training now...")
        from brain.trainer import train
        train()

    print("\n── Nexus Classifier Test ──")
    for phrase in tests:
        intent, conf, entity = classify(phrase)
        print(f"  [{conf:.2f}] \"{phrase}\" → {intent}  (entity: {entity})")
