import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash import dcc, html, Input, Output, State


# =========================
# Load Data
# =========================
density_map_data = pd.read_csv("DensityMapDataV3.csv")
top_ai_skills_data = pd.read_csv("TopAISkillsChartData_CareerArea.csv")
top_ai_career_data = pd.read_csv("TopAICareerDataV2_with_other.csv")   # for share
career_intensity_data = pd.read_csv("CareerAreaIntensity.csv")         # for intensity

state_abbrev = {
    "Alabama": "AL","Alaska": "AK","Arizona": "AZ","Arkansas": "AR","California": "CA",
    "Colorado": "CO","Connecticut": "CT","Delaware": "DE","Florida": "FL","Georgia": "GA",
    "Hawaii": "HI","Idaho": "ID","Illinois": "IL","Indiana": "IN","Iowa": "IA",
    "Kansas": "KS","Kentucky": "KY","Louisiana": "LA","Maine": "ME","Maryland": "MD",
    "Massachusetts": "MA","Michigan": "MI","Minnesota": "MN","Mississippi": "MS",
    "Missouri": "MO","Montana": "MT","Nebraska": "NE","Nevada": "NV","New Hampshire": "NH",
    "New Jersey": "NJ","New Mexico": "NM","New York": "NY","North Carolina": "NC",
    "North Dakota": "ND","Ohio": "OH","Oklahoma": "OK","Oregon": "OR","Pennsylvania": "PA",
    "Rhode Island": "RI","South Carolina": "SC","South Dakota": "SD","Tennessee": "TN",
    "Texas": "TX","Utah": "UT","Vermont": "VT","Virginia": "VA","Washington": "WA",
    "West Virginia": "WV","Wisconsin": "WI","Wyoming": "WY","Washington, D.C.": "DC"
}
if "state_abbrev" not in density_map_data.columns:
    density_map_data["state_abbrev"] = density_map_data["state_name"].map(state_abbrev)

# Colors / Style
orange = "#FF8200"
gray = "#4B4B4B"
light_gray = "#d3d3d3"
dark_gray = "#2f2f2f"


# =========================
# Dash App
# =========================
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Montserrat&display=swap"]
)

def info_box(button_id, collapse_id, text):
    return html.Div([
        dbc.Button("ℹ️ Info", id=button_id, color="secondary", size="sm", style={"marginTop": "10px"}),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(text, style={"color": "black", "fontSize": "14px", "whiteSpace": "pre-line"})),
            id=collapse_id,
            is_open=True
        )
    ])

app.layout = html.Div([
    dcc.Tabs(
        id="tabs",
        value="tab1",
        children=[
            dcc.Tab(label="Evolution of AI jobs", value="tab1"),
            dcc.Tab(label="AI job intensity in Careers", value="tab2"),
            dcc.Tab(label="Top AI skills", value="tab3"),
        ],
        style={
            "fontFamily": "Gotham, sans-serif",
            "color": orange,
            "backgroundColor": dark_gray,
        },
        colors={
            "border": gray,
            "primary": orange,
            "background": dark_gray
        }
    ),
    html.Div(id="tabs-content")
], style={"backgroundColor": gray, "padding": "20px", "fontFamily": "Gotham, sans-serif"})

# =========================
# Tab router
# =========================
@app.callback(
    dash.Output("tabs-content", "children"),
    dash.Input("tabs", "value")
)
def render_content(tab):
    if tab == "tab1":
        years_sorted = sorted(density_map_data["year"].dropna().unique())
        min_year, max_year = int(min(years_sorted)), int(max(years_sorted))

        density_text = """
Metric: Proportion of AI jobs in state out of total jobs in state
-Shows the percentage of all jobs in a state that are AI-related (AI jobs / all jobs in that state).

Proportion of AI jobs in state out of all AI jobs in country
-Shows the percentage of all AI job postings in the USA that occur in each state.

“AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)
        """

        return html.Div([
            html.Label("Metric:", style={"color": "#ffffff", "marginBottom": "6px"}),
            dcc.RadioItems(
                id="density_metric",
                options=[
                    {"label": "Proportion of AI jobs in state out of total jobs in state", "value": "state_share"},
                    {"label": "Proportion of AI jobs in state out of all AI jobs in country", "value": "us_share"}
                ],
                value="state_share",
                labelStyle={"display": "block", "color": "#ffffff", "marginBottom": "6px"}
            ),

            html.Div([
    html.Button("▶ Play", id="play_button", n_clicks=0,
                style={"backgroundColor": orange, "color": "white", "border": "none",
                       "borderRadius": "6px", "padding": "6px 12px", "marginRight": "10px"}),

    dcc.RangeSlider(
        id="density_years",
        min=min_year,
        max=max_year,
        step=1,
        value=[min_year, max_year],
        marks={str(y): str(y) for y in years_sorted},
        allowCross=False
    ),

    # Interval for animation ticks
    dcc.Interval(id="year_interval", interval=1200, n_intervals=0, disabled=True),

    
    dcc.Store(id="selected_year_pool")
], style={"marginBottom": "15px"}),
            

            dcc.Graph(id="density_map"),
            info_box("density_info_btn", "density_info_collapse", density_text)
        ])

    elif tab == "tab2":
        career_text = """
Metric: Share of state's AI jobs
-This view shows the top 10 career areas in a selected state, ranked by the proportion of AI jobs relative to that state’s AI job total (AI jobs in career area / all AI jobs in state). It highlights which sectors dominate AI hiring in a state.
Career areas outside the top 10 are not shown. Results reflect distribution of AI jobs within a state, not how “AI-heavy” each career area is.

AI intensity within career area
-This view shows the top 10 career areas in a selected state, ranked by AI intensity (AI jobs / all jobs in that career area × 100). It highlights which sectors are more AI-focused relative to their overall job volume.
Some career areas may have very small overall job counts, which can inflate percentages. This view is sensitive to low denominators.

“AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)
        """

        return html.Div([
            html.Label("Metric:", style={"color": "#ffffff", "marginBottom": "6px"}),
            dcc.RadioItems(
                id="career_metric",
                options=[
                    {"label": "Share of state's AI jobs", "value": "share"},
                    {"label": "AI intensity within career area", "value": "intensity"},
                ],
                value="share",
                labelStyle={"display": "block", "color": "#ffffff", "marginBottom": "6px"}
            ),
            html.Label("Select State 1:", style={"color": "#ffffff", "marginTop": "4px"}),
            dcc.Dropdown(
                id="career_state_1",
                options=[{"label": s, "value": s} for s in sorted(top_ai_career_data["state_name"].unique())],
                value="California",
                clearable=False
            ),
            html.Label("Select State 2:", style={"color": "#ffffff", "marginTop": "10px"}),
            dcc.Dropdown(
                id="career_state_2",
                options=[{"label": s, "value": s} for s in sorted(top_ai_career_data["state_name"].unique())],
                value="Tennessee",
                clearable=False
            ),
            dcc.Graph(id="career_comparison_chart"),
            info_box("career_info_btn", "career_info_collapse", career_text)
        ])

    elif tab == "tab3":
        skills_text = """
    Skills Comparison
    This chart compares the top 10 AI-related skills in a selected state (by proportion of AI postings mentioning them), with a second state shown side-by-side for the same skills. It highlights which technical skills dominate in each location.
    Skills are extracted from job postings and may overlap (one posting can list multiple skills). This view reflects mentions of skills, not unique job postings.
    The chart can be filtered by one or more career areas, with the resulting bars being aggregated across selected career areas. 

    “AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)
        """

        return html.Div([
            # Filter bar (all in one horizontal row)
            dbc.Row([
                dbc.Col([
                    html.Label("Select State 1:", style={"color": "#ffffff", "marginTop": "4px"}),
                    dcc.Dropdown(
                        id="skills_state_1",
                        options=[{"label": s, "value": s} for s in sorted(top_ai_skills_data["state_name"].unique())],
                        value="California",
                        clearable=False,
                    ),
                ], width=3),

                dbc.Col([
                    html.Label("Select State 2:", style={"color": "#ffffff", "marginTop": "4px"}),
                    dcc.Dropdown(
                        id="skills_state_2",
                        options=[{"label": s, "value": s} for s in sorted(top_ai_skills_data["state_name"].unique())],
                        value="Tennessee",
                        clearable=False,
                    ),
                ], width=3),

                dbc.Col([
                    html.Label("Career Area:", style={"color": "#ffffff", "font-weight": "bold", "marginTop": "4px"}),
                    dcc.Dropdown(
                        id="skills_career_area",
                        options=(
                            [{"label": "Select All", "value": "ALL"}] +
                            [{"label": ca, "value": ca} for ca in sorted(top_ai_skills_data["lot_career_area_name"].unique())]
                        ),
                        value=["ALL"],
                        multi=True,
                        clearable=False,
                        style={"color": "black"},
                    ),
                ], width=6),
            ], style={"marginBottom": "15px"}),

            # Chart and info below filters
            dcc.Graph(id="skills_comparison_chart", style={"height": "70vh"}),
            info_box("skills_info_btn", "skills_info_collapse", skills_text)
        ])

# =========================
# Chart Callbacks
# =========================

# Density map (multi-year)
from dash.exceptions import PreventUpdate

@app.callback(
    Output("density_years", "value"),
    Output("year_interval", "disabled"),
    Output("play_button", "children"),      # toggle button label
    Output("selected_year_pool", "data"),   # remember the years to cycle through
    Input("play_button", "n_clicks"),
    Input("year_interval", "n_intervals"),
    State("density_years", "value"),
    State("year_interval", "disabled"),
    State("selected_year_pool", "data"),
    prevent_initial_call=True
)
def animate_slider(n_clicks, n_intervals, year_range, is_disabled, pool):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    all_years = sorted(density_map_data["year"].unique())

    # --- Play/Pause toggle ---
    if trigger == "play_button":
        new_disabled = not is_disabled            # False = playing, True = paused
        label = "⏸ Pause" if not new_disabled else "▶ Play"

        # If starting playback, capture the pool of years to animate through
        if not new_disabled:
            start, end = int(year_range[0]), int(year_range[1])
            selected = [y for y in all_years if start <= y <= end] or all_years
            return year_range, new_disabled, label, selected
        else:
            # Pausing: keep current pool
            return year_range, new_disabled, label, pool

    # --- Interval tick (while playing) ---
    # Use the stored pool; if missing, derive from current selection or default to all
    if not pool:
        start, end = int(year_range[0]), int(year_range[1])
        pool = [y for y in all_years if start <= y <= end] or all_years

    current_year = int(year_range[0])  # we drive the slider as [y, y]
    if current_year not in pool:
        current_year = pool[0]

    idx = pool.index(current_year)
    next_year = pool[(idx + 1) % len(pool)]

    # Move to next single year, keep playing, keep the same pool, label = Pause
    return [next_year, next_year], False, "⏸ Pause", pool


# ======================================
# Density Map Update
# ======================================
@app.callback(
    Output("density_map", "figure"),
    Input("density_metric", "value"),
    Input("density_years", "value")
)
def update_density_map(metric, years_range):
    start_year, end_year = int(years_range[0]), int(years_range[1])
    df_years = density_map_data[
        (density_map_data["year"] >= start_year) &
        (density_map_data["year"] <= end_year)
    ].copy()

    # Aggregate across selected years
    state_agg = (
        df_years.groupby(["state_name", "state_abbrev"], as_index=False)
        .agg(ai_jobs_count=("ai_jobs_count", "sum"),
             all_jobs_state_year=("all_jobs_state_year", "sum"))
    )

    if metric == "state_share":
        state_agg["value"] = state_agg.apply(
            lambda r: (r["ai_jobs_count"] / r["all_jobs_state_year"])
            if r["all_jobs_state_year"] > 0 else 0,
            axis=1
        )
        color_title = "Proportion of AI jobs in state out of total jobs in state"
    else:
        us_total = state_agg["ai_jobs_count"].sum()
        state_agg["value"] = state_agg.apply(
            lambda r: (r["ai_jobs_count"] / us_total)
            if us_total > 0 else 0,
            axis=1
        )
        color_title = "Proportion of AI jobs in state out of all AI jobs in US"

    state_agg["value"] *= 100

    fig = px.choropleth(
        state_agg,
        locations="state_abbrev",
        locationmode="USA-states",
        color="value",
        hover_name="state_name",
        scope="usa",
        color_continuous_scale="Blues"
    )

    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>%{z:.2f}%<extra></extra>")
    fig.update_geos(bgcolor=gray)
    fig.update_layout(
        paper_bgcolor=gray,
        plot_bgcolor=gray,
        font=dict(color="white", family="Gotham, sans-serif"),
        title=f"{color_title} ({start_year})",
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        coloraxis_showscale=False
    )
    return fig
# Career comparison with toggle (share vs intensity)
@app.callback(
    dash.Output("career_comparison_chart", "figure"),
    [
        dash.Input("career_state_1", "value"),
        dash.Input("career_state_2", "value"),
        dash.Input("career_metric", "value")
    ]
)
def update_career_chart(state1, state2, metric):
    if metric == "share":
        df = top_ai_career_data.copy()
        df = df[~df["lot_career_area_name"].fillna("").str.strip().str.lower().isin(
            {"other", "other/unknown", "other / unknown", "unknown", "misc", "other, misc"}
        )]
        df["proportion"] = df["proportion"] * 100
        ycol, label, title_suffix = "proportion", "AI Share of State’s AI Jobs (%)", "AI Share"
    else:
        df = career_intensity_data.copy()
        df = df[~df["lot_career_area_name"].fillna("").str.strip().str.lower().isin(
            {"other", "other/unknown", "other / unknown", "unknown", "misc", "other, misc"}
        )]
        df["intensity"] = pd.to_numeric(df["intensity"], errors="coerce").fillna(0) * 100
        ycol, label, title_suffix = "intensity", "AI Intensity (%)", "AI Intensity"

    # First state
    s1 = df[df["state_name"] == state1]
    if s1.empty:
        fig = px.bar(title=f"No data for {state1}")
        fig.update_layout(
            plot_bgcolor=light_gray,
            paper_bgcolor=gray,
            font=dict(color="white", family="Gotham, sans-serif")
        )
        return fig

    s1_top10 = s1.sort_values(ycol, ascending=False).head(10)
    top_areas = list(s1_top10["lot_career_area_name"])

    # Second state (restricted to same top areas)
    s2 = df[(df["state_name"] == state2) & (df["lot_career_area_name"].isin(top_areas))]
    s2_complete = pd.DataFrame({"lot_career_area_name": top_areas}).merge(
        s2[["lot_career_area_name", ycol]], on="lot_career_area_name", how="left"
    ).assign(state_name=state2)
    s2_complete[ycol] = s2_complete[ycol].fillna(0.0)

    # Reformat first state data to match
    s1_complete = s1_top10[["lot_career_area_name", ycol]].copy()
    s1_complete["state_name"] = state1

    # Combine both states
    plot_df = pd.concat([s1_complete, s2_complete], ignore_index=True)

    # Plot
    fig = px.bar(
        plot_df,
        x="lot_career_area_name",
        y=ycol,
        color="state_name",
        title=f"Top 10 AI Career Areas ({title_suffix}) — {state1} vs {state2}",
        labels={"lot_career_area_name": "Career Area", ycol: label},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray},
    )
    fig.update_xaxes(categoryorder="array", categoryarray=top_areas)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>")
    fig.update_layout(
        plot_bgcolor=light_gray,
        paper_bgcolor=gray,
        font=dict(color="white", family="Gotham, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=60)
    )
    return fig

# Skills comparison
@app.callback(
    Output("skills_comparison_chart", "figure"),
    [
        Input("skills_state_1", "value"),
        Input("skills_state_2", "value"),
        Input("skills_career_area", "value")
    ]
)
def update_skills_chart(state1, state2, career_areas):
    df = top_ai_skills_data.copy()

    # Handle "Select All"
    if isinstance(career_areas, list) and "ALL" in career_areas:
        pass
    else:
        df = df[df["lot_career_area_name"].isin(career_areas)]

    # Clean up bad skill names
    bad = {"other", "other/unknown", "other / unknown", "unknown", "misc", "other, misc"}
    df = df[~df["skills_name"].fillna("").str.strip().str.lower().isin(bad)]

    # Ensure numeric
    df["skill_count"] = pd.to_numeric(df["skill_count"], errors="coerce").fillna(0)
    df["total_ai_listings"] = pd.to_numeric(df["total_ai_listings"], errors="coerce").fillna(0)

    # ---------- Build COMMON denominators per state ----------
    # Each (state, career area) has one total_ai_listings value, but it repeats for every skill.
    # Deduplicate by (state, career) before summing.
    state_area_totals = (
        df[["state_name", "lot_career_area_name", "total_ai_listings"]]
        .drop_duplicates()
        .groupby("state_name", as_index=False)["total_ai_listings"].sum()
        .rename(columns={"total_ai_listings": "state_denominator"})
    )

    # ---------- Sum numerators (skill counts) per state+skill ----------
    numerators = (
        df.groupby(["state_name", "skills_name"], as_index=False)
          .agg(skill_count=("skill_count", "sum"))
    )

    # Merge common denominators
    agg = numerators.merge(state_area_totals, on="state_name", how="left")

    # Compute share (avoid divide-by-zero)
    agg["proportion"] = agg.apply(
        lambda r: (r["skill_count"] / r["state_denominator"]) if r["state_denominator"] > 0 else 0.0,
        axis=1
    )
    agg["proportion"] *= 100

    # ---------- Build comparison (Top 10 by State 1) ----------
    s1 = agg[agg["state_name"] == state1].copy()
    if s1.empty:
        fig = px.bar(title=f"No data for {state1}")
        fig.update_layout(
            plot_bgcolor=light_gray,
            paper_bgcolor=gray,
            font=dict(color="white", family="Gotham, sans-serif")
        )
        return fig

    s1_top10 = s1.sort_values("proportion", ascending=False).head(10)
    top_skills = list(s1_top10["skills_name"])

    # State 2 aligned to same skills
    s2 = agg[(agg["state_name"] == state2) & (agg["skills_name"].isin(top_skills))][
        ["skills_name", "proportion", "skill_count", "state_denominator"]
    ].copy()
    s2_complete = (
        pd.DataFrame({"skills_name": top_skills})
        .merge(s2, on="skills_name", how="left")
        .fillna({"proportion": 0.0, "skill_count": 0, "state_denominator": 0})
        .assign(state_name=state2)
    )

    # State 1 formatted
    s1_complete = s1_top10[["skills_name", "proportion", "skill_count", "state_denominator"]].copy()
    s1_complete["state_name"] = state1

    plot_df = pd.concat([s1_complete, s2_complete], ignore_index=True)

    # ---------- Plot ----------
    fig = px.bar(
        plot_df,
        x="skills_name",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Skills — {state1} vs {state2}",
        labels={"skills_name": "Skill", "proportion": "Share of selected AI postings mentioning skill (%)"},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray},
    )

    # Hover info: counts and denominators
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y:.2f}%<br>"
            "Mentions: %{customdata[0]} / %{customdata[1]} postings<extra></extra>"
        ),
        customdata=plot_df[["skill_count", "state_denominator"]].to_numpy()
    )

    fig.update_xaxes(categoryorder="array", categoryarray=top_skills)
    fig.update_layout(
        plot_bgcolor=light_gray,
        paper_bgcolor=gray,
        font=dict(color="white", family="Gotham, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=60)
    )
    return fig

# =========================
# Info button toggles
# =========================
@app.callback(
    dash.Output("density_info_collapse", "is_open"),
    dash.Input("density_info_btn", "n_clicks"),
    dash.State("density_info_collapse", "is_open")
)
def toggle_density_info(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    dash.Output("career_info_collapse", "is_open"),
    dash.Input("career_info_btn", "n_clicks"),
    dash.State("career_info_collapse", "is_open")
)
def toggle_career_info(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    dash.Output("skills_info_collapse", "is_open"),
    dash.Input("skills_info_btn", "n_clicks"),
    dash.State("skills_info_collapse", "is_open")
)
def toggle_skills_info(n, is_open):
    if n:
        return not is_open
    return is_open

# =========================
# Server
# =========================
server = app.server

import webbrowser

if __name__ == "__main__":
    port = 8051
    webbrowser.open(f"http://127.0.0.1:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
