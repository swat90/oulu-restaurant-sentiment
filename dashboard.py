"""
dashboard.py
─────────────
WHERE IT RUNS: Streamlit Cloud (free, always online, public URL)
WHAT IT READS: "processed" tab of your Google Sheet via public CSV
NO AUTH NEEDED: Sheet must be set to "Anyone with link can view"

HOW TO RUN LOCALLY FIRST (to test):
  streamlit run src/dashboard.py

HOW TO DEPLOY:
  1. Push repo to GitHub
  2. Go to share.streamlit.io → New app
  3. Select your repo, set main file: src/dashboard.py
  4. Deploy → get public URL

ONLY ONE THING TO FILL IN: SHEET_ID and PROCESSED_GID below.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — fill these in
# ─────────────────────────────────────────────────────────────────────────────

# Your Google Sheet ID — from the URL between /d/ and /edit
SHEET_ID = "17ADm27u7yICbqD9etdiCNlZb-UlVzqPsbthozTiXgn0"

# GID of the "processed" tab — look at the URL when you click that tab
# e.g. https://docs.google.com/spreadsheets/d/.../edit#gid=1234567890
PROCESSED_GID = "2068389138"


# ─────────────────────────────────────────────────────────────────────────────
# TRANSLATIONS — add more languages by extending each dict
# ─────────────────────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "page_title":    "Oulu Restaurant Sentiment",
        "page_caption":  "Aspect-based analysis of Google Maps reviews · English & Finnish · Google structured ratings + NLP",
        "title":         "🍽️ Oulu Restaurant Sentiment",
        "filters":       "🔍 Filters",
        "filter_rest":   "Restaurant",
        "filter_stars":  "Minimum stars",
        "filter_meal":   "Meal Type",
        "filter_year":   "Year",
        "refresh":       "🔄 Refresh data",
        "auto_refresh":  "Auto-refreshes every 10 min",
        "metrics": {
            "total":     "Total Reviews",
            "rests":     "Restaurants",
            "avg_stars": "Avg Stars",
            "fi_reviews":"Finnish Reviews",
            "en_reviews":"English Reviews",
            "owner_resp":"Owner Responses",
        },
        "data_source_title": "How scores were computed",
        "source_labels": {
            "google_ratings":  "✅ Google's structured ratings",
            "context_scored":  "📋 Context fields (NLP scored)",
            "nlp_text":        "🤖 NLP on review text",
            "no_data":         "⚪ No scoreable data",
        },
        "tabs": [
            "📡 Aspect Scores",
            "🏪 By Restaurant",
            "📅 Trends",
            "📋 Context & Filters",
            "🍛 Food Deep Dive",
            "📄 Raw Data",
        ],
        "radar_title":    "Radar Chart",
        "bar_title":      "Score Summary",
        "heatmap_title":  "Heatmap — all aspects",
        "summary_table":  "Summary Table",
        "trend_title":    "Rating trend over time",
        "aspect_trend":   "Aspect trend",
        "select_aspect":  "Select aspect to track over time",
        "lang_trend":     "Review language over time",
        "context_caption":"These come directly from Google Maps structured fields.",
        "raw_ctx_title":  "Raw context text samples",
        "reviewer_title": "Reviewer breakdown",
        "local_guides":   "Local Guides",
        "avg_exp":        "Avg Reviewer Experience",
        "total_likes":    "Total Review Likes",
        "food_overview":  "Food aspect overview",
        "recommended":    "Dishes recommended by reviewers",
        "food_by_rest":   "Food scores by restaurant",
        "raw_data_title": "Processed reviews",
        "download":       "⬇️ Download full data as CSV",
        "no_data_msg":    "No processed data yet.",
        "no_match":       "No reviews match the current filters.",
    },
    "fi": {
        "page_title":    "Oulu Ravintola Sentimentti",
        "page_caption":  "Aspektipohjainen analyysi Google Maps -arvosteluista · Suomi & Englanti",
        "title":         "🍽️ Oulu Ravintola Sentimenttianalyysi",
        "filters":       "🔍 Suodattimet",
        "filter_rest":   "Ravintola",
        "filter_stars":  "Vähimmäistähdet",
        "filter_meal":   "Ateriatyyppi",
        "filter_year":   "Vuosi",
        "refresh":       "🔄 Päivitä tiedot",
        "auto_refresh":  "Päivittyy automaattisesti 10 min välein",
        "metrics": {
            "total":     "Arvosteluja yhteensä",
            "rests":     "Ravintoloita",
            "avg_stars": "Keskim. tähdet",
            "fi_reviews":"Suomenkieliset arvostelut",
            "en_reviews":"Englanninkieliset arvostelut",
            "owner_resp":"Omistajan vastaukset",
        },
        "data_source_title": "Miten pisteet laskettiin",
        "source_labels": {
            "google_ratings":  "✅ Googlen rakenteelliset arviot",
            "context_scored":  "📋 Kontekstikenttien NLP-pisteet",
            "nlp_text":        "🤖 NLP arvosteluista",
            "no_data":         "⚪ Ei pisteytettävää dataa",
        },
        "tabs": [
            "📡 Aspektipisteet",
            "🏪 Ravintoloittain",
            "📅 Trendit",
            "📋 Konteksti & Suodattimet",
            "🍛 Ruokasyvennys",
            "📄 Raakadata",
        ],
        "radar_title":    "Tutkakaavio",
        "bar_title":      "Pisteyhteenveto",
        "heatmap_title":  "Lämpökartta — kaikki aspektit",
        "summary_table":  "Yhteenvetotaulukko",
        "trend_title":    "Arvioiden trendi ajan myötä",
        "aspect_trend":   "Aspektitrendi",
        "select_aspect":  "Valitse seurattava aspekti",
        "lang_trend":     "Arvostelujen kieli ajan myötä",
        "context_caption":"Nämä tulevat suoraan Googlen rakenteellisista kentistä.",
        "raw_ctx_title":  "Kontekstikentät — esimerkkejä",
        "reviewer_title": "Arvostelijatilastot",
        "local_guides":   "Paikalliset oppaat",
        "avg_exp":        "Keskim. arvostelijan kokemus",
        "total_likes":    "Tykkäykset yhteensä",
        "food_overview":  "Ruoka-aspektit yleiskatsaus",
        "recommended":    "Suositellut ruoat",
        "food_by_rest":   "Ruokapisteet ravintoloittain",
        "raw_data_title": "Käsitellyt arvostelut",
        "download":       "⬇️ Lataa kaikki data CSV:nä",
        "no_data_msg":    "Ei käsiteltyä dataa vielä.",
        "no_match":       "Ei arvosteluja valituilla suodattimilla.",
    },
    "sv": {
        "page_title":    "Uleåborg Restaurang Sentiment",
        "page_caption":  "Aspektbaserad analys av Google Maps-recensioner",
        "title":         "🍽️ Uleåborg Restaurang Sentimentanalys",
        "filters":       "🔍 Filter",
        "filter_rest":   "Restaurang",
        "filter_stars":  "Lägsta stjärnor",
        "filter_meal":   "Måltidstyp",
        "filter_year":   "År",
        "refresh":       "🔄 Uppdatera data",
        "auto_refresh":  "Uppdateras var 10:e minut",
        "metrics": {
            "total":     "Recensioner totalt",
            "rests":     "Restauranger",
            "avg_stars": "Snitt stjärnor",
            "fi_reviews":"Finska recensioner",
            "en_reviews":"Engelska recensioner",
            "owner_resp":"Ägarens svar",
        },
        "data_source_title": "Hur poängen beräknades",
        "source_labels": {
            "google_ratings":  "✅ Googles strukturerade betyg",
            "context_scored":  "📋 Kontextfält (NLP-poäng)",
            "nlp_text":        "🤖 NLP på recensionstext",
            "no_data":         "⚪ Ingen poängsättbar data",
        },
        "tabs": [
            "📡 Aspektpoäng",
            "🏪 Per restaurang",
            "📅 Trender",
            "📋 Kontext & Filter",
            "🍛 Matfördjupning",
            "📄 Rådata",
        ],
        "radar_title":    "Radardiagram",
        "bar_title":      "Poängsammanfattning",
        "heatmap_title":  "Värmekarta — alla aspekter",
        "summary_table":  "Sammanfattningstabell",
        "trend_title":    "Betygstendens över tid",
        "aspect_trend":   "Aspekttendens",
        "select_aspect":  "Välj aspekt att följa",
        "lang_trend":     "Recensionsspråk över tid",
        "context_caption":"Dessa kommer direkt från Googles strukturerade fält.",
        "raw_ctx_title":  "Kontextfält — exempel",
        "reviewer_title": "Recensentstatistik",
        "local_guides":   "Lokala guider",
        "avg_exp":        "Snitt recensenterfarenhet",
        "total_likes":    "Totala gilla-markeringar",
        "food_overview":  "Mataspekter — översikt",
        "recommended":    "Rekommenderade rätter",
        "food_by_rest":   "Matpoäng per restaurang",
        "raw_data_title": "Bearbetade recensioner",
        "download":       "⬇️ Ladda ner all data som CSV",
        "no_data_msg":    "Ingen bearbetad data ännu.",
        "no_match":       "Inga recensioner matchar filtren.",
    },
}

LANG_OPTIONS = {"Suomi": "fi", "Svenska": "sv", "English": "en"}

# ─────────────────────────────────────────────────────────────────────────────
# SCORE COLUMNS → display labels
# ─────────────────────────────────────────────────────────────────────────────
SCORE_COLS = {
    "score_food":         "🍛 Food",
    "score_service":      "👨‍🍳 Service",
    "score_ambience":     "🌿 Ambience",
    "score_noise":        "🔊 Noise Level",
    "score_wait_time":    "⏱️ Wait Time",
    "score_parking":      "🅿️ Parking",
    "score_wheelchair":   "♿ Accessibility",
    "score_vegetarian":   "🥗 Veg Options",
    "score_kid_friendly": "👶 Kid Friendly",
    "score_price":        "💰 Price/Value",
    "score_authenticity": "🏆 Authenticity",
    "score_spice":        "🌶️ Spice Level",
    "score_cleanliness":  "🧼 Cleanliness",
    "score_chicken":      "🍗 Chicken",
    "score_lamb":         "🥩 Lamb/Mutton",
    "score_vegan_dishes": "🌱 Vegan Dishes",
    "score_bread_rice":   "🫓 Bread & Rice",
    "score_starters":     "🥙 Starters",
}

# Categorical context columns → chart labels
CONTEXT_CATS = {
    "ctx_meal_type":        "Meal Type",
    "ctx_order_type":       "Order Type",
    "ctx_group_size":       "Group Size",
    "ctx_seating_type":     "Seating Type",
    "ctx_dietary":          "Dietary Restrictions",
    "ctx_price_per_person": "Price per Person",
    "ctx_recommended":      "Recommended Dishes",
    "ctx_reservation":      "Reservation",
    "ctx_special_events":   "Special Events",
}

# Raw text context columns kept for reference
RAW_CTX = {
    "ctx_noise_raw":      "Noise",
    "ctx_wait_raw":       "Wait Time",
    "ctx_kid_raw":        "Kid Friendliness",
    "ctx_parking_raw":    "Parking",
    "ctx_wheelchair_raw": "Wheelchair",
    "ctx_vegetarian_raw": "Vegetarian Options",
}

# ─────────────────────────────────────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Oulu Restaurant Sentiment",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #2563eb; }
  [data-testid="stMetricLabel"] { font-size: 0.75rem; color: #64748b; }
  .section-title {
    font-size: 1rem; font-weight: 600; color: #1e293b;
    padding: 0.5rem 0; border-bottom: 2px solid #e2e8f0;
    margin: 1.5rem 0 1rem 0;
  }
  .score-bar { height: 8px; border-radius: 4px; background: #e2e8f0; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING — public CSV, no auth
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)   # refresh every 10 min
def load_data() -> pd.DataFrame:
    if "YOUR_SHEET_ID" in SHEET_ID:
        return pd.DataFrame()

    url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
           f"/export?format=csv&gid={PROCESSED_GID}")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"   # prevent â¬ / â encoding corruption
        df = pd.read_csv(StringIO(resp.text), encoding="utf-8")
        # Fix any remaining encoding issues in string columns
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].apply(
                lambda x: x.encode("latin-1").decode("utf-8")
                if isinstance(x, str) and "â" in x else x
            )
    except Exception as e:
        st.error(f"Cannot load sheet: {e}")
        return pd.DataFrame()

    # Numeric conversion
    for col in list(SCORE_COLS.keys()) + [
        "review_stars", "place_total_score",
        "credibility_weight", "likes_count", "reviewer_review_count",
        "lat", "lng",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Date parsing
    if "review_date" in df.columns:
        df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
        df["month"] = df["review_date"].dt.to_period("M").astype(str)
        df["year"]  = df["review_date"].dt.year.astype("Int64")

    # Boolean
    for col in ["is_local_guide", "owner_responded"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().isin(["true","1","yes"])

    return df

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame, T: dict) -> pd.DataFrame:
    st.sidebar.header(T["filters"])

    # Restaurant
    restaurants = sorted(df["restaurant"].dropna().unique())
    sel_r = st.sidebar.multiselect(
        T["filter_rest"], restaurants, default=list(restaurants)
    )

    # Language filter removed — all reviews in English after translation
    sel_l     = []
    lang_map  = {"en":"English","fi":"Finnish","ja":"Japanese","sv":"Swedish"}

    # Stars
    min_stars = st.sidebar.slider(T["filter_stars"], 1.0, 5.0, 1.0, 0.5)

    # Meal type
    if "ctx_meal_type" in df.columns:
        meal_opts = sorted(
            df["ctx_meal_type"].dropna().replace("", np.nan).dropna().unique()
        )
        sel_meal = st.sidebar.multiselect(T["filter_meal"], meal_opts) if meal_opts else []
    else:
        sel_meal = []

    # Visited period
    if "year" in df.columns:
        years = sorted(df["year"].dropna().astype(int).unique())
        if len(years) > 1:
            sel_year = st.sidebar.multiselect(T["filter_year"], years, default=years)
        else:
            sel_year = years
    else:
        sel_year = []

    st.sidebar.markdown("---")
    if st.sidebar.button(T["refresh"]):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.caption(T["auto_refresh"])

    # Apply filters
    mask = pd.Series(True, index=df.index)

    if sel_r:
        mask &= df["restaurant"].isin(sel_r)

    # language filter removed

    mask &= df["review_stars"].fillna(0) >= min_stars

    if sel_meal and "ctx_meal_type" in df.columns:
        mask &= df["ctx_meal_type"].isin(sel_meal)

    if sel_year and "year" in df.columns:
        mask &= df["year"].isin(sel_year)

    return df[mask].copy()

# ─────────────────────────────────────────────────────────────────────────────
# HELPER CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def score_color(score):
    """Return hex color for a 1-5 score."""
    if score is None or np.isnan(score):
        return "#e2e8f0"
    if score >= 4.5: return "#16a34a"
    if score >= 3.5: return "#65a30d"
    if score >= 2.5: return "#ca8a04"
    if score >= 1.5: return "#ea580c"
    return "#dc2626"

def cat_chart(df, col, label, max_items=10):
    """Bar or pie chart for a categorical column."""
    counts = (
        df[col]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", np.nan)
        .dropna()
        .value_counts()
        .head(max_items)
        .reset_index()
    )
    counts.columns = ["category", "count"]
    if counts.empty:
        return None
    if len(counts) <= 5:
        fig = px.pie(
            counts, names="category", values="count",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=260, margin=dict(t=10,b=5,l=5,r=5),
                          showlegend=True)
    else:
        # Truncate long labels so they don't overlap axis
        counts["short_label"] = counts["category"].apply(
            lambda x: x[:35] + "…" if len(str(x)) > 35 else x
        )
        fig = px.bar(
            counts, x="count", y="short_label",
            orientation="h",
            color="count",
            color_continuous_scale=["#dbeafe","#2563eb"],
            hover_data={"category": True, "count": True, "short_label": False},
        )
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis=dict(title="", tickfont=dict(size=11)),
            xaxis=dict(title="count"),
            # Extra left margin so long labels have room
            margin=dict(t=10, b=5, l=160, r=20),
            height=max(260, 35 * len(counts)),
        )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── Language selector — top of sidebar, Finnish default ──────────────────
    st.sidebar.markdown("### 🌐 Kieli / Språk / Language")
    lang_label = st.sidebar.selectbox(
        "",
        options=list(LANG_OPTIONS.keys()),
        index=0,   # Suomi is default
        label_visibility="collapsed",
    )
    lang_code = LANG_OPTIONS[lang_label]
    T = TRANSLATIONS[lang_code]
    st.sidebar.markdown("---")

    st.title(T["title"])
    st.caption(T["page_caption"])

    # Config check
    if "YOUR_SHEET_ID" in SHEET_ID:
        st.warning("⚠️ Set SHEET_ID and PROCESSED_GID at the top of dashboard.py")
        st.code(
            'SHEET_ID      = "1BxiMVs..."\n'
            'PROCESSED_GID = "1234567890"'
        )
        st.stop()

    with st.spinner("Loading data from Google Sheets..."):
        raw_df = load_data()

    if raw_df.empty:
        st.warning(T["no_data_msg"])
        st.markdown("""
        **To populate data:**
        1. Run your Make.com scenario to scrape reviews
        2. Run `python src/process_reviews.py` locally
        3. Come back here — dashboard reads from Google Sheets automatically
        """)
        st.stop()

    df = sidebar_filters(raw_df, T)

    if df.empty:
        st.warning(T["no_match"])
        st.stop()

    avail_scores = [c for c in SCORE_COLS if c in df.columns and df[c].notna().any()]

    # ═══════════════════════════════════════════════════════════════
    # TOP METRICS ROW
    # ═══════════════════════════════════════════════════════════════
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.metric(T["metrics"]["total"], len(df))
    m2.metric(T["metrics"]["rests"], df["restaurant"].nunique())
    m3.metric(T["metrics"]["avg_stars"], f'{df["review_stars"].mean():.2f} ★'
                                    if "review_stars" in df.columns else "–")
    m4.metric(T["metrics"]["fi_reviews"], int(df["language"].str.startswith("fi").sum())
                                    if "language" in df.columns else 0)
    m5.metric(T["metrics"]["en_reviews"], int(df["language"].str.startswith("en").sum())
                                    if "language" in df.columns else 0)
    m6.metric(T["metrics"]["owner_resp"], int(df["owner_responded"].sum())
                                    if "owner_responded" in df.columns else 0)

    # Data source info
    if "data_source" in df.columns:
        src = df["data_source"].value_counts()
        with st.expander(f"ℹ️ {T['data_source_title']}"):
            cols = st.columns(min(4, len(src)))
            for i,(s,c) in enumerate(src.items()):
                cols[i].metric(T["source_labels"].get(s, s), f"{c} ({round(100*c/len(df))}%)")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════
    # TABS
    # ═══════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(T["tabs"])

    # ──────────────────────────────────────────────────────────────
    # TAB 1 — ASPECT SCORES
    # ──────────────────────────────────────────────────────────────
    with tab1:
        avg = (df[avail_scores].mean()
               .rename(SCORE_COLS)
               .sort_values(ascending=False)
               .dropna())

        col_l, col_r = st.columns([1, 1])

        with col_l:
            st.markdown(f'<div class="section-title">{T["radar_title"]}</div>',
                        unsafe_allow_html=True)
            labels = avg.index.tolist()
            values = avg.values.tolist()
            fig = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=labels + [labels[0]],
                fill="toself",
                fillcolor="rgba(37,99,235,0.12)",
                line=dict(color="#2563eb", width=2),
                marker=dict(size=5, color="#2563eb"),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,5], visible=True,
                                           tickvals=[1,2,3,4,5])),
                showlegend=False, height=400,
                margin=dict(t=20,b=20,l=40,r=40),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown(f'<div class="section-title">{T["bar_title"]}</div>',
                        unsafe_allow_html=True)
            bar_df = pd.DataFrame({
                "aspect": avg.index.tolist(),
                "score":  avg.values.tolist(),
            }).sort_values("score", ascending=True)
            fig2 = px.bar(
                bar_df,
                x="score",
                y="aspect",
                orientation="h",
                color="score",
                color_continuous_scale=["#dc2626","#f59e0b","#16a34a"],
                range_color=[1, 5],
                text=bar_df["score"].round(2),
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(
                xaxis=dict(range=[0, 5.8], title=""),
                yaxis=dict(title=""),
                height=400,
                coloraxis_showscale=False,
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=80),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ──────────────────────────────────────────────────────────────
    # TAB 2 — BY RESTAURANT
    # ──────────────────────────────────────────────────────────────
    with tab2:
        rest_avg = df.groupby("restaurant")[avail_scores].mean()
        rest_avg["⭐ Avg Stars"]     = df.groupby("restaurant")["review_stars"].mean()
        rest_avg["# Reviews"]        = df.groupby("restaurant").size()
        rest_avg["Owner Responses %"]= (
            df.groupby("restaurant")["owner_responded"].mean() * 100
            if "owner_responded" in df.columns else np.nan
        )

        score_labels = [SCORE_COLS[c] for c in avail_scores]

        st.markdown(f'<div class="section-title">{T["heatmap_title"]}</div>',
                    unsafe_allow_html=True)
        z_vals = rest_avg[avail_scores].values.round(2)
        fig_h = go.Figure(go.Heatmap(
            z=z_vals,
            x=score_labels,
            y=rest_avg.index.tolist(),
            colorscale=[[0,"#dc2626"],[0.5,"#fef9c3"],[1,"#16a34a"]],
            zmin=1, zmax=5,
            text=np.where(np.isnan(z_vals.astype(float)), "",
                          z_vals.astype(str)),
            texttemplate="%{text}",
            hovertemplate="%{y}<br>%{x}: %{z:.2f}<extra></extra>",
        ))
        fig_h.update_layout(
            height=max(200, 80 * len(rest_avg)),
            margin=dict(t=10,b=80,l=10,r=10),
            xaxis=dict(tickangle=-30),
        )
        st.plotly_chart(fig_h, use_container_width=True)

        st.markdown(f'<div class="section-title">{T["summary_table"]}</div>',
                    unsafe_allow_html=True)
        summary_cols = ["⭐ Avg Stars","# Reviews","Owner Responses %"]
        avail_summary = [c for c in summary_cols if c in rest_avg.columns]
        st.dataframe(
            rest_avg[avail_summary].round(2)
            .sort_values("⭐ Avg Stars", ascending=False),
            use_container_width=True,
        )

    # ──────────────────────────────────────────────────────────────
    # TAB 3 — TRENDS OVER TIME
    # ──────────────────────────────────────────────────────────────
    with tab3:
        if "month" not in df.columns or df["month"].isna().all():
            st.info("No date data available.")
        else:
            st.markdown(f'<div class="section-title">{T["trend_title"]}</div>',
                        unsafe_allow_html=True)

            trend = df.groupby("month").agg(
                avg_stars    = ("review_stars","mean"),
                review_count = ("review_stars","count"),
            ).reset_index().sort_values("month")

            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(
                x=trend["month"], y=trend["avg_stars"].round(2),
                mode="lines+markers", name="Avg Stars",
                line=dict(color="#2563eb",width=2),
                marker=dict(size=7),
                yaxis="y",
            ))
            fig_t.add_trace(go.Bar(
                x=trend["month"], y=trend["review_count"],
                name="# Reviews", yaxis="y2",
                marker_color="rgba(37,99,235,0.1)",
                marker_line_color="rgba(37,99,235,0.3)",
                marker_line_width=1,
            ))
            fig_t.update_layout(
                yaxis =dict(title="Avg Stars", range=[1,5.2]),
                yaxis2=dict(title="Review Count", overlaying="y",
                            side="right", showgrid=False),
                legend=dict(x=0,y=1.1,orientation="h"),
                height=300, margin=dict(t=30,b=10),
            )
            st.plotly_chart(fig_t, use_container_width=True)

            # Per-aspect trend
            st.markdown(f'<div class="section-title">{T["aspect_trend"]}</div>',
                        unsafe_allow_html=True)
            sel_asp = st.selectbox(
                T["select_aspect"],
                [SCORE_COLS[c] for c in avail_scores],
            )
            rev_map = {v: k for k,v in SCORE_COLS.items()}
            col_key = rev_map.get(sel_asp)
            if col_key and col_key in df.columns:
                asp_t = (df.dropna(subset=[col_key])
                           .groupby("month")[col_key]
                           .mean()
                           .reset_index()
                           .sort_values("month"))
                fig_a = px.line(
                    asp_t, x="month", y=col_key,
                    markers=True,
                    labels={col_key: sel_asp, "month":"Month"},
                    color_discrete_sequence=["#7c3aed"],
                )
                fig_a.update_layout(
                    yaxis=dict(range=[1,5.2]),
                    height=260, margin=dict(t=10,b=10),
                )
                st.plotly_chart(fig_a, use_container_width=True)

            # Language trend
            if "language" in df.columns:
                st.markdown(f'<div class="section-title">{T["lang_trend"]}</div>',
                            unsafe_allow_html=True)
                lang_trend = (df.assign(lang_short=df["language"].str[:2])
                               .groupby(["month","lang_short"])
                               .size()
                               .reset_index(name="count")
                               .sort_values("month"))
                lang_trend["language"] = lang_trend["lang_short"].map(
                    {"en":"English","fi":"Finnish","ja":"Japanese"}
                ).fillna(lang_trend["lang_short"])
                fig_l = px.bar(
                    lang_trend, x="month", y="count",
                    color="language", barmode="stack",
                    color_discrete_sequence=["#2563eb","#7c3aed","#059669"],
                    labels={"count":"Reviews","month":"Month"},
                )
                fig_l.update_layout(height=260,margin=dict(t=10,b=10))
                st.plotly_chart(fig_l, use_container_width=True)

    # ──────────────────────────────────────────────────────────────
    # TAB 4 — CONTEXT & FILTERS
    # ──────────────────────────────────────────────────────────────
    with tab4:
        st.caption(T["context_caption"])

        avail_cats = [
            (col, label) for col, label in CONTEXT_CATS.items()
            if col in df.columns
            and df[col].astype(str).str.strip().replace("",np.nan).notna().any()
        ]

        if not avail_cats:
            st.info("No categorical context data available yet.")
        else:
            cols_per_row = 3
            for i in range(0, len(avail_cats), cols_per_row):
                row = avail_cats[i:i+cols_per_row]
                rcols = st.columns(cols_per_row)
                for j,(col,label) in enumerate(row):
                    fig = cat_chart(df, col, label)
                    if fig:
                        rcols[j].markdown(
                            f'<div class="section-title">{label}</div>',
                            unsafe_allow_html=True,
                        )
                        rcols[j].plotly_chart(fig, use_container_width=True)

        # Raw context text samples
        st.markdown(f'<div class="section-title">{T["raw_ctx_title"]}</div>',
                    unsafe_allow_html=True)

        avail_raw = [(col, label) for col, label in RAW_CTX.items()
                     if col in df.columns
                     and df[col].astype(str).str.strip().replace("",np.nan).notna().any()]

        if avail_raw:
            sample_cols = st.columns(min(3, len(avail_raw)))
            for j, (col, label) in enumerate(avail_raw[:3]):
                with sample_cols[j]:
                    st.write(f"**{label}**")
                    samples = (
                        df[col].dropna()
                        .astype(str).str.strip()
                        .replace("",np.nan).dropna()
                        .value_counts()
                        .head(6)
                        .reset_index()
                    )
                    samples.columns = ["value","count"]
                    for _, r in samples.iterrows():
                        st.write(f"- {r['value']} ({r['count']}×)")

        # Reviewer stats
        st.markdown(f'<div class="section-title">{T["reviewer_title"]}</div>',
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if "is_local_guide" in df.columns:
            guide_pct = round(100 * df["is_local_guide"].mean())
            c1.metric(T["local_guides"], f"{guide_pct}%")
        if "reviewer_review_count" in df.columns:
            c2.metric(T["avg_exp"],
                      f"{df['reviewer_review_count'].median():.0f}")
        if "likes_count" in df.columns:
            c3.metric(T["total_likes"], int(df["likes_count"].sum()))

    # ──────────────────────────────────────────────────────────────
    # TAB 5 — FOOD DEEP DIVE
    # ──────────────────────────────────────────────────────────────
    with tab5:
        food_score_cols = {
            "score_food":         "🍛 Overall Food",
            "score_authenticity": "🏆 Authenticity",
            "score_spice":        "🌶️ Spice Level",
            "score_cleanliness":  "🧼 Cleanliness",
            "score_chicken":      "🍗 Chicken",
            "score_lamb":         "🥩 Lamb/Mutton",
            "score_vegan_dishes": "🌱 Vegan Dishes",
            "score_bread_rice":   "🫓 Bread & Rice",
            "score_starters":     "🥙 Starters",
            "score_vegetarian":   "🥗 Veg Options",
        }
        avail_food = {c:l for c,l in food_score_cols.items()
                      if c in df.columns and df[c].notna().any()}

        if not avail_food:
            st.info(
                "No food-specific scores yet. "
                "These come from NLP — make sure reviews have enough text."
            )
        else:
            food_avg = (df[list(avail_food)]
                        .mean()
                        .rename(avail_food)
                        .sort_values(ascending=False)
                        .dropna())

            st.markdown(f'<div class="section-title">{T["food_overview"]}</div>',
                        unsafe_allow_html=True)
            food_bar_df = pd.DataFrame({
                "aspect": food_avg.index.tolist(),
                "score":  food_avg.values.tolist(),
            }).sort_values("score", ascending=False)
            fig_f = px.bar(
                food_bar_df,
                x="aspect",
                y="score",
                color="score",
                color_continuous_scale=["#dc2626","#f59e0b","#16a34a"],
                range_color=[1, 5],
                text=food_bar_df["score"].round(2),
                labels={"aspect": "", "score": "Score"},
            )
            fig_f.update_traces(textposition="outside")
            fig_f.update_layout(
                xaxis_title="", yaxis=dict(range=[0,5.8]),
                coloraxis_showscale=False, height=350,
                margin=dict(t=10,b=10),
            )
            st.plotly_chart(fig_f, use_container_width=True)

            # Recommended dishes
            if "ctx_recommended" in df.columns:
                st.markdown(
                    f'<div class="section-title">{T["recommended"]}</div>',
                    unsafe_allow_html=True
                )
                dishes = (
                    df["ctx_recommended"]
                    .dropna().astype(str)
                    .str.split(",").explode()
                    .str.strip().str.lower()
                    .replace("",np.nan).dropna()
                )
                if not dishes.empty:
                    dc = dishes.value_counts().head(15).reset_index()
                    dc.columns = ["dish","mentions"]
                    fig_d = px.bar(
                        dc, x="mentions", y="dish",
                        orientation="h",
                        color="mentions",
                        color_continuous_scale=["#dbeafe","#1d4ed8"],
                        text="mentions",
                    )
                    fig_d.update_layout(
                        height=max(250, 28*len(dc)),
                        coloraxis_showscale=False,
                        margin=dict(t=10,b=10,r=10),
                    )
                    st.plotly_chart(fig_d, use_container_width=True)

            # Per-restaurant food comparison
            st.markdown(f'<div class="section-title">{T["food_by_rest"]}</div>',
                        unsafe_allow_html=True)
            food_by_rest = (df.groupby("restaurant")[list(avail_food)]
                              .mean()
                              .rename(columns=avail_food)
                              .round(2))
            st.dataframe(food_by_rest, use_container_width=True)

    # ──────────────────────────────────────────────────────────────
    # TAB 6 — RAW DATA
    # ──────────────────────────────────────────────────────────────
    with tab6:
        st.markdown(f'<div class="section-title">{T["raw_data_title"]}</div>',
                    unsafe_allow_html=True)

        display_cols = (
            ["restaurant","review_date","language","review_stars","data_source"]
            + avail_scores[:6]
            + ["text_original","text_translated"]
        )
        show_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(
            df[show_cols].sort_values("review_date", ascending=False)
            .reset_index(drop=True)
            .round(2),
            use_container_width=True,
            height=400,
        )

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            T["download"],
            data=csv,
            file_name=f"oulu_sentiment_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.caption(
        f"Last loaded: {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
        "Source: Google Sheets (public) · "
        "Sentiment: nlptown/bert-base-multilingual"
    )

if __name__ == "__main__":
    main()
