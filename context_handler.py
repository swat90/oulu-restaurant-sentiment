"""
context_handler.py
───────────────────
Smart handler for reviewContext/* fields from Apify/Google Maps.

Problem: these fields contain unpredictable free text, not fixed labels.
Examples seen in real data:
  - "Asiakaspalvelu lapsiperheille kohda..." (Finnish sentence)
  - "Child friendly customer service, it w..."
  - "Desserts for kids and they were nic..."
  - "It is a family oriented place"
  - "Very kid friendly."
  - "Suitable for all group sizes"   ← categorical, not sentiment
  - "3-4 people"                     ← categorical
  - "Free street parking"            ← semi-categorical
  - "Lunch"                          ← pure category
  - "Dine in"                        ← pure category
  - "Amazing"                        ← short sentiment word

Solution:
  1. Detect if value is a SHORT CATEGORICAL LABEL or a SENTIMENT TEXT
  2. For categorical → keep raw, use for charts
  3. For short sentiment words (amazing, good, terrible) → fast lookup
  4. For actual sentences → run through sentiment model
  5. For truly ambiguous/neutral categories → return None (skip scoring)
"""

import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# KNOWN CATEGORICAL VALUES — these are labels, not sentiment
# If a value matches one of these patterns, it's a category — don't score it
# ─────────────────────────────────────────────────────────────────────────────

# Regex patterns for values that are pure categories
CATEGORICAL_PATTERNS = [
    # Meal types
    r"^(lunch|dinner|breakfast|brunch|other|snack|supper)$",
    # Order types
    r"^(dine.?in|takeaway|take.?out|delivery|curbside|drive.?through)$",
    # Group sizes — numbers + people
    r"^\d+.?\d*\s*(people|person|guests?|henkilöä|henkilö)$",
    r"^(solo|alone|couple|pairs?|family|group|large group)$",
    r"^suitable for all group sizes$",
    r"^(1|2|3.4|5.10|10\+)\s*(people|person)?$",
    # Seating types
    r"^(indoor|outdoor|bar seating|booth|patio|terrace|window|street)$",
    # Time periods
    r"^(morning|afternoon|evening|night|weekend|weekday)$",
    # Pure location labels
    r"^(free street parking|paid parking|no parking|free parking lot)$",
    r"^(wheelchair accessible|not wheelchair accessible)$",
    r"^(offers vegetarian options|doesn't offer vegetarian options)$",
    r"^(reservations? (recommended|required|not (needed|required)))$",
    r"^(no wait|up to \d+ min|\d+.?\d+ min|\d+\+ min)$",
    r"^(quiet|quiet.{0,20}talk|average|very noisy|loud)$",
]

# Short single-word or 2-word sentiment mappings (for values too short for model)
SHORT_SENTIMENT = {
    # Positive
    "amazing": 5.0, "excellent": 5.0, "perfect": 5.0, "outstanding": 5.0,
    "great": 4.5, "good": 4.0, "nice": 4.0, "wonderful": 5.0,
    "fantastic": 5.0, "superb": 5.0, "brilliant": 5.0, "lovely": 4.5,
    "very good": 4.5, "very kid friendly": 5.0, "kid friendly": 4.5,
    "family friendly": 4.5, "highly recommended": 5.0,
    "yes": 4.0, "absolutely": 5.0, "definitely": 4.5,
    # Negative
    "terrible": 1.0, "awful": 1.0, "horrible": 1.0, "bad": 1.5,
    "poor": 2.0, "disappointing": 2.0, "disappointing.": 2.0,
    "not good": 2.0, "no": 2.0, "never": 1.5,
    # Finnish single words
    "erinomainen": 5.0, "loistava": 5.0, "hyvä": 4.0, "mainio": 4.5,
    "huono": 2.0, "kauhea": 1.0, "täydellinen": 5.0,
}

# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def classify_context_value(value: str) -> str:
    """
    Returns one of:
      'empty'       — null/empty/nan
      'categorical' — a label/category, not sentiment (keep for charts)
      'short_sentiment' — short word/phrase with known sentiment
      'sentence'    — full sentence that needs model scoring
    """
    if not value or str(value).strip() in ("", "nan", "None", "none"):
        return "empty"

    v = str(value).strip()
    v_lower = v.lower()

    # Check categorical patterns
    for pattern in CATEGORICAL_PATTERNS:
        if re.match(pattern, v_lower):
            return "categorical"

    # Very short values (1-3 words) — check short sentiment dict
    word_count = len(v_lower.split())
    if word_count <= 4:
        if v_lower.rstrip(".!?,") in SHORT_SENTIMENT:
            return "short_sentiment"
        # Short but unknown — treat as categorical to avoid garbage scores
        if word_count <= 2:
            return "categorical"

    # Anything longer is a sentence — run through model
    return "sentence"


def is_negative_sentence(text: str) -> bool:
    """Quick check for negation — helps model accuracy."""
    negations = [
        "not ", "no ", "never ", "don't ", "doesn't ", "didn't ",
        "wasn't ", "weren't ", "isn't ", "aren't ", "without ",
        "ei ", "ei ole", "ei ollut", "en ", "emme ", "eivät ",
    ]
    t = text.lower()
    return any(t.startswith(neg) or f" {neg}" in t for neg in negations)


# ─────────────────────────────────────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────────────────────────────────────

def score_context_value(
    value: str,
    sentiment_pipe=None,
) -> Optional[float]:
    """
    Score a context field value.
    Returns float 1.0-5.0 or None if not scoreable.

    Args:
        value:          raw string from the context column
        sentiment_pipe: loaded nlptown pipeline (pass None to lazy-load)
    """
    kind = classify_context_value(value)

    if kind == "empty":
        return None

    if kind == "categorical":
        return None  # keep for charts, not for scoring

    v = str(value).strip()
    v_lower = v.lower().rstrip(".!?,")

    if kind == "short_sentiment":
        return SHORT_SENTIMENT.get(v_lower)

    # kind == "sentence" — run through model
    if sentiment_pipe is None:
        # lazy load
        from transformers import pipeline as hf_pipeline
        sentiment_pipe = hf_pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            truncation=True, max_length=512,
        )

    try:
        result = sentiment_pipe(v[:512])[0]
        label  = result["label"]
        score  = {"1 star":1,"2 stars":2,"3 stars":3,
                  "4 stars":4,"5 stars":5}.get(label, 3)

        # Small adjustment for explicit negation that model might miss
        if is_negative_sentence(v) and score >= 4:
            score = max(2, score - 1)

        return float(score)
    except Exception:
        return None


def score_all_context_fields(
    row: dict,
    sentiment_pipe=None,
) -> dict:
    """
    Process ALL reviewContext/* fields in one row.

    Returns dict with two sub-dicts:
      'scores':     {field_name: float_score}   — for aspect rating columns
      'categories': {field_name: str_value}     — for chart filter columns
    """
    scores     = {}
    categories = {}

    # Normalise column names (handles underscore vs slash from Make.com)
    try:
        from _column_aliases import normalise_row
        row = normalise_row(row)
    except ImportError:
        pass
    context_fields = {k: v for k, v in row.items()
                      if k.startswith("reviewContext/")}

    for field, raw_value in context_fields.items():
        val  = str(raw_value).strip() if raw_value else ""
        kind = classify_context_value(val)

        if kind == "empty":
            continue
        elif kind == "categorical":
            categories[field] = val
        elif kind in ("short_sentiment", "sentence"):
            score = score_context_value(val, sentiment_pipe)
            if score is not None:
                scores[field]     = score
                # Also keep raw text as category for charts
                categories[field] = val
            else:
                categories[field] = val

    return {"scores": scores, "categories": categories}


# ─────────────────────────────────────────────────────────────────────────────
# FIELD → ASPECT MAPPING
# Maps context field name → our aspect score column name
# ─────────────────────────────────────────────────────────────────────────────

CONTEXT_TO_SCORE_COL = {
    "reviewContext/Noise level":              "score_noise",
    "reviewContext/Wait time":                "score_wait_time",
    "reviewContext/Kid-friendliness":         "score_kid_friendly",
    "reviewContext/Wheelchair accessibility": "score_wheelchair",
    "reviewContext/Parking":                  "score_parking",
    "reviewContext/Parking options":          "score_parking",   # same col
    "reviewContext/Parking space":            "score_parking",
    "reviewContext/Vegetarian options":       "score_vegetarian",
    "reviewContext/Reservation":              None,  # categorical only
    "reviewContext/Dietary restrictions":     None,  # categorical only
    "reviewContext/Meal type":                None,  # categorical only
    "reviewContext/Order type":               None,  # categorical only
    "reviewContext/Group size":               None,  # categorical only
    "reviewContext/Seating type":             None,  # categorical only
    "reviewContext/Price per person":         None,  # categorical only
    "reviewContext/Recommended dishes":       None,  # categorical only
    "reviewContext/Special events":           None,  # categorical only
    "reviewContext/Special offers":           None,  # categorical only
}

# ─────────────────────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_values = [
        # From your screenshot
        ("reviewContext/Kid-friendliness", "Asiakaspalvelu lapsiperheille kohda"),
        ("reviewContext/Kid-friendliness", "Child friendly customer service, it was great"),
        ("reviewContext/Kid-friendliness", "Desserts for kids and they were nice"),
        ("reviewContext/Kid-friendliness", "It is a family oriented place"),
        ("reviewContext/Kid-friendliness", "They have chair for babies"),
        ("reviewContext/Kid-friendliness", "Very kid friendly."),
        ("reviewContext/Kid-friendliness", "Vessassa oli potta. En huomannut"),
        # Other fields
        ("reviewContext/Group size",       "Suitable for all group sizes"),
        ("reviewContext/Group size",       "3-4 people"),
        ("reviewContext/Meal type",        "Lunch"),
        ("reviewContext/Noise level",      "Quiet, easy to talk"),
        ("reviewContext/Noise level",      "It was surprisingly loud for a lunch spot"),
        ("reviewContext/Wait time",        "No wait"),
        ("reviewContext/Wait time",        "We waited almost 40 minutes for our food"),
        ("reviewContext/Parking",          "Free street parking"),
        ("reviewContext/Parking",          "Parking was a nightmare, had to walk far"),
        ("reviewContext/Vegetarian options","Offers vegetarian options"),
        ("reviewContext/Vegetarian options","The veg menu was limited but tasty"),
    ]

    print("Context field classification + scoring test")
    print("(Note: sentence scoring requires model — showing classification only)\n")
    print(f"{'Field':<40} {'Value':<45} {'Kind'}")
    print("─"*110)
    for field, val in test_values:
        kind = classify_context_value(val)
        short_val = val[:43] + "..." if len(val) > 45 else val
        print(f"{field[-30:]:<40} {short_val:<45} {kind}")
