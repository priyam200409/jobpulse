# ============================================================
# JOBPULSE
# India Data Analyst Job Market Intelligence
# ============================================================

import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.database.database import get_connection


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JobPulse | India Data Analyst Market",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


# ============================================================
# THEME COLORS
# ============================================================

DARK_MODE = st.session_state.dark_mode

if DARK_MODE:

    COLORS = {
        "background": "#0b1220",
        "card": "#111827",
        "card_alt": "#172033",
        "border": "#263244",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "grid": "#334155",
        "primary": "#60a5fa",
        "secondary": "#a78bfa",
        "success": "#34d399",
        "warning": "#fbbf24",
    }

else:

    COLORS = {
        "background": "#f5f7fb",
        "card": "#ffffff",
        "card_alt": "#f8fafc",
        "border": "#dbe3ef",
        "text": "#0f172a",
        "muted": "#475569",
        "grid": "#dbe3ef",
        "primary": "#2563eb",
        "secondary": "#7c3aed",
        "success": "#16a34a",
        "warning": "#d97706",
    }


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ======================================================
       MAIN APPLICATION
       ====================================================== */

    .stApp {{
        background: {COLORS["background"]};
    }}

    /*
       Fix the Streamlit top header.
       The previous version allowed the header to overlap
       the application title.
    */

    header[data-testid="stHeader"] {{
        background: {COLORS["background"]} !important;
        border-bottom: 1px solid {COLORS["border"]};
        height: 52px;
    }}

    /*
       Give the page enough space below the header.
    */

    .block-container {{
        max-width: 1500px;
        padding-top: 4.2rem !important;
        padding-bottom: 3rem !important;
    }}


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {{
        background: #0b1628;
    }}

    section[data-testid="stSidebar"] * {{
        color: #f8fafc !important;
    }}


    /* ======================================================
       NATIVE STREAMLIT METRICS
       ====================================================== */

    div[data-testid="stMetric"] {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 14px;
        padding: 18px;
        min-height: 125px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {COLORS["muted"]} !important;
    }}

    div[data-testid="stMetricLabel"] p {{
        color: {COLORS["muted"]} !important;
        font-size: 12px !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {COLORS["text"]} !important;
    }}

    div[data-testid="stMetricValue"] div {{
        color: {COLORS["text"]} !important;
    }}


    /* ======================================================
       HEADINGS
       ====================================================== */

    h1 {{
        color: {COLORS["text"]} !important;
    }}

    h2 {{
        color: {COLORS["text"]} !important;
    }}

    h3 {{
        color: {COLORS["text"]} !important;
    }}

    h4 {{
        color: {COLORS["text"]} !important;
    }}


    /* ======================================================
       NORMAL STREAMLIT TEXT
       ====================================================== */

    .stMarkdown p {{
        color: {COLORS["text"]};
    }}

    .stCaption {{
        color: {COLORS["muted"]} !important;
    }}

    label {{
        color: {COLORS["text"]} !important;
    }}


    /* ======================================================
       BORDERED CONTAINERS
       ====================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {COLORS["card"]};
        border-color: {COLORS["border"]};
        border-radius: 14px;
    }}


    /* ======================================================
       SELECTBOX / MULTISELECT / TEXT INPUT
       ====================================================== */

    div[data-baseweb="select"] > div {{
        background: {COLORS["card"]};
        border-color: {COLORS["border"]};
    }}

    div[data-baseweb="select"] span {{
        color: {COLORS["text"]} !important;
    }}

    div[data-baseweb="input"] {{
        background: {COLORS["card"]};
    }}

    div[data-baseweb="input"] input {{
        color: {COLORS["text"]} !important;
    }}


    /* ======================================================
       DATAFRAME
       ====================================================== */

    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLORS["border"]};
        border-radius: 12px;
    }}


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton button {{
        border-radius: 9px;
        border: 1px solid {COLORS["border"]};
    }}


    /* ======================================================
       REMOVE STREAMLIT FOOTER
       ====================================================== */

    footer {{
        visibility: hidden;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE QUERY
# ============================================================

def query_dataframe(query: str) -> pd.DataFrame:

    connection = get_connection()

    try:

        return pd.read_sql_query(
            query,
            connection,
        )

    finally:

        connection.close()
@st.cache_data
def load_historical_job_trends():
    """Load weekly and monthly job trends from historical snapshots."""
    from src.analytics.trends import (
        get_weekly_job_trends,
        get_monthly_job_trends,
    )

    weekly = get_weekly_job_trends()
    monthly = get_monthly_job_trends()

    return weekly, monthly


@st.cache_data
def load_historical_skill_trends():
    """Load historical skill demand from snapshot data."""
    from src.analytics.trends import get_skill_trends

    return get_skill_trends()


@st.cache_data
def load_skill_growth():
    """Load skill growth between the latest two snapshots."""
    from src.analytics.skill_trends import (
        get_growing_skills,
        get_declining_skills,
    )

    growing = get_growing_skills()
    declining = get_declining_skills()

    return growing, declining


# ============================================================
# DATA LOADERS
# ============================================================

@st.cache_data
def load_postings():

    return query_dataframe(
        """
        SELECT
            posting_id,
            job_title,
            company,
            location,
            experience,
            description,
            requirements,
            posted_date,
            source,
            job_url,
            scraped_at
        FROM postings
        ORDER BY posted_date DESC
        """
    )


@st.cache_data
def load_skill_frequency():

    return query_dataframe(
        """
        SELECT
            s.skill_name,
            s.category,
            COUNT(DISTINCT sm.posting_id) AS job_count
        FROM skill_mentions sm
        JOIN skills s
            ON sm.skill_id = s.skill_id
        GROUP BY
            s.skill_id,
            s.skill_name,
            s.category
        ORDER BY
            job_count DESC,
            s.skill_name
        """
    )


@st.cache_data
def load_city_volume():

    return query_dataframe(
        """
        SELECT
            location,
            COUNT(*) AS job_count
        FROM postings
        GROUP BY location
        ORDER BY job_count DESC
        """
    )


@st.cache_data
def load_city_skill():

    return query_dataframe(
        """
        SELECT
            p.location,
            s.skill_name,
            s.category,
            COUNT(DISTINCT p.posting_id) AS job_count
        FROM postings p
        JOIN skill_mentions sm
            ON p.posting_id = sm.posting_id
        JOIN skills s
            ON sm.skill_id = s.skill_id
        GROUP BY
            p.location,
            s.skill_id,
            s.skill_name,
            s.category
        ORDER BY
            p.location,
            job_count DESC
        """
    )


@st.cache_data
def load_experience():

    return query_dataframe(
        """
        SELECT
            experience,
            COUNT(*) AS job_count
        FROM postings
        WHERE
            experience IS NOT NULL
            AND TRIM(experience) <> ''
        GROUP BY experience
        ORDER BY job_count DESC
        """
    )


@st.cache_data
def load_cooccurrence():

    return query_dataframe(
        """
        SELECT
            s1.skill_name AS skill_1,
            s2.skill_name AS skill_2,
            COUNT(DISTINCT sm1.posting_id) AS job_count
        FROM skill_mentions sm1
        JOIN skill_mentions sm2
            ON sm1.posting_id = sm2.posting_id
            AND sm1.skill_id < sm2.skill_id
        JOIN skills s1
            ON sm1.skill_id = s1.skill_id
        JOIN skills s2
            ON sm2.skill_id = s2.skill_id
        GROUP BY
            s1.skill_id,
            s2.skill_id,
            s1.skill_name,
            s2.skill_name
        ORDER BY
            job_count DESC,
            skill_1,
            skill_2
        """
    )


# ============================================================
# LOAD DATA
# ============================================================

postings = load_postings()
skill_frequency = load_skill_frequency()
city_volume = load_city_volume()
city_skill = load_city_skill()
experience = load_experience()
cooccurrence = load_cooccurrence()


# ============================================================
# VALIDATE DATABASE
# ============================================================

if postings.empty:

    st.error(
        "JobPulse database does not contain any job postings."
    )

    st.stop()


# ============================================================
# DERIVED KPIs
# ============================================================

TOTAL_JOBS = len(postings)

TOTAL_COMPANIES = postings["company"].nunique()

TOTAL_CITIES = postings["location"].nunique()

TOTAL_SKILLS = skill_frequency["skill_name"].nunique()

TOP_SKILL = (
    skill_frequency.iloc[0]["skill_name"]
    if not skill_frequency.empty
    else "N/A"
)

TOP_SKILL_JOBS = (
    int(skill_frequency.iloc[0]["job_count"])
    if not skill_frequency.empty
    else 0
)

TOP_SKILL_PERCENT = (
    TOP_SKILL_JOBS / TOTAL_JOBS * 100
    if TOTAL_JOBS
    else 0
)

TOP_CITY = (
    city_volume.iloc[0]["location"]
    if not city_volume.empty
    else "N/A"
)

TOP_CITY_JOBS = (
    int(city_volume.iloc[0]["job_count"])
    if not city_volume.empty
    else 0
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 JobPulse")

    st.caption(
        "India Data Analyst Job Market Intelligence"
    )

    st.divider()

    st.markdown("### Explore")

    page = st.radio(
        "Dashboard pages",
        [
            "Market Overview",
            "Skill Intelligence",
            "Skill Relationships",
            "Geography",
            "Trends",
            "Skill Gap Analyzer",
            "Job Explorer",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### Dataset")

    st.caption(f"Jobs: {TOTAL_JOBS:,}")

    st.caption(f"Companies: {TOTAL_COMPANIES:,}")

    st.caption(f"Cities: {TOTAL_CITIES:,}")

    st.caption(f"Skills detected: {TOTAL_SKILLS:,}")

    st.divider()

    st.markdown("### Appearance")

    new_dark_mode = st.toggle(
        "Dark mode",
        value=st.session_state.dark_mode,
    )

    if new_dark_mode != st.session_state.dark_mode:

        st.session_state.dark_mode = new_dark_mode

        st.rerun()

    st.divider()

    if st.button(
        "🔄 Refresh dashboard data",
        width="stretch",
    ):

        st.cache_data.clear()

        st.rerun()

    st.divider()

    st.caption("JobPulse v1.0")

    st.caption("Development dataset")


# ============================================================
# PLOTLY THEME HELPER
# ============================================================

def apply_plot_theme(fig, height=430):

    fig.update_layout(
        height=height,
        margin=dict(
            l=20,
            r=35,
            t=30,
            b=50,
        ),
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(
            color=COLORS["text"],
            family="Arial",
        ),
        legend=dict(
            font=dict(
                color=COLORS["text"],
            )
        ),
    )

    fig.update_xaxes(
        color=COLORS["text"],
        title_font=dict(
            color=COLORS["text"]
        ),
        tickfont=dict(
            color=COLORS["text"]
        ),
        gridcolor=COLORS["grid"],
        linecolor=COLORS["border"],
    )

    fig.update_yaxes(
        color=COLORS["text"],
        title_font=dict(
            color=COLORS["text"]
        ),
        tickfont=dict(
            color=COLORS["text"]
        ),
        gridcolor=COLORS["grid"],
        linecolor=COLORS["border"],
    )

    return fig


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "India Data Analyst Job Market"
)

st.caption(
    "JobPulse analyzes job postings to identify skill demand, "
    "hiring geography, experience requirements, skill relationships "
    "and career opportunities."
)


# ============================================================
# MARKET OVERVIEW
# ============================================================

if page == "Market Overview":

    st.header("Market Overview")

    st.caption(
        "Executive snapshot of the current JobPulse dataset."
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "TOTAL JOBS",
            f"{TOTAL_JOBS:,}",
        )

    with c2:

        st.metric(
            "COMPANIES",
            f"{TOTAL_COMPANIES:,}",
        )

    with c3:

        st.metric(
            "CITIES",
            f"{TOTAL_CITIES:,}",
        )

    with c4:

        st.metric(
            "SKILLS DETECTED",
            f"{TOTAL_SKILLS:,}",
        )

    st.write("")

    # --------------------------------------------------------
    # INSIGHT
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "💡 Current Dataset Insight"
        )

        st.write(
            f"**{TOP_SKILL}** is the most frequently detected "
            f"skill in the current dataset, appearing in "
            f"**{TOP_SKILL_JOBS} of {TOTAL_JOBS} jobs "
            f"({TOP_SKILL_PERCENT:.0f}%)**."
        )

        st.caption(
            "Note: these figures currently represent the development "
            "dataset, not the full India job market."
        )

    st.write("")

    # --------------------------------------------------------
    # SKILLS + CITIES
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.subheader("🔥 Skill Demand")

        st.caption(
            "Percentage of analyzed jobs mentioning each skill."
        )

        skill_chart = skill_frequency.copy()

        skill_chart["demand_percentage"] = (
            skill_chart["job_count"]
            / TOTAL_JOBS
            * 100
        )

        skill_chart = (
            skill_chart
            .head(10)
            .sort_values(
                "demand_percentage",
                ascending=True,
            )
        )

        fig = px.bar(
            skill_chart,
            x="demand_percentage",
            y="skill_name",
            orientation="h",
            text="demand_percentage",
        )

        fig.update_traces(
            marker_color=COLORS["primary"],
            texttemplate="%{text:.0f}%",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Demand: %{x:.0f}%"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            xaxis=dict(
                title="Share of Jobs",
                range=[0, 110],
                ticksuffix="%",
            ),
            yaxis=dict(
                title="",
            ),
            showlegend=False,
        )

        apply_plot_theme(fig, 470)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    with right:

        st.subheader("📍 Hiring by City")

        st.caption(
            "Number of analyzed postings by location."
        )

        city_chart = city_volume.sort_values(
            "job_count",
            ascending=True,
        )

        fig = px.bar(
            city_chart,
            x="job_count",
            y="location",
            orientation="h",
            text="job_count",
        )

        fig.update_traces(
            marker_color=COLORS["secondary"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Jobs: %{x}"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            xaxis=dict(
                title="Number of Jobs",
            ),
            yaxis=dict(
                title="",
            ),
            showlegend=False,
        )

        apply_plot_theme(fig, 470)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    st.subheader("🎓 Experience Demand")

    st.caption(
        "Experience ranges represented in the current dataset."
    )

    if not experience.empty:

        fig = px.bar(
            experience,
            x="experience",
            y="job_count",
            text="job_count",
        )

        fig.update_traces(
            marker_color=COLORS["primary"],
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis_title="Experience Range",
            yaxis_title="Jobs",
            showlegend=False,
        )

        apply_plot_theme(fig, 360)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )


# ============================================================
# SKILL INTELLIGENCE
# ============================================================

elif page == "Skill Intelligence":

    st.header("🧠 Skill Intelligence")

    st.caption(
        "Explore demand by individual skill and skill category."
    )

    categories = sorted(
        skill_frequency[
            "category"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    f1, f2 = st.columns([2, 1])

    with f1:

        category = st.selectbox(
            "Skill category",
            ["All Categories"] + categories,
        )

    with f2:

        maximum = min(
            20,
            max(5, len(skill_frequency)),
        )

        top_n = st.slider(
            "Skills to display",
            min_value=5,
            max_value=maximum,
            value=min(10, maximum),
        )

    if category == "All Categories":

        filtered = skill_frequency.copy()

    else:

        filtered = skill_frequency[
            skill_frequency["category"] == category
        ].copy()

    filtered["demand_percentage"] = (
        filtered["job_count"]
        / TOTAL_JOBS
        * 100
    )

    filtered = (
        filtered
        .sort_values(
            "job_count",
            ascending=False,
        )
        .head(top_n)
    )

    # --------------------------------------------------------
    # SUMMARY KPIs
    # --------------------------------------------------------

    s1, s2, s3 = st.columns(3)

    with s1:

        st.metric(
            "TOP SKILL",
            (
                filtered.iloc[0]["skill_name"]
                if not filtered.empty
                else "N/A"
            ),
        )

    with s2:

        st.metric(
            "SKILLS SHOWN",
            len(filtered),
        )

    with s3:

        average_demand = (
            filtered["demand_percentage"].mean()
            if not filtered.empty
            else 0
        )

        st.metric(
            "AVERAGE DEMAND",
            f"{average_demand:.1f}%",
        )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    if not filtered.empty:

        plot_data = filtered.sort_values(
            "demand_percentage",
            ascending=True,
        )

        fig = px.bar(
            plot_data,
            x="demand_percentage",
            y="skill_name",
            orientation="h",
            color="category",
            text="demand_percentage",
        )

        fig.update_traces(
            texttemplate="%{text:.0f}%",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis=dict(
                title="Share of Jobs",
                range=[0, 110],
                ticksuffix="%",
            ),
            yaxis=dict(
                title="",
            ),
            legend_title="Category",
        )

        apply_plot_theme(fig, 560)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

        table = filtered[
            [
                "skill_name",
                "category",
                "job_count",
                "demand_percentage",
            ]
        ].copy()

        table.columns = [
            "Skill",
            "Category",
            "Jobs",
            "Demand %",
        ]

        table["Demand %"] = table[
            "Demand %"
        ].round(1)

        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
        )


# ============================================================
# SKILL RELATIONSHIPS
# ============================================================

elif page == "Skill Relationships":

    st.header("🔗 Skill Relationships")

    st.caption(
        "Identify skills that frequently occur together in the same "
        "job postings."
    )

    if cooccurrence.empty:

        st.info(
            "No skill relationships are available yet."
        )

    else:

        relationships = cooccurrence.copy()

        relationships["pair"] = (
            relationships["skill_1"]
            + " + "
            + relationships["skill_2"]
        )

        top_relationships = relationships.head(15)

        # ----------------------------------------------------
        # TOP COMBINATIONS
        # ----------------------------------------------------

        st.subheader(
            "Most Common Skill Combinations"
        )

        pair_plot = top_relationships.sort_values(
            "job_count",
            ascending=True,
        )

        fig = px.bar(
            pair_plot,
            x="job_count",
            y="pair",
            orientation="h",
            text="job_count",
        )

        fig.update_traces(
            marker_color=COLORS["primary"],
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis_title="Jobs Containing Both Skills",
            yaxis_title="",
            showlegend=False,
        )

        apply_plot_theme(fig, 560)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        st.subheader(
            "Relationship Table"
        )

        pair_table = top_relationships[
            [
                "skill_1",
                "skill_2",
                "job_count",
            ]
        ].copy()

        pair_table.columns = [
            "Skill 1",
            "Skill 2",
            "Jobs Together",
        ]

        st.dataframe(
            pair_table,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # HEATMAP
        # ----------------------------------------------------

        st.subheader(
            "Skill Co-occurrence Matrix"
        )

        matrix_skills = sorted(
            set(
                top_relationships["skill_1"]
            )
            |
            set(
                top_relationships["skill_2"]
            )
        )

        matrix = pd.DataFrame(
            0,
            index=matrix_skills,
            columns=matrix_skills,
        )

        for _, row in top_relationships.iterrows():

            skill_1 = row["skill_1"]
            skill_2 = row["skill_2"]

            value = int(
                row["job_count"]
            )

            matrix.loc[
                skill_1,
                skill_2,
            ] = value

            matrix.loc[
                skill_2,
                skill_1,
            ] = value

        fig = go.Figure(
            data=[
                go.Heatmap(
                    z=matrix.values,
                    x=matrix.columns,
                    y=matrix.index,
                    text=matrix.values,
                    texttemplate="%{text}",
                    colorscale="Blues",
                    hovertemplate=(
                        "<b>%{y}</b> + "
                        "<b>%{x}</b><br>"
                        "Jobs: %{z}"
                        "<extra></extra>"
                    ),
                )
            ]
        )

        fig.update_layout(
            height=620,
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=80,
            ),
            paper_bgcolor=COLORS["card"],
            plot_bgcolor=COLORS["card"],
            font=dict(
                color=COLORS["text"],
            ),
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(
                    color=COLORS["text"]
                ),
            ),
            yaxis=dict(
                tickfont=dict(
                    color=COLORS["text"]
                ),
            ),
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )


# ============================================================
# GEOGRAPHY
# ============================================================

elif page == "Geography":

    st.header("📍 Geography")

    st.caption(
        "Understand where Data Analyst opportunities are concentrated."
    )

    selected_city = st.selectbox(
        "Select a city",
        city_volume[
            "location"
        ].tolist(),
    )

    city_jobs = int(
        city_volume.loc[
            city_volume["location"] == selected_city,
            "job_count",
        ].iloc[0]
    )

    selected_city_skills = city_skill[
        city_skill["location"] == selected_city
    ].copy()

    selected_city_skills[
        "demand_percentage"
    ] = (
        selected_city_skills["job_count"]
        / city_jobs
        * 100
    )

    # --------------------------------------------------------
    # CITY KPIs
    # --------------------------------------------------------

    g1, g2, g3 = st.columns(3)

    with g1:

        st.metric(
            "CITY JOBS",
            city_jobs,
        )

    with g2:

        st.metric(
            "SKILLS DETECTED",
            selected_city_skills[
                "skill_name"
            ].nunique(),
        )

    with g3:

        st.metric(
            "TOP CITY SKILL",
            (
                selected_city_skills.iloc[0]["skill_name"]
                if not selected_city_skills.empty
                else "N/A"
            ),
        )

    st.write("")

    left, right = st.columns(2)

    # --------------------------------------------------------
    # CITY VOLUME
    # --------------------------------------------------------

    with left:

        st.subheader(
            "Hiring Volume by City"
        )

        city_plot = city_volume.sort_values(
            "job_count",
            ascending=True,
        )

        fig = px.bar(
            city_plot,
            x="job_count",
            y="location",
            orientation="h",
            text="job_count",
        )

        fig.update_traces(
            marker_color=COLORS["primary"],
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis_title="Jobs",
            yaxis_title="",
            showlegend=False,
        )

        apply_plot_theme(fig, 500)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    # --------------------------------------------------------
    # CITY SKILLS
    # --------------------------------------------------------

    with right:

        st.subheader(
            f"Skills in {selected_city}"
        )

        city_plot = (
            selected_city_skills
            .head(10)
            .sort_values(
                "demand_percentage",
                ascending=True,
            )
        )

        fig = px.bar(
            city_plot,
            x="demand_percentage",
            y="skill_name",
            orientation="h",
            text="demand_percentage",
        )

        fig.update_traces(
            marker_color=COLORS["secondary"],
            texttemplate="%{text:.0f}%",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis=dict(
                title="Share of City Jobs",
                range=[0, 110],
                ticksuffix="%",
            ),
            yaxis=dict(
                title="",
            ),
            showlegend=False,
        )

        apply_plot_theme(fig, 500)

        st.plotly_chart(
            fig,
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    # --------------------------------------------------------
    # CITY TABLE
    # --------------------------------------------------------

    st.subheader(
        f"Skill Breakdown — {selected_city}"
    )

    city_table = selected_city_skills[
        [
            "skill_name",
            "category",
            "job_count",
            "demand_percentage",
        ]
    ].copy()

    city_table.columns = [
        "Skill",
        "Category",
        "Jobs",
        "Demand %",
    ]

    city_table["Demand %"] = (
        city_table["Demand %"]
        .round(1)
    )

    st.dataframe(
        city_table,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# TRENDS
# ============================================================

elif page == "Trends":

    st.header("📈 Market Trends")

    st.caption(
        "Track job-market changes using historical JobPulse snapshots."
    )

    weekly_trends, monthly_trends = load_historical_job_trends()

    # --------------------------------------------------------
    # HISTORICAL SNAPSHOT STATUS
    # --------------------------------------------------------

    snapshot_dates = set()

    if not weekly_trends.empty:
        snapshot_dates.update(
            weekly_trends["snapshot_date"]
            .dropna()
            .astype(str)
            .tolist()
        )

    if not monthly_trends.empty:
        snapshot_dates.update(
            monthly_trends["snapshot_date"]
            .dropna()
            .astype(str)
            .tolist()
        )

    snapshot_count = len(snapshot_dates)

    if snapshot_count < 2:

        with st.container(border=True):

            st.subheader("ℹ️ Historical Data Required")

            if snapshot_count == 1:
                st.write(
                    "JobPulse currently has 1 historical snapshot."
                )
            else:
                st.write(
                    "JobPulse currently has no historical snapshots."
                )

            st.write(
                "Weekly and monthly growth calculations require "
                "at least two snapshots from different collection periods."
            )

            st.info(
                "No historical growth rate is being estimated "
                "or fabricated. Growth calculations will appear "
                "automatically as additional snapshots are collected."
            )

    else:

        latest_week = weekly_trends.iloc[-1]

        t1, t2, t3 = st.columns(3)

        with t1:
            st.metric(
                "SNAPSHOTS",
                snapshot_count,
            )

        with t2:
            st.metric(
                "LATEST WEEK",
                str(latest_week["week"]),
            )

        with t3:
            st.metric(
                "LATEST JOB VOLUME",
                int(latest_week["job_count"]),
            )

        st.write("")

    # --------------------------------------------------------
    # WEEKLY JOB VOLUME
    # --------------------------------------------------------

    st.subheader("Weekly Job Volume")

    if weekly_trends.empty:

        st.warning(
            "No historical weekly data is available yet."
        )

    else:

        weekly_chart = weekly_trends.copy()

        fig = px.line(
            weekly_chart,
            x="week",
            y="job_count",
            markers=True,
        )

        fig.update_traces(
            line=dict(
                color=COLORS["primary"],
                width=3,
            ),
            marker=dict(
                size=8,
            ),
            hovertemplate=(
                "<b>Week:</b> %{x}<br>"
                "<b>Jobs:</b> %{y}"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            xaxis_title="Week",
            yaxis_title="Jobs",
        )

        apply_plot_theme(fig, 390)

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displaylogo": False},
        )

    # --------------------------------------------------------
    # MONTHLY JOB VOLUME
    # --------------------------------------------------------

    st.subheader("Monthly Job Volume")

    if monthly_trends.empty:

        st.warning(
            "No historical monthly data is available yet."
        )

    else:

        monthly_chart = monthly_trends.copy()

        fig = px.bar(
            monthly_chart,
            x="month",
            y="job_count",
            text="job_count",
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Jobs",
        )

        apply_plot_theme(fig, 390)

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displaylogo": False},
        )

    # --------------------------------------------------------
    # MONTH-OVER-MONTH CHANGE
    # --------------------------------------------------------

    if snapshot_count >= 2 and not monthly_trends.empty:

        st.subheader("Month-over-Month Change")

        growth_table = monthly_trends[
            [
                "month",
                "job_count",
                "previous_month_jobs",
                "mom_change_percentage",
            ]
        ].copy()

        growth_table.columns = [
            "Month",
            "Jobs",
            "Previous Month Jobs",
            "MoM Change %",
        ]

        growth_table["MoM Change %"] = pd.to_numeric(
            growth_table["MoM Change %"],
            errors="coerce",
        ).round(1)

        st.dataframe(
            growth_table,
            width="stretch",
            hide_index=True,
        )

    # --------------------------------------------------------
    # HISTORICAL SKILL DEMAND
    # --------------------------------------------------------

    st.subheader("Historical Skill Demand")

    historical_skill_trends = (
        load_historical_skill_trends()
    )

    if historical_skill_trends.empty:

        st.info(
            "Historical skill demand will become available "
            "as additional snapshots are collected."
        )

    else:

        latest_skill_date = (
            historical_skill_trends[
                "snapshot_date"
            ].max()
        )

        latest_skill_demand = (
            historical_skill_trends[
                historical_skill_trends[
                    "snapshot_date"
                ] == latest_skill_date
            ]
            .sort_values(
                "job_count",
                ascending=False,
            )
            .head(15)
        )

        skill_chart = latest_skill_demand.sort_values(
            "job_count",
            ascending=True,
        )

        fig = px.bar(
            skill_chart,
            x="job_count",
            y="skill",
            orientation="h",
            text="job_count",
        )

        fig.update_traces(
            marker_color=COLORS["secondary"],
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            xaxis_title="Jobs",
            yaxis_title="",
        )

        apply_plot_theme(fig, 520)

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displaylogo": False},
        )

        st.caption(
            f"Skill demand from the latest historical snapshot: "
            f"{latest_skill_date}"
        )

    # --------------------------------------------------------
    # SKILL GROWTH
    # --------------------------------------------------------

    if snapshot_count >= 2:

        growing_skills, declining_skills = (
            load_skill_growth()
        )

        st.subheader("Skill Growth")

        left, right = st.columns(2)

        with left:

            st.markdown("**Growing Skills**")

            if growing_skills.empty:

                st.info(
                    "No growing skills detected."
                )

            else:

                growing_table = (
                    growing_skills.head(10).copy()
                )

                growing_table.columns = [
                    "Skill",
                    "Current Jobs",
                    "Previous Jobs",
                    "Job Change",
                    "Growth %",
                ]

                growing_table["Growth %"] = pd.to_numeric(
                    growing_table["Growth %"],
                    errors="coerce",
                ).round(1)

                st.dataframe(
                    growing_table,
                    width="stretch",
                    hide_index=True,
                )

        with right:

            st.markdown("**Declining Skills**")

            if declining_skills.empty:

                st.info(
                    "No declining skills detected."
                )

            else:

                declining_table = (
                    declining_skills.head(10).copy()
                )

                declining_table.columns = [
                    "Skill",
                    "Current Jobs",
                    "Previous Jobs",
                    "Job Change",
                    "Growth %",
                ]

                declining_table["Growth %"] = pd.to_numeric(
                    declining_table["Growth %"],
                    errors="coerce",
                ).round(1)

                st.dataframe(
                    declining_table,
                    width="stretch",
                    hide_index=True,
                )


# SKILL GAP ANALYZER
# ============================================================

elif page == "Skill Gap Analyzer":

    st.header("🎯 Skill Gap Analyzer")

    st.caption(
        "Compare your current skills with the skills demanded "
        "in the JobPulse dataset."
    )

    detected_skills = sorted(
        skill_frequency[
            "skill_name"
        ]
        .unique()
        .tolist()
    )

    user_skills = st.multiselect(
        "Select the skills you already have",
        detected_skills,
        placeholder="Choose your current skills...",
    )

    if not user_skills:

        with st.container(border=True):

            st.subheader(
                "Start your analysis"
            )

            st.write(
                "Select your current skills above. "
                "JobPulse will identify high-demand skills "
                "you may want to add."
            )

    else:

        owned = skill_frequency[
            skill_frequency[
                "skill_name"
            ].isin(
                user_skills
            )
        ].copy()

        gap = skill_frequency[
            ~skill_frequency[
                "skill_name"
            ].isin(
                user_skills
            )
        ].copy()

        total_mentions = (
            skill_frequency[
                "job_count"
            ].sum()
        )

        owned_mentions = (
            owned[
                "job_count"
            ].sum()
        )

        coverage = (
            owned_mentions
            / total_mentions
            * 100
            if total_mentions
            else 0
        )

        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        a1, a2, a3 = st.columns(3)

        with a1:

            st.metric(
                "YOUR SKILLS",
                len(user_skills),
            )

        with a2:

            st.metric(
                "POTENTIAL GAPS",
                len(gap),
            )

        with a3:

            st.metric(
                "DEMAND COVERAGE",
                f"{coverage:.0f}%",
            )

        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        st.subheader(
            "Recommended Skills to Consider"
        )

        st.caption(
            "Prioritized by the number of postings mentioning "
            "each skill."
        )

        recommendations = gap.head(10).copy()

        recommendations[
            "demand_percentage"
        ] = (
            recommendations[
                "job_count"
            ]
            / TOTAL_JOBS
            * 100
        )

        if recommendations.empty:

            st.success(
                "You have selected every skill detected "
                "in the current dataset."
            )

        else:

            rec_plot = recommendations.sort_values(
                "job_count",
                ascending=True,
            )

            fig = px.bar(
                rec_plot,
                x="demand_percentage",
                y="skill_name",
                orientation="h",
                color="category",
                text="demand_percentage",
            )

            fig.update_traces(
                texttemplate="%{text:.0f}%",
                textposition="outside",
                cliponaxis=False,
            )

            fig.update_layout(
                xaxis=dict(
                    title="Share of Jobs",
                    range=[0, 110],
                    ticksuffix="%",
                ),
                yaxis=dict(
                    title="",
                ),
                legend_title="Category",
            )

            apply_plot_theme(fig, 520)

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displaylogo": False,
                },
            )

            recommendation_table = recommendations[
                [
                    "skill_name",
                    "category",
                    "job_count",
                    "demand_percentage",
                ]
            ].copy()

            recommendation_table.columns = [
                "Recommended Skill",
                "Category",
                "Jobs",
                "Demand %",
            ]

            recommendation_table[
                "Demand %"
            ] = (
                recommendation_table[
                    "Demand %"
                ].round(1)
            )

            st.dataframe(
                recommendation_table,
                width="stretch",
                hide_index=True,
            )

        # ----------------------------------------------------
        # OWNED SKILLS
        # ----------------------------------------------------

        if not owned.empty:

            st.subheader(
                "Your Selected Skills"
            )

            owned_table = owned[
                [
                    "skill_name",
                    "category",
                    "job_count",
                ]
            ].copy()

            owned_table[
                "demand_percentage"
            ] = (
                owned_table[
                    "job_count"
                ]
                / TOTAL_JOBS
                * 100
            )

            owned_table.columns = [
                "Skill",
                "Category",
                "Jobs",
                "Demand %",
            ]

            owned_table[
                "Demand %"
            ] = (
                owned_table[
                    "Demand %"
                ].round(1)
            )

            st.dataframe(
                owned_table,
                width="stretch",
                hide_index=True,
            )


# ============================================================
# JOB EXPLORER
# ============================================================

elif page == "Job Explorer":

    st.header("🔎 Job Explorer")

    st.caption(
        "Search and filter the underlying job postings."
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    f1, f2, f3 = st.columns(3)

    with f1:

        locations = [
            "All Cities"
        ] + sorted(
            postings[
                "location"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        selected_location = st.selectbox(
            "Location",
            locations,
        )

    with f2:

        companies = [
            "All Companies"
        ] + sorted(
            postings[
                "company"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        selected_company = st.selectbox(
            "Company",
            companies,
        )

    with f3:

        search_text = st.text_input(
            "Search job title",
            placeholder="e.g. Data Analyst",
        )

    # --------------------------------------------------------
    # FILTER DATA
    # --------------------------------------------------------

    filtered_jobs = postings.copy()

    if selected_location != "All Cities":

        filtered_jobs = filtered_jobs[
            filtered_jobs[
                "location"
            ]
            ==
            selected_location
        ]

    if selected_company != "All Companies":

        filtered_jobs = filtered_jobs[
            filtered_jobs[
                "company"
            ]
            ==
            selected_company
        ]

    if search_text.strip():

        mask = filtered_jobs[
            "job_title"
        ].str.contains(
            search_text,
            case=False,
            na=False,
        )

        filtered_jobs = filtered_jobs[
            mask
        ]

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.metric(
        "MATCHING JOBS",
        len(filtered_jobs),
    )

    if filtered_jobs.empty:

        st.warning(
            "No jobs match the selected filters."
        )

    else:

        result_table = filtered_jobs[
            [
                "job_title",
                "company",
                "location",
                "experience",
                "posted_date",
                "source",
            ]
        ].copy()

        result_table.columns = [
            "Job Title",
            "Company",
            "Location",
            "Experience",
            "Posted Date",
            "Source",
        ]

        st.dataframe(
            result_table,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # JOB DETAILS
        # ----------------------------------------------------

        st.subheader(
            "Job Details"
        )

        selected_index = st.selectbox(
            "Select a posting",
            filtered_jobs.index.tolist(),
            format_func=lambda index: (
                f'{filtered_jobs.loc[index, "job_title"]} — '
                f'{filtered_jobs.loc[index, "company"]}'
            ),
        )

        selected_job = filtered_jobs.loc[
            selected_index
        ]

        with st.container(border=True):

            st.subheader(
                selected_job["job_title"]
            )

            d1, d2 = st.columns(2)

            with d1:

                st.write(
                    f'**Company:** '
                    f'{selected_job["company"]}'
                )

                st.write(
                    f'**Location:** '
                    f'{selected_job["location"]}'
                )

                st.write(
                    f'**Experience:** '
                    f'{selected_job["experience"]}'
                )

            with d2:

                st.write(
                    f'**Source:** '
                    f'{selected_job["source"]}'
                )

                st.write(
                    f'**Posted:** '
                    f'{selected_job["posted_date"]}'
                )

            if selected_job["job_url"]:

                st.link_button(
                    "Open Job Posting",
                    selected_job["job_url"],
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "JobPulse · India Data Analyst Job Market Intelligence"
)

st.caption(
    "Python · Pandas · SQL · SQLite · Plotly · Streamlit"
)
