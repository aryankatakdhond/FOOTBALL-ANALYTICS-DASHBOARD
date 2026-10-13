"""
Football Player Performance Analytics Dashboard
================================================
Interactive analytics dashboard built with Streamlit + Plotly.

⚠️  DATA DISCLAIMER: All player statistics in this application are
    SYNTHETIC (computer-generated). They do NOT represent real-world
    football results or any actual player's performance.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Constants ──────────────────────────────────────────────────────────────────
ACCENT_GREEN = "#00ff87"
DARK_BG = "#0d1117"
CARD_BG = "#1a2332"
MUTED = "#8b949e"
TEXT = "#e0e0e0"

POSITION_ORDER = ["GK", "DEF", "MID", "FWD"]
POSITION_COLOURS = {
    "GK": "#f0a500",
    "DEF": "#3b82f6",
    "MID": "#00ff87",
    "FWD": "#ef4444",
}

PLOTLY_TEMPLATE = "plotly_dark"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
CUSTOM_CSS = f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {DARK_BG};
        color: {TEXT};
    }}
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {CARD_BG};
        border-right: 1px solid #30363d;
    }}
    section[data-testid="stSidebar"] * {{
        color: {TEXT} !important;
    }}
    /* Metric cards */
    div[data-testid="metric-container"] {{
        background-color: {CARD_BG};
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 20px;
    }}
    div[data-testid="metric-container"] label {{
        color: {MUTED} !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        color: {ACCENT_GREEN} !important;
        font-size: 1.6rem !important;
        font-weight: 700;
    }}
    /* Page title */
    h1 {{
        color: {ACCENT_GREEN};
        font-size: 1.9rem !important;
        font-weight: 800;
        letter-spacing: -0.02em;
    }}
    h2, h3 {{
        color: {TEXT};
    }}
    /* Divider */
    hr {{
        border-color: #30363d;
    }}
    /* DataFrames */
    .stDataFrame {{
        border: 1px solid #30363d;
        border-radius: 8px;
    }}
    /* Disclaimer banner */
    .disclaimer {{
        background-color: #2d1f00;
        border: 1px solid #f0a500;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.80rem;
        color: #f0a500;
        margin-bottom: 12px;
    }}
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {CARD_BG};
        border-radius: 8px 8px 0 0;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {MUTED};
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        color: {ACCENT_GREEN} !important;
        border-bottom: 2px solid {ACCENT_GREEN} !important;
    }}
</style>
"""


# ── Data Loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load football_players.csv with caching. Returns an empty DataFrame on error."""
    try:
        df = pd.read_csv("football_players.csv")
        # Ensure correct dtypes
        int_cols = [
            "player_id", "age", "matches_played", "minutes_played",
            "goals", "assists", "shots", "shots_on_target",
            "key_passes", "tackles", "interceptions", "clean_sheets",
            "yellow_cards", "red_cards",
        ]
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        df["pass_accuracy"] = pd.to_numeric(df["pass_accuracy"], errors="coerce").fillna(0.0)
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
        return df
    except FileNotFoundError:
        st.error(
            "⚠️ **football_players.csv not found.**  "
            "Run `python generate_data.py` first to create the dataset."
        )
        return pd.DataFrame()


# ── Sidebar Filters ────────────────────────────────────────────────────────────
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filter widgets and return the filtered DataFrame."""
    st.sidebar.markdown(
        f"<h2 style='color:{ACCENT_GREEN};font-size:1.1rem;margin-bottom:4px;'>⚽ Filters</h2>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # Season
    all_seasons = sorted(df["season"].unique().tolist())
    selected_seasons = st.sidebar.multiselect(
        "Season", options=all_seasons, default=all_seasons, key="filter_season"
    )

    # Team
    all_teams = sorted(df["team"].unique().tolist())
    selected_teams = st.sidebar.multiselect(
        "Team", options=all_teams, default=all_teams, key="filter_team"
    )

    # Position
    positions_available = [p for p in POSITION_ORDER if p in df["position"].unique()]
    selected_positions = st.sidebar.multiselect(
        "Position", options=positions_available, default=positions_available, key="filter_pos"
    )

    # Player name search
    search_text = st.sidebar.text_input("Search Player Name", value="", key="filter_player")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<p style='color:{MUTED};font-size:0.75rem;'>⚠️ All data is <strong>synthetic</strong>. "
        "Not real-world statistics.</p>",
        unsafe_allow_html=True,
    )

    # Apply filters
    if selected_seasons:
        df = df[df["season"].isin(selected_seasons)]
    if selected_teams:
        df = df[df["team"].isin(selected_teams)]
    if selected_positions:
        df = df[df["position"].isin(selected_positions)]
    if search_text.strip():
        df = df[df["player_name"].str.contains(search_text.strip(), case=False, na=False)]

    return df


# ── Chart Helpers ──────────────────────────────────────────────────────────────
def _chart_layout(fig, title: str = "") -> go.Figure:
    """Apply consistent dark theme layout to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT, size=15, family="sans-serif")),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="sans-serif"),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor=DARK_BG, bordercolor="#30363d", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="#30363d", zerolinecolor="#30363d")
    fig.update_yaxes(gridcolor="#30363d", zerolinecolor="#30363d")
    return fig


def _pos_color_map(positions):
    return {p: POSITION_COLOURS.get(p, ACCENT_GREEN) for p in positions}


# ── Page 1: Overview ──────────────────────────────────────────────────────────
def render_overview(df: pd.DataFrame) -> None:
    st.markdown("## 📊 Overview")
    st.markdown(
        "<div class='disclaimer'>⚠️ All statistics below are <strong>synthetic</strong> "
        "and do not represent real-world football performance.</div>",
        unsafe_allow_html=True,
    )

    # KPI calculations
    total_players = int(df["player_id"].nunique())
    total_goals = int(df["goals"].sum())
    total_assists = int(df["assists"].sum())
    total_minutes = int(df["minutes_played"].sum())
    avg_rating = round(float(df["rating"].mean()), 2)

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Players", f"{total_players:,}")
    c2.metric("⚽ Total Goals", f"{total_goals:,}")
    c3.metric("🎯 Total Assists", f"{total_assists:,}")
    c4.metric("⏱ Minutes Played", f"{total_minutes:,}")
    c5.metric("⭐ Avg Rating", f"{avg_rating:.2f}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        top_goals = (
            df.groupby("player_name", as_index=False)["goals"]
            .sum()
            .nlargest(10, "goals")
        )
        fig_goals = px.bar(
            top_goals,
            x="goals",
            y="player_name",
            orientation="h",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[ACCENT_GREEN],
            labels={"goals": "Goals", "player_name": "Player"},
            hover_data={"goals": True},
        )
        fig_goals.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_goals = _chart_layout(fig_goals, "🏆 Top 10 Players by Goals")
        st.plotly_chart(fig_goals, use_container_width=True)

    with col_right:
        top_assists = (
            df.groupby("player_name", as_index=False)["assists"]
            .sum()
            .nlargest(10, "assists")
        )
        fig_assists = px.bar(
            top_assists,
            x="assists",
            y="player_name",
            orientation="h",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#3b82f6"],
            labels={"assists": "Assists", "player_name": "Player"},
            hover_data={"assists": True},
        )
        fig_assists.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_assists = _chart_layout(fig_assists, "🎯 Top 10 Players by Assists")
        st.plotly_chart(fig_assists, use_container_width=True)

    # Searchable stats table + CSV download
    st.markdown("---")
    st.markdown("### 🔍 Player Statistics Table")
    table_search = st.text_input(
        "Search by player name…", value="", key="table_search"
    )
    display_df = df.copy()
    if table_search.strip():
        display_df = display_df[
            display_df["player_name"].str.contains(table_search.strip(), case=False, na=False)
        ]

    st.markdown(
        f"<p style='color:{MUTED};font-size:0.8rem;'>Showing {len(display_df):,} rows</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        display_df.drop(columns=["player_id"]).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

    # CSV download
    csv_buffer = io.StringIO()
    display_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_buffer.getvalue(),
        file_name="football_players_filtered.csv",
        mime="text/csv",
    )


# ── Page 2: Player Analysis ───────────────────────────────────────────────────
def render_player_analysis(df: pd.DataFrame) -> None:
    st.markdown("## 🧍 Player Analysis")

    # ── Player Comparison ──
    st.markdown("### Compare Players")
    all_players = sorted(df["player_name"].unique().tolist())

    if len(all_players) < 2:
        st.info("ℹ️ At least 2 players are needed for comparison. Adjust your filters.")
    else:
        default_picks = all_players[:4] if len(all_players) >= 4 else all_players[:2]
        selected_players = st.multiselect(
            "Select players to compare (2 or more):",
            options=all_players,
            default=default_picks,
            key="player_compare",
        )
        if len(selected_players) < 2:
            st.info("ℹ️ Select at least 2 players to compare.")
        else:
            compare_cols = [
                "player_name", "team", "position", "season",
                "matches_played", "goals", "assists", "shots",
                "pass_accuracy", "key_passes", "tackles",
                "clean_sheets", "yellow_cards", "red_cards", "rating",
            ]
            compare_df = (
                df[df["player_name"].isin(selected_players)][compare_cols]
                .sort_values(["player_name", "season"])
                .reset_index(drop=True)
            )
            st.dataframe(compare_df, use_container_width=True)

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        # Goals vs Assists scatter
        st.markdown("### Goals vs Assists")
        scatter_df = df.groupby(
            ["player_name", "position", "team"], as_index=False
        ).agg(goals=("goals", "sum"), assists=("assists", "sum"),
              minutes_played=("minutes_played", "sum"))

        fig_ga = px.scatter(
            scatter_df,
            x="goals",
            y="assists",
            color="position",
            color_discrete_map=POSITION_COLOURS,
            size="minutes_played",
            size_max=30,
            hover_data=["player_name", "team", "minutes_played"],
            template=PLOTLY_TEMPLATE,
            labels={"goals": "Goals", "assists": "Assists", "position": "Position"},
        )
        fig_ga = _chart_layout(fig_ga, "⚽ Goals vs Assists (size = minutes played)")
        st.plotly_chart(fig_ga, use_container_width=True)

    with col_right:
        # Shots vs Goals scatter with trendline
        st.markdown("### Shots vs Goals")
        shots_df = df.groupby(
            ["player_name", "team"], as_index=False
        ).agg(goals=("goals", "sum"), shots=("shots", "sum"))

        fig_sg = px.scatter(
            shots_df,
            x="shots",
            y="goals",
            color="team",
            hover_data=["player_name"],
            trendline="ols",
            template=PLOTLY_TEMPLATE,
            labels={"shots": "Shots", "goals": "Goals", "team": "Team"},
        )
        # Style trendline
        for trace in fig_sg.data:
            if trace.mode == "lines":
                trace.line.color = "#ffffff"
                trace.line.width = 1.5
                trace.line.dash = "dash"
        fig_sg = _chart_layout(fig_sg, "🎯 Shots vs Goals (with trendline)")
        st.plotly_chart(fig_sg, use_container_width=True)

    # Rating distribution by position
    st.markdown("---")
    st.markdown("### Rating Distribution by Position")
    fig_rating = px.violin(
        df,
        x="position",
        y="rating",
        color="position",
        color_discrete_map=POSITION_COLOURS,
        box=True,
        points="outliers",
        template=PLOTLY_TEMPLATE,
        category_orders={"position": POSITION_ORDER},
        labels={"position": "Position", "rating": "Rating"},
        hover_data=["player_name"],
    )
    fig_rating = _chart_layout(fig_rating, "⭐ Rating Distribution by Position")
    st.plotly_chart(fig_rating, use_container_width=True)


# ── Page 3: Team Analysis ─────────────────────────────────────────────────────
def render_team_analysis(df: pd.DataFrame) -> None:
    st.markdown("## 🏟 Team Analysis")

    team_agg = (
        df.groupby("team", as_index=False)
        .agg(
            total_goals=("goals", "sum"),
            total_assists=("assists", "sum"),
            total_players=("player_name", "nunique"),
            avg_rating=("rating", "mean"),
            total_minutes=("minutes_played", "sum"),
        )
        .sort_values("total_goals", ascending=False)
    )
    team_agg["avg_rating"] = team_agg["avg_rating"].round(2)

    # ── Grouped bar: Goals & Assists per team ──
    st.markdown("### Goals & Assists per Team")
    melted = team_agg.melt(
        id_vars="team",
        value_vars=["total_goals", "total_assists"],
        var_name="Metric",
        value_name="Count",
    )
    melted["Metric"] = melted["Metric"].map(
        {"total_goals": "Goals", "total_assists": "Assists"}
    )
    fig_ga_team = px.bar(
        melted,
        x="team",
        y="Count",
        color="Metric",
        barmode="group",
        template=PLOTLY_TEMPLATE,
        color_discrete_map={"Goals": ACCENT_GREEN, "Assists": "#3b82f6"},
        labels={"team": "Team", "Count": "Total", "Metric": ""},
    )
    fig_ga_team.update_xaxes(tickangle=-35)
    fig_ga_team = _chart_layout(fig_ga_team, "⚽ Goals & Assists by Team")
    st.plotly_chart(fig_ga_team, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        # Player count per team
        fig_players = px.bar(
            team_agg.sort_values("total_players", ascending=True),
            x="total_players",
            y="team",
            orientation="h",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#7c5cd8"],
            labels={"total_players": "Distinct Players", "team": "Team"},
        )
        fig_players = _chart_layout(fig_players, "👥 Player Count per Team")
        st.plotly_chart(fig_players, use_container_width=True)

    with col_right:
        # Average rating per team
        fig_avg_rating = px.bar(
            team_agg.sort_values("avg_rating", ascending=True),
            x="avg_rating",
            y="team",
            orientation="h",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=[ACCENT_GREEN],
            labels={"avg_rating": "Avg Rating", "team": "Team"},
        )
        fig_avg_rating.update_xaxes(range=[5, 9.5])
        fig_avg_rating = _chart_layout(fig_avg_rating, "⭐ Average Rating per Team")
        st.plotly_chart(fig_avg_rating, use_container_width=True)

    # Summary table
    st.markdown("---")
    st.markdown("### 📋 Team Summary Table")
    display_team = team_agg.rename(columns={
        "team": "Team",
        "total_goals": "Goals",
        "total_assists": "Assists",
        "total_players": "Players",
        "avg_rating": "Avg Rating",
        "total_minutes": "Minutes Played",
    })
    st.dataframe(display_team.reset_index(drop=True), use_container_width=True)


# ── Page 4: Position Analysis ─────────────────────────────────────────────────
def render_position_analysis(df: pd.DataFrame) -> None:
    st.markdown("## 🎽 Position Analysis")

    pos_agg = (
        df.groupby("position", as_index=False)
        .agg(
            avg_goals=("goals", "mean"),
            avg_assists=("assists", "mean"),
            avg_rating=("rating", "mean"),
            avg_pass_accuracy=("pass_accuracy", "mean"),
            avg_tackles=("tackles", "mean"),
            avg_key_passes=("key_passes", "mean"),
            total_yellow=("yellow_cards", "sum"),
            total_red=("red_cards", "sum"),
            player_count=("player_name", "nunique"),
        )
    )
    for col in ["avg_goals", "avg_assists", "avg_rating", "avg_pass_accuracy",
                "avg_tackles", "avg_key_passes"]:
        pos_agg[col] = pos_agg[col].round(2)

    # Reorder rows
    pos_order_available = [p for p in POSITION_ORDER if p in pos_agg["position"].values]
    pos_agg["position"] = pd.Categorical(pos_agg["position"], categories=pos_order_available, ordered=True)
    pos_agg = pos_agg.sort_values("position")

    col_left, col_right = st.columns(2)

    with col_left:
        # Avg stats grouped bar
        melted_stats = pos_agg.melt(
            id_vars="position",
            value_vars=["avg_goals", "avg_assists", "avg_key_passes", "avg_tackles"],
            var_name="Metric",
            value_name="Value",
        )
        melted_stats["Metric"] = melted_stats["Metric"].map({
            "avg_goals": "Avg Goals",
            "avg_assists": "Avg Assists",
            "avg_key_passes": "Avg Key Passes",
            "avg_tackles": "Avg Tackles",
        })
        fig_avg = px.bar(
            melted_stats,
            x="position",
            y="Value",
            color="Metric",
            barmode="group",
            template=PLOTLY_TEMPLATE,
            category_orders={"position": pos_order_available},
            color_discrete_sequence=[ACCENT_GREEN, "#3b82f6", "#f0a500", "#ef4444"],
            labels={"position": "Position", "Value": "Average", "Metric": ""},
        )
        fig_avg = _chart_layout(fig_avg, "📊 Average Stats by Position")
        st.plotly_chart(fig_avg, use_container_width=True)

    with col_right:
        # Pass accuracy by position
        fig_pass = px.bar(
            pos_agg,
            x="position",
            y="avg_pass_accuracy",
            color="position",
            color_discrete_map=POSITION_COLOURS,
            template=PLOTLY_TEMPLATE,
            category_orders={"position": pos_order_available},
            labels={"position": "Position", "avg_pass_accuracy": "Avg Pass Accuracy"},
        )
        fig_pass.update_yaxes(tickformat=".0%")
        fig_pass = _chart_layout(fig_pass, "🎯 Average Pass Accuracy by Position")
        st.plotly_chart(fig_pass, use_container_width=True)

    st.markdown("---")
    col_mid, col_cards = st.columns(2)

    with col_mid:
        # Rating box plot
        fig_box = px.box(
            df,
            x="position",
            y="rating",
            color="position",
            color_discrete_map=POSITION_COLOURS,
            template=PLOTLY_TEMPLATE,
            category_orders={"position": pos_order_available},
            points="outliers",
            hover_data=["player_name"],
            labels={"position": "Position", "rating": "Rating"},
        )
        fig_box = _chart_layout(fig_box, "⭐ Rating Distribution (Box Plot)")
        st.plotly_chart(fig_box, use_container_width=True)

    with col_cards:
        # Card discipline stacked bar
        cards_melted = pos_agg.melt(
            id_vars="position",
            value_vars=["total_yellow", "total_red"],
            var_name="Card",
            value_name="Count",
        )
        cards_melted["Card"] = cards_melted["Card"].map(
            {"total_yellow": "Yellow Cards", "total_red": "Red Cards"}
        )
        fig_cards = px.bar(
            cards_melted,
            x="position",
            y="Count",
            color="Card",
            barmode="stack",
            template=PLOTLY_TEMPLATE,
            category_orders={"position": pos_order_available},
            color_discrete_map={"Yellow Cards": "#f0a500", "Red Cards": "#ef4444"},
            labels={"position": "Position", "Count": "Total Cards", "Card": ""},
        )
        fig_cards = _chart_layout(fig_cards, "🟨🟥 Card Discipline by Position")
        st.plotly_chart(fig_cards, use_container_width=True)

    # Radar chart — avg stats per position
    st.markdown("---")
    st.markdown("### 🕸 Position Radar — Normalised Averages")
    radar_metrics = ["avg_goals", "avg_assists", "avg_rating",
                     "avg_pass_accuracy", "avg_tackles", "avg_key_passes"]
    radar_labels = ["Goals", "Assists", "Rating", "Pass Acc.", "Tackles", "Key Passes"]

    # Normalise 0–1 per metric
    radar_norm = pos_agg[["position"] + radar_metrics].copy()
    for m in radar_metrics:
        col_min = radar_norm[m].min()
        col_max = radar_norm[m].max()
        radar_norm[m] = (
            (radar_norm[m] - col_min) / (col_max - col_min)
            if col_max > col_min else 0.5
        )

    fig_radar = go.Figure()
    for _, row in radar_norm.iterrows():
        pos = row["position"]
        vals = [row[m] for m in radar_metrics]
        vals += vals[:1]  # close the polygon
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_labels + radar_labels[:1],
            fill="toself",
            name=pos,
            line_color=POSITION_COLOURS.get(pos, ACCENT_GREEN),
            opacity=0.6,
        ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#30363d"),
            bgcolor=CARD_BG,
            angularaxis=dict(gridcolor="#30363d"),
        ),
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT),
        legend=dict(bgcolor=DARK_BG, bordercolor="#30363d"),
        margin=dict(l=40, r=40, t=50, b=40),
        title=dict(text="Position Profiles (normalised)", font=dict(color=TEXT, size=15)),
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="⚽ Football Analytics Dashboard",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Load data
    df_raw = load_data()
    if df_raw.empty:
        st.stop()

    # Sidebar branding
    st.sidebar.markdown(
        f"<h1 style='color:{ACCENT_GREEN};font-size:1.3rem;font-weight:800;"
        f"letter-spacing:-0.02em;margin-bottom:0;'>⚽ Football Analytics</h1>"
        f"<p style='color:{MUTED};font-size:0.75rem;margin-top:2px;'>Performance Dashboard</p>",
        unsafe_allow_html=True,
    )

    # Page navigation
    page = st.sidebar.radio(
        "Navigate",
        options=["📊 Overview", "🧍 Player Analysis", "🏟 Team Analysis", "🎽 Position Analysis"],
        key="nav",
    )

    st.sidebar.markdown("---")

    # Apply filters
    df_filtered = apply_filters(df_raw)

    # Guard: empty result
    if df_filtered.empty:
        st.warning(
            "⚠️ No data matches the current filters. "
            "Please adjust your Season, Team, or Position selections."
        )
        st.stop()

    # Route to page
    if page == "📊 Overview":
        render_overview(df_filtered)
    elif page == "🧍 Player Analysis":
        render_player_analysis(df_filtered)
    elif page == "🏟 Team Analysis":
        render_team_analysis(df_filtered)
    elif page == "🎽 Position Analysis":
        render_position_analysis(df_filtered)


if __name__ == "__main__":
    main()
