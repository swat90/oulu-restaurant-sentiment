"""
dashboard.py — Oulu Restaurant Sentiment Dashboard
────────────────────────────────────────────────────
Reads from Google Sheets via public CSV URL — zero credentials needed.
Sheet must be set to "Anyone with link can view".

Run locally:  streamlit run src/dashboard.py
Deploy free:  share.streamlit.io

Only ONE thing to configure — paste your Sheet ID below.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import StringIO
import requests

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — only this needs changing
# ─────────────────────────────────────────────────────────────────────────────
SHEET_ID       = "YOUR_SHEET_ID_HERE"
PROCESSED_GID  = ""   # GID of "processed" tab — find in URL when tab is open

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Oulu Restaurant Sentiment",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stMetricValue"] { font-size: 2rem; color: #2563eb; }
  .section-header {
    font-size: 1.1rem; font-weight: 600; color: #0f172a;
    border-bottom: 2px solid #e2e8f0; padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem;
  }
  .source-tag {
    display: inline-block; font-size: 0.65rem; font-weight: 700;
    padding: 0.15rem 0.5rem; border-radius: 100px; margin-left: 0.4rem;
  }
</style>
""", unsafe_allow_html=True)

# Score columns and their display labels
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

# Categorical context columns for charts
CONTEXT_CATS = {
    "ctx_meal_type":       "Meal Type",
    "ctx_order_type":      "Order Type",
    "ctx_group_size":      "Group Size",
    "ctx_seating_type":    "Seating Type",
    "ctx_dietary":         "Dietary Restrictions",
    "ctx_price_per_person":"Price per Person",
    "ctx_recommended_dishes": "Recommended Dishes",
}

# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data():
    """Load processed sheet — public CSV, no auth."""
    if SHEET_ID == "YOUR_SHEET_ID_HERE":
        return pd.DataFrame()

    gid = PROCESSED_GID or "0"
    url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
           f"/export?format=csv&gid={gid}")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df   = pd.read_csv(StringIO(resp.text))
    except Exception as e:
        st.error(f"Could not load sheet: {e}")
        return pd.DataFrame()

    # Type cleanup
    for col in SCORE_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["review_stars", "place_total_score", "credibility_weight",
                "likes_count", "reviewer_review_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "review_date" in df.columns:
        df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
        df["month"]  = df["review_date"].dt.to_period("M").astype(str)
        df["year"]   = df["review_date"].dt.year

    return df

# ─────────────────────────────────────────────────────────────────────────────
def sidebar_filters(df):
    st.sidebar.header("🔍 Filters")

    restaurants = sorted(df["restaurant"].dropna().unique().tolist())
    sel_r = st.sidebar.multiselect("Restaurant", restaurants, default=restaurants)

    langs_raw = df["language"].dropna().unique().tolist()
    lang_map  = {"en": "English", "fi": "Finnish", "ja": "Japanese"}
    langs     = sorted(set(lang_map.get(l[:2], l) for l in langs_raw))
    sel_l     = st.sidebar.multiselect("Review Language", langs, default=langs)

    min_stars = st.sidebar.slider("Minimum review stars", 1.0, 5.0, 1.0, 0.5)

    meal_types = [v for v in df["ctx_meal_type"].dropna().unique() if v] if "ctx_meal_type" in df.columns else []
    sel_meal = st.sidebar.multiselect("Meal Type", meal_types) if meal_types else []

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.caption("Data refreshes every 10 min")

    mask = pd.Series([True] * len(df), index=df.index)
    if sel_r:
        mask &= df["restaurant"].isin(sel_r)
    if sel_l:
        mask &= df["language"].apply(
            lambda l: lang_map.get(str(l)[:2], l) if pd.notna(l) else False
        ).isin(sel_l)
    if min_stars > 1.0:
        mask &= df["review_stars"].fillna(0) >= min_stars
    if sel_meal and "ctx_meal_type" in df.columns:
        mask &= df["ctx_meal_type"].isin(sel_meal)

    return df[mask]

# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.title("🍽️ Oulu Restaurant Sentiment Dashboard")
    st.caption(
        "Aspect-based analysis of Google Maps reviews · "
        "English & Finnish · Structured Google ratings + NLP"
    )

    if SHEET_ID == "YOUR_SHEET_ID_HERE":
        st.warning("Set SHEET_ID at the top of dashboard.py")
        st.code('SHEET_ID = "your-google-sheet-id-here"')
        st.stop()

    with st.spinner("Loading..."):
        raw_df = load_data()

    if raw_df.empty:
        st.warning("No processed data yet. Run process_reviews.py first.")
        st.stop()

    df = sidebar_filters(raw_df)
    if df.empty:
        st.warning("No reviews match the current filters.")
        st.stop()

    # Available score cols that actually have data
    avail_scores = [c for c in SCORE_COLS if c in df.columns and df[c].notna().any()]

    # ── TOP METRICS ───────────────────────────────────────────────────────────
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Reviews",         len(df))
    c2.metric("Restaurants",     df["restaurant"].nunique())
    c3.metric("Avg Stars",       f"{df['review_stars'].mean():.2f} ★"
                                  if "review_stars" in df.columns else "–")
    c4.metric("Finnish Reviews", int((df["language"].str.startswith("fi")).sum()))
    c5.metric("English Reviews", int((df["language"].str.startswith("en")).sum()))
    c6.metric("Owner Responses", int(df["owner_responded"].sum())
                                  if "owner_responded" in df.columns else 0)

    st.markdown("---")

    # ── DATA SOURCE BREAKDOWN ─────────────────────────────────────────────────
    if "data_source" in df.columns:
        src_counts = df["data_source"].value_counts()
        with st.expander("ℹ️ Data source breakdown (how scores were computed)"):
            src_map = {
                "google_ratings":  "✅ Google's own Food/Service/Atmosphere ratings",
                "context_fields":  "📋 Structured context (noise, wait, parking, etc.)",
                "nlp_text":        "🤖 NLP model on review text",
                "no_data":         "⚪ No rating data available",
            }
            cols = st.columns(len(src_counts))
            for i, (src, count) in enumerate(src_counts.items()):
                cols[i].metric(
                    src_map.get(src, src),
                    f"{count} ({round(100*count/len(df))}%)"
                )

    # ── TAB LAYOUT ────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📡 Aspect Scores",
        "🏪 Restaurant Comparison",
        "📅 Trends Over Time",
        "📋 Context Insights",
        "🍛 Food Deep Dive",
    ])

    # ── TAB 1: ASPECT SCORES ──────────────────────────────────────────────────
    with tab1:
        avg_scores = (
            df[avail_scores].mean()
            .reset_index()
            .rename(columns={"index":"col", 0:"score"})
        )
        avg_scores["label"] = avg_scores["col"].map(SCORE_COLS)
        avg_scores = avg_scores.dropna(subset=["label"]).sort_values("score")

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-header">Radar View</div>',
                        unsafe_allow_html=True)
            radar_labels = avg_scores["label"].tolist()
            radar_vals   = avg_scores["score"].tolist()
            fig = go.Figure(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                fillcolor="rgba(37,99,235,0.12)",
                line=dict(color="#2563eb", width=2),
                marker=dict(size=5),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,5], visible=True)),
                showlegend=False, height=380,
                margin=dict(t=20,b=20,l=30,r=30),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-header">Bar View</div>',
                        unsafe_allow_html=True)
            fig2 = px.bar(
                avg_scores,
                x="score", y="label", orientation="h",
                color="score",
                color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                range_color=[1,5],
                text=avg_scores["score"].round(2),
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(
                height=380, showlegend=False, coloraxis_showscale=False,
                xaxis=dict(range=[0,5.5]),
                margin=dict(t=10,b=10,l=10,r=80),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 2: RESTAURANT COMPARISON ─────────────────────────────────────────
    with tab2:
        rest_avgs = df.groupby("restaurant")[avail_scores].mean().reset_index()
        rest_avgs["review_count"] = df.groupby("restaurant").size().values
        rest_avgs["avg_stars"]    = df.groupby("restaurant")["review_stars"].mean().values

        # Rename for display
        rename_map = {c: SCORE_COLS[c] for c in avail_scores}
        display_df = rest_avgs.rename(columns=rename_map)
        score_labels = [SCORE_COLS[c] for c in avail_scores]

        # Heatmap
        st.markdown('<div class="section-header">Aspect Heatmap by Restaurant</div>',
                    unsafe_allow_html=True)
        fig_heat = go.Figure(data=go.Heatmap(
            z=rest_avgs[avail_scores].values.round(2),
            x=score_labels,
            y=rest_avgs["restaurant"].tolist(),
            colorscale=[[0,"#ef4444"],[0.5,"#fef9c3"],[1,"#22c55e"]],
            zmin=1, zmax=5,
            text=rest_avgs[avail_scores].values.round(1),
            texttemplate="%{text}",
        ))
        fig_heat.update_layout(
            height=max(250, 70*rest_avgs["restaurant"].nunique()),
            margin=dict(t=10,b=10),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Summary table
        st.markdown('<div class="section-header">Summary Table</div>',
                    unsafe_allow_html=True)
        summary = rest_avgs[["restaurant","review_count","avg_stars"]].copy()
        summary["avg_stars"] = summary["avg_stars"].round(2)
        st.dataframe(
            summary.sort_values("avg_stars", ascending=False),
            use_container_width=True, hide_index=True,
        )

    # ── TAB 3: TRENDS OVER TIME ───────────────────────────────────────────────
    with tab3:
        if "month" not in df.columns or df["month"].isna().all():
            st.info("No date data available for trend analysis.")
        else:
            st.markdown('<div class="section-header">Overall Rating Trend</div>',
                        unsafe_allow_html=True)
            trend = df.groupby("month").agg(
                avg_stars=("review_stars","mean"),
                review_count=("review_stars","count"),
            ).reset_index()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=trend["month"], y=trend["avg_stars"].round(2),
                mode="lines+markers", name="Avg Stars",
                line=dict(color="#2563eb", width=2),
                marker=dict(size=7),
            ))
            fig_trend.add_trace(go.Bar(
                x=trend["month"], y=trend["review_count"],
                name="Review Count", yaxis="y2",
                marker_color="rgba(37,99,235,0.1)",
            ))
            fig_trend.update_layout(
                yaxis=dict(title="Avg Stars", range=[1,5]),
                yaxis2=dict(title="Review Count", overlaying="y", side="right"),
                height=320, margin=dict(t=10,b=10),
                legend=dict(x=0, y=1),
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            # Aspect trend for selected aspect
            sel_aspect = st.selectbox(
                "Aspect trend", [SCORE_COLS[c] for c in avail_scores]
            )
            col_key = {v:k for k,v in SCORE_COLS.items()}.get(sel_aspect)
            if col_key and col_key in df.columns:
                asp_trend = df.groupby("month")[col_key].mean().reset_index()
                fig_asp = px.line(
                    asp_trend, x="month", y=col_key,
                    markers=True,
                    labels={col_key: sel_aspect, "month": "Month"},
                    color_discrete_sequence=["#7c3aed"],
                )
                fig_asp.update_layout(
                    height=260, yaxis=dict(range=[1,5]),
                    margin=dict(t=10,b=10),
                )
                st.plotly_chart(fig_asp, use_container_width=True)

    # ── TAB 4: CONTEXT INSIGHTS ───────────────────────────────────────────────
    with tab4:
        st.markdown(
            "These come directly from Google Maps structured data — "
            "no model needed.",
        )
        avail_cats = [(col, label) for col, label in CONTEXT_CATS.items()
                      if col in df.columns and df[col].notna().any()
                      and df[col].astype(str).str.strip().ne("").any()]

        if not avail_cats:
            st.info("No categorical context data available yet.")
        else:
            cols_per_row = 2
            for i in range(0, len(avail_cats), cols_per_row):
                row_cats = avail_cats[i:i+cols_per_row]
                row_cols = st.columns(cols_per_row)
                for j, (col, label) in enumerate(row_cats):
                    counts = (
                        df[col]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .replace("", np.nan)
                        .dropna()
                        .value_counts()
                        .reset_index()
                    )
                    counts.columns = [label, "count"]
                    if len(counts) <= 6:
                        fig = px.pie(counts, names=label, values="count",
                                     title=label,
                                     color_discrete_sequence=px.colors.qualitative.Set2)
                        fig.update_layout(height=280, margin=dict(t=40,b=10))
                        row_cols[j].plotly_chart(fig, use_container_width=True)
                    else:
                        fig = px.bar(counts.head(10), x="count", y=label,
                                     orientation="h", title=label,
                                     color_discrete_sequence=["#2563eb"])
                        fig.update_layout(height=280, margin=dict(t=40,b=10))
                        row_cols[j].plotly_chart(fig, use_container_width=True)

        # Reviewer type breakdown
        if "is_local_guide" in df.columns:
            st.markdown('<div class="section-header">Reviewer Type</div>',
                        unsafe_allow_html=True)
            guide_counts = df["is_local_guide"].value_counts().reset_index()
            guide_counts.columns = ["is_local_guide","count"]
            guide_counts["type"] = guide_counts["is_local_guide"].map(
                {True:"Local Guide", False:"Regular Reviewer"}
            )
            fig_guide = px.pie(
                guide_counts, names="type", values="count",
                color_discrete_sequence=["#2563eb","#e2e8f0"],
            )
            fig_guide.update_layout(height=260, margin=dict(t=10,b=10))
            st.plotly_chart(fig_guide, use_container_width=True)

    # ── TAB 5: FOOD DEEP DIVE ─────────────────────────────────────────────────
    with tab5:
        food_cols = {
            "score_food":        "🍛 Overall Food",
            "score_authenticity":"🏆 Authenticity",
            "score_spice":       "🌶️ Spice Level",
            "score_cleanliness": "🧼 Cleanliness",
            "score_chicken":     "🍗 Chicken",
            "score_lamb":        "🥩 Lamb/Mutton",
            "score_vegan_dishes":"🌱 Vegan",
            "score_bread_rice":  "🫓 Bread & Rice",
            "score_starters":    "🥙 Starters",
            "score_vegetarian":  "🥗 Veg Options",
        }
        avail_food = {c:l for c,l in food_cols.items()
                      if c in df.columns and df[c].notna().any()}

        if not avail_food:
            st.info("No food-specific NLP scores yet.")
        else:
            food_avgs = df[list(avail_food)].mean().reset_index()
            food_avgs.columns = ["col","score"]
            food_avgs["label"] = food_avgs["col"].map(avail_food)
            food_avgs = food_avgs.dropna().sort_values("score", ascending=False)

            fig_food = px.bar(
                food_avgs, x="label", y="score",
                color="score",
                color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                range_color=[1,5],
                text=food_avgs["score"].round(2),
                title="Food Aspect Scores",
            )
            fig_food.update_traces(textposition="outside")
            fig_food.update_layout(
                yaxis=dict(range=[0,5.5]),
                coloraxis_showscale=False,
                height=380, margin=dict(t=40,b=10),
            )
            st.plotly_chart(fig_food, use_container_width=True)

            # Recommended dishes word frequency
            if "ctx_recommended_dishes" in df.columns:
                st.markdown('<div class="section-header">Most Recommended Dishes</div>',
                            unsafe_allow_html=True)
                all_dishes = (
                    df["ctx_recommended_dishes"]
                    .dropna()
                    .astype(str)
                    .str.split(",")
                    .explode()
                    .str.strip()
                    .str.lower()
                    .replace("", np.nan)
                    .dropna()
                )
                dish_counts = all_dishes.value_counts().head(15).reset_index()
                dish_counts.columns = ["dish","mentions"]
                fig_dishes = px.bar(
                    dish_counts, x="mentions", y="dish",
                    orientation="h",
                    color="mentions",
                    color_continuous_scale=["#dbeafe","#2563eb"],
                )
                fig_dishes.update_layout(
                    height=350, coloraxis_showscale=False,
                    margin=dict(t=10,b=10),
                )
                st.plotly_chart(fig_dishes, use_container_width=True)

            # Per-restaurant food scores
            st.markdown('<div class="section-header">Food Scores per Restaurant</div>',
                        unsafe_allow_html=True)
            food_by_rest = df.groupby("restaurant")[list(avail_food)].mean()
            food_by_rest.columns = [avail_food[c] for c in food_by_rest.columns]
            st.dataframe(food_by_rest.round(2), use_container_width=True)

    st.markdown("---")
    st.caption(
        f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
        "Data: Google Sheets (public) · "
        "Model: nlptown/bert-base-multilingual"
    )

if __name__ == "__main__":
    main()
