"""
process_reviews.py
───────────────────
WHERE TO RUN: locally on your laptop, OR automatically via GitHub Actions weekly.
WHAT IT DOES:
  1. Reads "raw_reviews" tab from your Google Sheet (public CSV, no auth)
  2. Scores each review using: Google ratings > context fields > NLP text
  3. Writes results to "processed" tab via Apps Script (no auth)

BEFORE RUNNING:
  Fill in SHEET_ID, RAW_GID, and APPS_SCRIPT_URL below.

HOW TO RUN:
  python src/process_reviews.py

DEPENDENCIES:
  pip install -r requirements.txt
"""

import os, re, json, time, requests
import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — fill these in once, then never touch again
# ─────────────────────────────────────────────────────────────────────────────

# From your Google Sheet URL:
# https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_ID/edit
SHEET_ID = '17ADm27u7yICbqD9etdiCNlZb-UlVzqPsbthozTiXgn0'

# GID of the "raw_reviews" tab — look at URL when you click that tab
# e.g. https://docs.google.com/spreadsheets/d/.../edit#gid=0
RAW_GID  = os.environ.get("RAW_GID", "0")

# Your Google Apps Script Web App URL
APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwM0bVHTMdPwvEOIsJrvn346KP3dvPA6Cpqck5Fq6FhDGQb7peX2biQU4RtCtYkKN0Q/exec'

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS FROM SAME FOLDER
# ─────────────────────────────────────────────────────────────────────────────
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from _column_aliases import normalise_row, normalise_columns
from context_handler import (
    score_all_context_fields,
    CONTEXT_TO_SCORE_COL,
    classify_context_value,
)
from aspect_groups_indian import ASPECT_GROUPS

# ─────────────────────────────────────────────────────────────────────────────
# LAZY-LOAD NLP — only imports heavy models when actually needed
# ─────────────────────────────────────────────────────────────────────────────
_sentiment_pipe  = None
_embed_model     = None
_aspect_embs     = None

def get_sentiment_pipe():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        from transformers import pipeline
        print("  Loading sentiment model (first time only)...")
        _sentiment_pipe = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            truncation=True, max_length=512,
        )
        print("  Sentiment model ready.")
    return _sentiment_pipe

def get_embed_model():
    global _embed_model, _aspect_embs
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        print("  Loading embedding model (first time only)...")
        _embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        _aspect_embs = {
            asp: _embed_model.encode(
                " ".join(data["en"][:10]), convert_to_tensor=True
            )
            for asp, data in ASPECT_GROUPS.items()
        }
        print("  Embedding model ready.")
    return _embed_model, _aspect_embs

# ─────────────────────────────────────────────────────────────────────────────
# READ — public CSV, zero auth required
# ─────────────────────────────────────────────────────────────────────────────

def read_raw_reviews() -> pd.DataFrame:
    if SHEET_ID == "YOUR_SHEET_ID_HERE":
        print("ERROR: Set SHEET_ID at the top of this file.")
        print("Find it in your Sheet URL:")
        print("https://docs.google.com/spreadsheets/d/SHEET_ID/edit")
        sys.exit(1)

    url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
           f"/export?format=csv&gid={RAW_GID}")
    print(f"Reading raw_reviews from Google Sheets...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        # Force UTF-8 so € and – are not mangled into â¬ / â
        resp.encoding = "utf-8"
        df = pd.read_csv(StringIO(resp.text), encoding="utf-8")
        df = normalise_columns(df)  # handles slash vs underscore column names
        # Fix any remaining encoding issues in string columns
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].apply(
                lambda x: x.encode("latin-1").decode("utf-8")
                if isinstance(x, str) and "â" in x else x
            )
        print(f"  Loaded {len(df)} reviews, {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"ERROR reading sheet: {e}")
        print("Make sure the sheet is set to 'Anyone with link can view'")
        sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# WRITE — via Apps Script, zero auth required
# ─────────────────────────────────────────────────────────────────────────────

def _fix_encoding(s: str) -> str:
    """Fix Latin-1 misread UTF-8 strings — e.g. â¬ → €, â → –"""
    if not isinstance(s, str) or "â" not in s:
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _clean_for_json(records: list) -> list:
    """
    - Replace float NaN/Infinity with None (JSON compliance)
    - Fix any UTF-8/Latin-1 encoding corruption in string values
    """
    import math
    cleaned = []
    for row in records:
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_row[k] = None
            elif isinstance(v, str):
                clean_row[k] = _fix_encoding(v)
            else:
                clean_row[k] = v
        cleaned.append(clean_row)
    return cleaned


def write_processed(df: pd.DataFrame):
    if APPS_SCRIPT_URL == "YOUR_APPS_SCRIPT_URL_HERE":
        print("ERROR: Set APPS_SCRIPT_URL at the top of this file.")
        sys.exit(1)

    # Step 1: replace pandas NaN with None
    records = df.where(pd.notnull(df), None).to_dict(orient="records")

    # Step 2: replace any remaining float NaN/Inf that slipped through
    records = _clean_for_json(records)

    total      = len(records)
    chunk_size = 400
    chunk_num  = 0

    print(f"Writing {total} rows to 'processed' tab via Apps Script...")
    print(f"  Sending in chunks of {chunk_size} rows...")

    written = 0
    for i in range(0, total, chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            payload_str = json.dumps(
                {
                    "action":      "write_results",
                    "results":     chunk,
                    "chunk_index": chunk_num,   # 0 = first chunk → clears sheet
                },
                allow_nan=False,
            )
            resp = requests.post(
                APPS_SCRIPT_URL,
                data=payload_str,
                headers={"Content-Type": "application/json"},
                timeout=90,
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("status") != "ok":
                print(f"  Warning from Apps Script: {result}")
            else:
                written += result.get("written", len(chunk))
                print(f"  {min(i + chunk_size, total)}/{total} rows written "
                      f"(chunk {chunk_num})")
            chunk_num += 1
        except Exception as e:
            print(f"  ERROR writing chunk {chunk_num} "
                  f"(rows {i}-{i+chunk_size}): {e}")
            chunk_num += 1
        time.sleep(2)   # slightly longer pause — Apps Script needs time between writes

    print(f"Done — {written}/{total} rows in 'processed' tab.")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _v(row, *keys):
    """First non-empty string value from row."""
    for k in keys:
        v = row.get(k, "")
        if v not in (None, "", "nan", float("nan")):
            return str(v).strip()
    return ""

def _f(row, *keys):
    """First valid float value from row."""
    for k in keys:
        try:
            v = float(row.get(k))
            if not np.isnan(v):
                return v
        except (TypeError, ValueError):
            pass
    return None

def _first(*args):
    """First non-None argument."""
    return next((a for a in args if a is not None), None)

def _avg(*args):
    vals = [a for a in args if a is not None]
    return round(sum(vals) / len(vals), 2) if vals else None

# ─────────────────────────────────────────────────────────────────────────────
# NLP ON TEXT — aspect-based sentence scoring
# ─────────────────────────────────────────────────────────────────────────────

def run_nlp(text: str, lang: str) -> dict:
    """
    Run aspect-based NLP on review text.
    Returns {aspect_name: avg_score}
    Only called when Google structured ratings are missing.
    """
    import nltk
    from sentence_transformers import util

    try:
        sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text)
                     if len(s.strip()) > 5]

    buckets  = {a: [] for a in ASPECT_GROUPS}
    kw_key   = "fi" if lang.startswith("fi") else "en"
    pipe     = get_sentiment_pipe()
    em, embs = get_embed_model()

    for sent in sentences:
        if len(sent.strip()) < 6:
            continue
        sl = sent.lower()
        matched = []

        # Step 1 — keyword match
        for asp, data in ASPECT_GROUPS.items():
            keys = set(data.get(kw_key, [])) | set(data.get("en", []))
            if any(re.search(rf'\b{re.escape(k)}\b', sl) for k in keys):
                matched.append(asp)

        # Step 2 — embedding fallback
        if not matched:
            emb = em.encode(sent, convert_to_tensor=True)
            for asp, a_emb in embs.items():
                if util.cos_sim(emb, a_emb).item() >= 0.38:
                    matched.append(asp)

        for a in matched:
            buckets[a].append(sent)

    result = {}
    for asp, sents in buckets.items():
        if not sents:
            continue
        scores = []
        for s in sents:
            try:
                label = pipe(s[:512])[0]["label"]
                scores.append({
                    "1 star":1,"2 stars":2,"3 stars":3,
                    "4 stars":4,"5 stars":5
                }.get(label, 3))
            except Exception:
                pass
        if scores:
            result[asp] = round(sum(scores) / len(scores), 2)
    return result

# ─────────────────────────────────────────────────────────────────────────────
# PROCESS ONE ROW
# ─────────────────────────────────────────────────────────────────────────────

def process_row(row: dict) -> dict:
    row = normalise_row(row)  # handles slash vs underscore column names
    out = {}

    # ── Restaurant / place metadata ───────────────────────────────────────────
    out["restaurant"]        = _v(row, "title", "name")
    out["address"]           = _v(row, "address")
    out["city"]              = _v(row, "city")
    out["neighborhood"]      = _v(row, "neighborhood")
    out["category"]          = _v(row, "categoryName")
    out["price_range"]       = _v(row, "price")
    out["place_url"]         = _v(row, "url")
    out["lat"]               = _f(row, "location/lat")
    out["lng"]               = _f(row, "location/lng")
    out["place_total_score"] = _f(row, "totalScore")
    out["place_reviews_count"] = _f(row, "reviewsCount")

    # ── Review metadata ───────────────────────────────────────────────────────
    out["review_id"]         = _v(row, "reviewId")
    out["review_stars"]      = _f(row, "stars", "rating")
    out["review_date"]       = _v(row, "publishedAtDate", "publishAt")
    out["visited_in"]        = _v(row, "visitedIn")
    out["language"]          = _v(row, "language", "originalLanguage")
    out["original_language"] = _v(row, "originalLanguage")
    out["likes_count"]       = _f(row, "likesCount")
    out["is_local_guide"]    = str(row.get("isLocalGuide","")).lower() == "true"
    out["reviewer_review_count"] = _f(row, "reviewerNumberOfReviews")
    out["owner_responded"]   = bool(_v(row, "responseFromOwnerText"))

    # ── Review text ───────────────────────────────────────────────────────────
    out["text_original"]   = _v(row, "text")
    out["text_translated"] = _v(row, "textTranslated")

    # Use translation for NLP if original was non-English
    orig_lang = out["original_language"].lower()
    out["text_for_nlp"] = (
        out["text_translated"]
        if out["text_translated"] and orig_lang not in ("en", "english")
        else out["text_original"] or out["text_translated"]
    )

    # ── Process ALL context fields smartly ───────────────────────────────────
    # context_handler figures out: categorical vs sentence vs short sentiment
    # and uses the sentiment model on free-text sentences automatically
    pipe = get_sentiment_pipe() if out["text_for_nlp"] else None
    ctx_result = score_all_context_fields(row, sentiment_pipe=pipe)

    ctx_scores     = ctx_result["scores"]       # {field: float}
    ctx_categories = ctx_result["categories"]   # {field: str}

    # Save all categorical context values as columns for dashboard filters
    out["ctx_meal_type"]        = ctx_categories.get("reviewContext/Meal type", "")
    out["ctx_order_type"]       = ctx_categories.get("reviewContext/Order type", "")
    out["ctx_group_size"]       = ctx_categories.get("reviewContext/Group size", "")
    out["ctx_seating_type"]     = ctx_categories.get("reviewContext/Seating type", "")
    out["ctx_dietary"]          = ctx_categories.get("reviewContext/Dietary restrictions", "")
    out["ctx_price_per_person"] = ctx_categories.get("reviewContext/Price per person", "")
    out["ctx_recommended"]      = ctx_categories.get("reviewContext/Recommended dishes", "")
    out["ctx_special_events"]   = ctx_categories.get("reviewContext/Special events", "")
    out["ctx_reservation"]      = ctx_categories.get("reviewContext/Reservation", "")
    out["ctx_noise_raw"]        = ctx_categories.get("reviewContext/Noise level", "")
    out["ctx_wait_raw"]         = ctx_categories.get("reviewContext/Wait time", "")
    out["ctx_kid_raw"]          = ctx_categories.get("reviewContext/Kid-friendliness", "")
    out["ctx_parking_raw"]      = ctx_categories.get("reviewContext/Parking", "")
    out["ctx_wheelchair_raw"]   = ctx_categories.get("reviewContext/Wheelchair accessibility", "")
    out["ctx_vegetarian_raw"]   = ctx_categories.get("reviewContext/Vegetarian options", "")

    # Map context scores to our aspect score columns
    def ctx_score(field):
        return ctx_scores.get(field)

    # ── Google's own structured ratings ───────────────────────────────────────
    g_food       = _f(row, "reviewDetailedRating/Food")
    g_service    = _f(row, "reviewDetailedRating/Service")
    g_atmosphere = _f(row, "reviewDetailedRating/Atmosphere")

    # ── Decide if NLP is needed ────────────────────────────────────────────────
    # Only run heavy NLP if Google ratings are missing AND text is long enough
    has_all_google = all(v is not None for v in [g_food, g_service, g_atmosphere])
    text_ok        = len(out["text_for_nlp"]) > 30

    nlp = {}
    if not has_all_google and text_ok:
        lang = out["language"][:2] if out["language"] else "en"
        print(f"    → Running NLP on text ({len(out['text_for_nlp'])} chars, {lang})")
        nlp = run_nlp(out["text_for_nlp"], lang)

    # ── Merge: Google > context-derived > NLP ─────────────────────────────────
    out["score_food"]        = _first(g_food,
                                      nlp.get("Food Quality"),
                                      nlp.get("Curry & Sauce"))
    out["score_service"]     = _first(g_service,
                                      _avg(ctx_score("reviewContext/Wait time"),
                                           nlp.get("Service & Staff")))
    out["score_ambience"]    = _first(g_atmosphere,
                                      _avg(ctx_score("reviewContext/Noise level"),
                                           nlp.get("Ambience & Atmosphere")))
    out["score_noise"]       = _first(ctx_score("reviewContext/Noise level"),
                                      nlp.get("Ambience & Atmosphere"))
    out["score_wait_time"]   = _first(ctx_score("reviewContext/Wait time"),
                                      nlp.get("Service & Staff"))
    out["score_parking"]     = _first(
                                      ctx_score("reviewContext/Parking"),
                                      ctx_score("reviewContext/Parking options"),
                                      ctx_score("reviewContext/Parking space"),
                                      nlp.get("Location & Accessibility"))
    out["score_wheelchair"]  = _first(ctx_score("reviewContext/Wheelchair accessibility"),
                                      nlp.get("Location & Accessibility"))
    out["score_vegetarian"]  = _first(ctx_score("reviewContext/Vegetarian options"),
                                      nlp.get("Vegetarian & Vegan Options"))
    out["score_kid_friendly"]= _first(ctx_score("reviewContext/Kid-friendliness"))
    out["score_price"]       = nlp.get("Price & Value")
    out["score_authenticity"]= nlp.get("Authenticity")
    out["score_spice"]       = nlp.get("Spice Level")
    out["score_cleanliness"] = nlp.get("Cleanliness & Hygiene")
    out["score_chicken"]     = nlp.get("Chicken Dishes")
    out["score_lamb"]        = nlp.get("Lamb & Mutton Dishes")
    out["score_vegan_dishes"]= nlp.get("Vegetarian & Vegan Options")
    out["score_bread_rice"]  = nlp.get("Bread & Rice")
    out["score_starters"]    = nlp.get("Starters & Street Food")
    out["score_overall_nlp"] = nlp.get("Overall Experience")

    # ── Reviewer credibility weight ───────────────────────────────────────────
    n = out["reviewer_review_count"] or 1
    out["credibility_weight"] = round(min(1.0, 0.3 + (n / 100) * 0.7), 3)

    # ── Data source tag ───────────────────────────────────────────────────────
    out["data_source"] = (
        "google_ratings" if has_all_google else
        "context_scored" if ctx_scores     else
        "nlp_text"       if nlp            else
        "no_data"
    )
    out["processed_at"] = datetime.now().isoformat()
    return out

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import nltk
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

    print("=" * 60)
    print("PROCESS REVIEWS — Oulu Restaurant Sentiment")
    print("=" * 60)

    raw_df = read_raw_reviews()
    if raw_df.empty:
        print("No reviews found. Run your Make.com scenario first.")
        sys.exit(0)

    results      = []
    source_tally = {}

    for i, row in raw_df.iterrows():
        name = str(row.get("title", row.get("name", "Unknown")))[:40]
        print(f"[{i+1}/{len(raw_df)}] {name}")
        processed = process_row(row.to_dict())
        results.append(processed)
        src = processed["data_source"]
        source_tally[src] = source_tally.get(src, 0) + 1

    out_df = pd.DataFrame(results)

    print(f"\nData source breakdown:")
    for src, count in sorted(source_tally.items(),
                              key=lambda x: -x[1]):
        pct = round(100 * count / len(results))
        bar = "█" * (pct // 5)
        print(f"  {src:<20} {bar:<20} {count:>4} ({pct}%)")

    print()
    write_processed(out_df)
    print("\nAll done! Dashboard will show updated data.")
    print(f"Processed tab has {len(out_df.columns)} columns.")
