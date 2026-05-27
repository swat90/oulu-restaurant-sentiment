"""
_column_aliases.py
───────────────────
Maps ALL possible incoming column names to a single canonical name.

WHY: Make.com Array Aggregator flattens nested JSON using underscores:
  reviewDetailedRating.Food   → reviewDetailedRating_Food
  reviewContext.Noise level   → reviewContext_Noise_level

But if you run the script on raw Apify CSV exports, columns use slashes:
  reviewDetailedRating/Food
  reviewContext/Noise level

This module normalises both into the canonical slash form so the rest
of the code works identically regardless of data source.
"""

# canonical_name → list of aliases (any of which may appear in the data)
ALIASES = {
    # ── Google detailed ratings ────────────────────────────────────────────
    "reviewDetailedRating/Food": [
        "reviewDetailedRating_Food",
        "reviewDetailedRating/Food",
        "Food Rating",
    ],
    "reviewDetailedRating/Service": [
        "reviewDetailedRating_Service",
        "reviewDetailedRating/Service",
        "Service Rating",
    ],
    "reviewDetailedRating/Atmosphere": [
        "reviewDetailedRating_Atmosphere",
        "reviewDetailedRating/Atmosphere",
        "Atmosphere Rating",
    ],

    # ── Review context — scored fields ────────────────────────────────────
    "reviewContext/Noise level": [
        "reviewContext_Noise_level",
        "reviewContext_Noise level",
        "reviewContext/Noise level",
        "Noise level",
    ],
    "reviewContext/Wait time": [
        "reviewContext_Wait_time",
        "reviewContext_Wait time",
        "reviewContext/Wait time",
        "Wait time",
    ],
    "reviewContext/Kid-friendliness": [
        "reviewContext_Kid_friendliness",
        "reviewContext_Kid-friendliness",
        "reviewContext/Kid-friendliness",
        "Kid-friendliness",
        "Kid friendliness",
    ],
    "reviewContext/Parking": [
        "reviewContext_Parking",
        "reviewContext/Parking",
        "Parking",
    ],
    "reviewContext/Parking options": [
        "reviewContext_Parking_options",
        "reviewContext_Parking options",
        "reviewContext/Parking options",
        "Parking options",
    ],
    "reviewContext/Parking space": [
        "reviewContext_Parking_space",
        "reviewContext_Parking space",
        "reviewContext/Parking space",
        "Parking space",
    ],
    "reviewContext/Wheelchair accessibility": [
        "reviewContext_Wheelchair_accessibility",
        "reviewContext_Wheelchair accessibility",
        "reviewContext/Wheelchair accessibility",
        "Wheelchair accessibility",
        "Wheelchair",
    ],
    "reviewContext/Vegetarian options": [
        "reviewContext_Vegetarian_options",
        "reviewContext_Vegetarian options",
        "reviewContext/Vegetarian options",
        "Vegetarian options",
    ],

    # ── Review context — categorical fields ───────────────────────────────
    "reviewContext/Meal type": [
        "reviewContext_Meal_type",
        "reviewContext_Meal type",
        "reviewContext/Meal type",
        "Meal type",
    ],
    "reviewContext/Order type": [
        "reviewContext_Order_type",
        "reviewContext_Order type",
        "reviewContext/Order type",
        "Order type",
    ],
    "reviewContext/Group size": [
        "reviewContext_Group_size",
        "reviewContext_Group size",
        "reviewContext/Group size",
        "Group size",
    ],
    "reviewContext/Seating type": [
        "reviewContext_Seating_type",
        "reviewContext_Seating type",
        "reviewContext/Seating type",
        "Seating type",
    ],
    "reviewContext/Dietary restrictions": [
        "reviewContext_Dietary_restrictions",
        "reviewContext_Dietary restrictions",
        "reviewContext/Dietary restrictions",
        "Dietary restrictions",
    ],
    "reviewContext/Price per person": [
        "reviewContext_Price_per_person",
        "reviewContext_Price per person",
        "reviewContext/Price per person",
        "Price per person",
    ],
    "reviewContext/Recommended dishes": [
        "reviewContext_Recommended_dishes",
        "reviewContext_Recommended dishes",
        "reviewContext/Recommended dishes",
        "Recommended dishes",
    ],
    "reviewContext/Reservation": [
        "reviewContext_Reservation",
        "reviewContext/Reservation",
        "Reservation",
    ],
    "reviewContext/Special events": [
        "reviewContext_Special_events",
        "reviewContext_Special events",
        "reviewContext/Special events",
        "Special events",
    ],
    "reviewContext/Special offers": [
        "reviewContext_Special_offers",
        "reviewContext_Special offers",
        "reviewContext/Special offers",
        "Special offers",
    ],

    # ── Location ──────────────────────────────────────────────────────────
    "location/lat": [
        "location_lat",
        "location/lat",
        "lat",
    ],
    "location/lng": [
        "location_lng",
        "location/lng",
        "lng",
    ],
}

# Build reverse map: alias → canonical
_REVERSE: dict[str, str] = {}
for canonical, aliases in ALIASES.items():
    for alias in aliases:
        _REVERSE[alias] = canonical


def normalise_row(row: dict) -> dict:
    """
    Return a copy of `row` where any aliased column names
    are replaced with their canonical names.
    Keys not in the alias table are kept as-is.
    """
    out = {}
    for k, v in row.items():
        canonical = _REVERSE.get(k, k)
        # If canonical already exists (from a different alias), don't overwrite
        if canonical not in out:
            out[canonical] = v
        elif v not in (None, "", "nan"):
            out[canonical] = v   # prefer non-empty value
    return out


def normalise_columns(df) -> "pd.DataFrame":
    """Rename DataFrame columns to canonical names."""
    rename_map = {c: _REVERSE.get(c, c) for c in df.columns}
    return df.rename(columns=rename_map)
