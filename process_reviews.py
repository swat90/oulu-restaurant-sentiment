"""
process_reviews.py
───────────────────
Reads from Google Sheets (public CSV - no credentials needed to read),
processes each review using structured context fields first, NLP second,
writes results back via Google Apps Script (no credentials needed to write).

HOW DATA FLOWS:
  Make.com (Apify → Apps Script) → Google Sheets "raw_reviews" tab
      ↓  [this script reads it — no auth needed if sheet is public]
  process_reviews.py
      ↓  [writes via Apps Script webhook — no auth needed]
  Google Sheets "processed" tab
      ↓
  Streamlit dashboard reads via public CSV URL

NO API KEYS NEEDED in this script at all.
Set your sheet to "Anyone with link can view" and paste the IDs below.
"""

import re
import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — fill these in, no credentials needed
# ─────────────────────────────────────────────────────────────────────────────

# Your Google Sheet ID — from the URL:
# https://docs.google.com/spreadsheets/d/THIS_PART_HERE/edit
SHEET_ID = "YOUR_SHEET_ID_HERE"

# GID of each tab — find it in the URL when you click the tab
# e.g. https://docs.google.com/spreadsheets/d/.../edit#gid=0
RAW_REVIEWS_GID  = "0"       # usually 0 for first tab
PROCESSED_GID    = ""        # leave empty — script creates it via Apps Script

# Your Google Apps Script Web App URL (from Part 2 of deployment guide)
APPS_SCRIPT_URL = "YOUR_APPS_SCRIPT_URL_HERE"

# ─────────────────────────────────────────────────────────────────────────────
# READ FROM SHEETS — public CSV, zero auth
# ─────────────────────────────────────────────────────────────────────────────

def read_sheet_public(sheet_id: str, gid: str) -> pd.DataFrame:
    """
    Read any publicly shared Google Sheet tab as CSV.
    Sheet must be set to 'Anyone with link can view'.
    No API key, no credentials, no OAuth.
    """
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/export?format=csv&gid={gid}"
    )
    print(f"Reading sheet: {url[:60]}...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    from io import StringIO
    df = pd.read_csv(StringIO(resp.text))
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    return df

# ─────────────────────────────────────────────────────────────────────────────
# WRITE BACK — via Apps Script webhook, zero auth
# ─────────────────────────────────────────────────────────────────────────────

def write_processed(df: pd.DataFrame, apps_script_url: str):
    """
    Send processed results to Apps Script which writes to Sheets.
    Sends in chunks of 500 rows to stay within HTTP payload limits.
    """
    # Convert NaN → None so JSON serialises cleanly
    records = df.where(pd.notnull(df), None).to_dict(orient="records")

    chunk_size = 500
    total_written = 0

    for i in range(0, len(records), chunk_size):
        chunk = records[i:i+chunk_size]
        payload = {
            "action":  "write_results",
            "results": chunk,
        }
        resp = requests.post(
            apps_script_url,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("status") != "ok":
            print(f"  Warning: Apps Script returned: {result}")
        else:
            total_written += result.get("written", len(chunk))
            print(f"  Written {min(i+chunk_size, len(records))}/{len(records)} rows")
        time.sleep(1)

    return total_written

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT FIELD HANDLING
# These fields contain TEXT labels, not numbers.
# Strategy:
#   - Fields with clear positive/negative meaning → convert to 1-5 score
#   - Fields that are just categories → keep as-is for charts
# ─────────────────────────────────────────────────────────────────────────────

# Each entry: list of (pattern, score) — checked in order, first match wins
# Score of None means "keep as category, don't score"
CONTEXT_SCORE_RULES = {

    "reviewContext/Noise level": [
        ("quiet, easy to talk",     5),
        ("quiet",                   5),
        ("average",                 3),
        ("can get pretty noisy",    2),
        ("very noisy",              1),
        ("loud",                    1),
    ],

    "reviewContext/Wait time": [
        ("no wait",         5),
        ("up to 10 min",    5),
        ("10-20 min",       4),
        ("20-30 min",       3),
        ("30-45 min",       2),
        ("45+ min",         1),
        ("long",            2),
        ("short",           5),
    ],

    "reviewContext/Kid-friendliness": [
        ("amazing",                     5),
        ("good for kids",               5),
        ("suitable for children",       5),
        ("not suitable for children",   2),
        ("not good for kids",           2),
    ],

    "reviewContext/Wheelchair accessibility": [
        ("wheelchair accessible",           5),
        ("fully accessible",                5),
        ("accessible",                      4),
        ("not wheelchair accessible",       1),
        ("not accessible",                  1),
        ("limited accessibility",           2),
    ],

    "reviewContext/Parking": [
        ("free parking lot",        5),
        ("free street parking",     4),
        ("paid parking lot",        3),
        ("paid street parking",     3),
        ("parking available",       3),
        ("no parking available",    1),
        ("no parking",              1),
        ("difficult parking",       2),
    ],

    "reviewContext/Parking options": [
        ("free",    4),
        ("paid",    3),
        ("none",    1),
    ],

    "reviewContext/Vegetarian options": [
        ("offers vegetarian options",           4),
        ("vegetarian options available",        4),
        ("great vegetarian options",            5),
        ("limited vegetarian",                  2),
        ("doesn't offer vegetarian options",    1),
        ("no vegetarian",                       1),
    ],

    "reviewContext/Reservation": [
        ("reservations recommended",    4),
        ("required",                    4),
        ("not needed",                  5),   # easy walk-in = positive
        ("not required",                5),
    ],
}

# These context fields stay as raw text — used for categorical charts only
CATEGORICAL_FIELDS = {
    "reviewContext/Meal type":         "ctx_meal_type",
    "reviewContext/Order type":        "ctx_order_type",
    "reviewContext/Group size":        "ctx_group_size",
    "reviewContext/Seating type":      "ctx_seating_type",
    "reviewContext/Dietary restrictions": "ctx_dietary",
    "reviewContext/Price per person":  "ctx_price_per_person",
    "reviewContext/Recommended dishes":"ctx_recommended_dishes",
    "reviewContext/Special events":    "ctx_special_events",
    "reviewContext/Special offers":    "ctx_special_offers",
}

def score_context_field(value: str, rules: list) -> float | None:
    """
    Given a text value and ordered rules list,
    return matching score or None if no match.
    """
    if not value or str(value).strip() in ("", "nan", "None"):
        return None
    v = str(value).strip().lower()
    for pattern, score in rules:
        if pattern.lower() in v:
            return float(score)
    return None

# ─────────────────────────────────────────────────────────────────────────────
# LAZY-LOAD NLP MODELS — only when structured data is insufficient
# ─────────────────────────────────────────────────────────────────────────────
_nlp_loaded = False
_sentiment_pipe = None
_embed_model = None
_aspect_embeddings = None

def load_nlp_models():
    global _nlp_loaded, _sentiment_pipe, _embed_model, _aspect_embeddings
    if _nlp_loaded:
        return
    print("Loading NLP models (first run only)...")
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    from aspect_groups_indian import ASPECT_GROUPS

    _sentiment_pipe = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        truncation=True, max_length=512,
    )
    _embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    _aspect_embeddings = {
        aspect: _embed_model.encode(
            " ".join(data["en"][:10]),
            convert_to_tensor=True
        )
        for aspect, data in ASPECT_GROUPS.items()
    }
    _nlp_loaded = True
    print("Models loaded.")

def run_nlp_on_text(text: str, lang: str) -> dict:
    """
    Run aspect-based sentiment NLP.
    Returns {aspect_name: score_float}
    Only called when Google structured ratings are missing.
    """
    load_nlp_models()

    from aspect_groups_indian import ASPECT_GROUPS
    from sentence_transformers import util
    import nltk

    try:
        sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text)
                     if len(s.strip()) > 5]

    buckets = {a: [] for a in ASPECT_GROUPS}
    kw_key  = "fi" if lang.startswith("fi") else "en"

    for sent in sentences:
        sl = sent.lower()
        if len(sl) < 5:
            continue

        matched = []
        # Step 1: keyword match
        for aspect, data in ASPECT_GROUPS.items():
            keys = set(data.get(kw_key, [])) | set(data.get("en", []))
            if any(re.search(rf'\b{re.escape(k)}\b', sl) for k in keys):
                matched.append(aspect)

        # Step 2: embedding fallback if nothing matched
        if not matched:
            emb = _embed_model.encode(sent, convert_to_tensor=True)
            for aspect, a_emb in _aspect_embeddings.items():
                if util.cos_sim(emb, a_emb).item() >= 0.38:
                    matched.append(aspect)

        for a in matched:
            buckets[a].append(sent)

    result = {}
    for aspect, sents in buckets.items():
        if not sents:
            continue
        scores = []
        for s in sents:
            try:
                label = _sentiment_pipe(s[:512])[0]["label"]
                scores.append({
                    "1 star":1,"2 stars":2,"3 stars":3,
                    "4 stars":4,"5 stars":5
                }.get(label, 3))
            except Exception:
                pass
        if scores:
            result[aspect] = round(sum(scores) / len(scores), 2)

    return result

# ─────────────────────────────────────────────────────────────────────────────
# ROW PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────

def _v(row, *keys):
    """Get first non-empty value from row using multiple key names."""
    for k in keys:
        val = row.get(k, "")
        if val not in (None, "", "nan", float("nan")):
            return str(val).strip()
    return ""

def _f(row, *keys):
    """Get float value."""
    for k in keys:
        val = row.get(k)
        try:
            f = float(val)
            if not np.isnan(f):
                return f
        except (TypeError, ValueError):
            pass
    return None

def _first(*args):
    """Return first non-None argument."""
    return next((a for a in args if a is not None), None)

def process_row(row: dict) -> dict:
    out = {}

    # ── Restaurant / place info ───────────────────────────────────────────────
    out["restaurant"]           = _v(row, "title", "name")
    out["address"]              = _v(row, "address")
    out["city"]                 = _v(row, "city")
    out["neighborhood"]         = _v(row, "neighborhood")
    out["category"]             = _v(row, "categoryName")
    out["price_range"]          = _v(row, "price")
    out["place_url"]            = _v(row, "url")
    out["lat"]                  = _f(row, "location/lat")
    out["lng"]                  = _f(row, "location/lng")
    out["place_total_score"]    = _f(row, "totalScore")
    out["place_reviews_count"]  = _f(row, "reviewsCount")
    out["place_permanently_closed"] = _v(row, "permanentlyClosed")

    # ── Review metadata ───────────────────────────────────────────────────────
    out["review_id"]            = _v(row, "reviewId")
    out["review_stars"]         = _f(row, "stars", "rating")
    out["review_date"]          = _v(row, "publishedAtDate", "publishAt")
    out["visited_in"]           = _v(row, "visitedIn")
    out["language"]             = _v(row, "language", "originalLanguage")
    out["original_language"]    = _v(row, "originalLanguage")
    out["review_origin"]        = _v(row, "reviewOrigin")
    out["likes_count"]          = _f(row, "likesCount")
    out["is_local_guide"]       = str(row.get("isLocalGuide","")).lower() == "true"
    out["reviewer_review_count"]= _f(row, "reviewerNumberOfReviews")
    out["owner_responded"]      = bool(_v(row, "responseFromOwnerText"))

    # ── Review text ───────────────────────────────────────────────────────────
    out["text_original"]        = _v(row, "text")
    out["text_translated"]      = _v(row, "textTranslated")

    # Best text for NLP: prefer translation when original was not English
    orig_lang = out["original_language"].lower()
    out["text_for_nlp"] = (
        out["text_translated"]
        if out["text_translated"] and orig_lang not in ("en", "english")
        else out["text_original"] or out["text_translated"]
    )

    # ── Categorical context fields (keep raw for charts) ─────────────────────
    for src_col, dest_col in CATEGORICAL_FIELDS.items():
        out[dest_col] = _v(row, src_col)

    # ── Score context fields (convert text labels → 1-5) ─────────────────────
    context_scores = {}
    for field, rules in CONTEXT_SCORE_RULES.items():
        val   = _v(row, field)
        score = score_context_field(val, rules)
        if score is not None:
            context_scores[field] = score

    # ── Google detailed ratings (most reliable — use directly) ────────────────
    g_food       = _f(row, "reviewDetailedRating/Food")
    g_service    = _f(row, "reviewDetailedRating/Service")
    g_atmosphere = _f(row, "reviewDetailedRating/Atmosphere")

    # ── Decide whether to run NLP ─────────────────────────────────────────────
    # Only run NLP if Google ratings are missing AND text is long enough
    has_google_all = all(v is not None for v in [g_food, g_service, g_atmosphere])
    text_long_enough = len(out["text_for_nlp"]) > 30

    nlp_scores = {}
    if not has_google_all and text_long_enough:
        lang = out["language"][:2] if out["language"] else "en"
        nlp_scores = run_nlp_on_text(out["text_for_nlp"], lang)

    # ── Final aspect scores: Google > context-derived > NLP ──────────────────
    noise_score      = context_scores.get("reviewContext/Noise level")
    wait_score       = context_scores.get("reviewContext/Wait time")
    parking_score    = context_scores.get("reviewContext/Parking")
    parking_opt_score= context_scores.get("reviewContext/Parking options")
    wheelchair_score = context_scores.get("reviewContext/Wheelchair accessibility")
    veg_score        = context_scores.get("reviewContext/Vegetarian options")
    kid_score        = context_scores.get("reviewContext/Kid-friendliness")

    def avg_nonnull(*args):
        vals = [a for a in args if a is not None]
        return round(sum(vals)/len(vals), 2) if vals else None

    out["score_food"]          = _first(g_food,
                                        nlp_scores.get("Food Quality"),
                                        nlp_scores.get("Curry & Sauce"))
    out["score_service"]       = _first(g_service,
                                        avg_nonnull(wait_score,
                                                    nlp_scores.get("Service & Staff")))
    out["score_ambience"]      = _first(g_atmosphere,
                                        avg_nonnull(noise_score,
                                                    nlp_scores.get("Ambience & Atmosphere")))
    out["score_noise"]         = _first(noise_score,
                                        nlp_scores.get("Ambience & Atmosphere"))
    out["score_wait_time"]     = _first(wait_score,
                                        nlp_scores.get("Service & Staff"))
    out["score_parking"]       = _first(parking_score, parking_opt_score,
                                        nlp_scores.get("Location & Accessibility"))
    out["score_wheelchair"]    = _first(wheelchair_score,
                                        nlp_scores.get("Location & Accessibility"))
    out["score_vegetarian"]    = _first(veg_score,
                                        nlp_scores.get("Vegetarian & Vegan Options"))
    out["score_kid_friendly"]  = _first(kid_score)
    out["score_price"]         = nlp_scores.get("Price & Value")
    out["score_authenticity"]  = nlp_scores.get("Authenticity")
    out["score_spice"]         = nlp_scores.get("Spice Level")
    out["score_cleanliness"]   = nlp_scores.get("Cleanliness & Hygiene")
    out["score_chicken"]       = nlp_scores.get("Chicken Dishes")
    out["score_lamb"]          = nlp_scores.get("Lamb & Mutton Dishes")
    out["score_vegan_dishes"]  = nlp_scores.get("Vegetarian & Vegan Options")
    out["score_bread_rice"]    = nlp_scores.get("Bread & Rice")
    out["score_starters"]      = nlp_scores.get("Starters & Street Food")
    out["score_overall_nlp"]   = nlp_scores.get("Overall Experience")

    # ── Credibility weight ────────────────────────────────────────────────────
    n = out["reviewer_review_count"] or 1
    out["credibility_weight"] = round(min(1.0, 0.3 + (n / 100) * 0.7), 3)

    # ── Data source tag ───────────────────────────────────────────────────────
    out["data_source"] = (
        "google_ratings"  if has_google_all else
        "context_fields"  if context_scores else
        "nlp_text"        if nlp_scores else
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

    if SHEET_ID == "YOUR_SHEET_ID_HERE":
        print("ERROR: Set SHEET_ID at the top of this file")
        print("Find it in your Google Sheet URL:")
        print("https://docs.google.com/spreadsheets/d/THIS_PART/edit")
        exit(1)

    if APPS_SCRIPT_URL == "YOUR_APPS_SCRIPT_URL_HERE":
        print("ERROR: Set APPS_SCRIPT_URL at the top of this file")
        exit(1)

    print("="*60)
    print("PROCESS REVIEWS — No credentials needed")
    print("="*60)

    raw_df = read_sheet_public(SHEET_ID, RAW_REVIEWS_GID)
    if raw_df.empty:
        print("No data. Run Make.com scenario first.")
        exit()

    results     = []
    source_tally = {"google_ratings": 0, "context_fields": 0,
                    "nlp_text": 0, "no_data": 0}

    for i, row in raw_df.iterrows():
        name = str(row.get("title", row.get("name", "?")))[:35]
        print(f"[{i+1}/{len(raw_df)}] {name}")
        result = process_row(row.to_dict())
        results.append(result)
        source_tally[result["data_source"]] = \
            source_tally.get(result["data_source"], 0) + 1

    df_out = pd.DataFrame(results)

    print(f"\nData source breakdown:")
    for src, count in source_tally.items():
        pct = round(100*count/len(results)) if results else 0
        print(f"  {src:<20} {count:>4} ({pct}%)")

    print(f"\nWriting {len(df_out)} rows back via Apps Script...")
    written = write_processed(df_out, APPS_SCRIPT_URL)
    print(f"Done — {written} rows written to 'processed' tab.")
    print("Your dashboard will now show fresh data.")
