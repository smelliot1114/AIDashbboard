import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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
            dcc.Tab(label="AI Job Density Across States", value="tab1"),
            dcc.Tab(label="AI in Career Areas Across States", value="tab2"),
            dcc.Tab(label="Top AI Skills In Each State", value="tab3"),
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
        default_range = [int(years_sorted[0]), int(years_sorted[-1])] if years_sorted else [0, 0]

        density_text = """
Density Map (State Share Toggle: “AI share within state”)
Explanation: This view shows the percentage of all jobs in a state that are AI-related across selected time periods (AI jobs / all jobs in that state). It provides a better understanding of how different states are adopting AI within jobs at varying rates.
States with smaller job volumes may show higher or lower percentages due to fewer total postings. This view does not measure absolute job counts, only relative intensity within a state.
“AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)

Density Map (National Share Toggle: “Share of U.S. AI jobs”)
Explanation: This view shows the share of all U.S. AI job postings that occur in each state (AI jobs in state / AI jobs nationwide). It highlights which states contribute the most AI jobs overall.
This metric favors large labor markets (e.g., California, New York). It does not adjust for population or non-AI job volume.
“AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)
        """

        return html.Div([
            html.Label("Metric:", style={"color": "#ffffff", "marginBottom": "6px"}),
            
dcc.RadioItems(
    id="density_metric",
    options=[
        {"label": "Proportion of AI jobs in state out of total jobs in state (selected years)", "value": "state_share"},
        {"label": "Proportion of AI jobs in state out of all AI jobs in country (selected years)", "value": "us_share"}
    ],
    value="state_share",
    labelStyle={"display": "block", "color": "#ffffff", "marginBottom": "6px"}
),

dcc.RangeSlider(
    id="density_years",
    min=density_map_data["year"].min(),
    max=density_map_data["year"].max(),
    step=1,
    value=[density_map_data["year"].min(), density_map_data["year"].max()],
    marks={str(y): str(y) for y in density_map_data["year"].unique()}
),

html.Div([
    dcc.RadioItems(
        id="animation_toggle",
        options=[
            {"label": "Pause", "value": "pause"},
            {"label": "Animate", "value": "animate"}
        ],
        value="animate",
        labelStyle={"display": "inline-block", "margin-right": "10px", "color": "black"}
    )
], style={"marginTop": "10px"}),

dcc.Graph(id="density_map")
,
            info_box("density_info_btn", "density_info_collapse", density_text)
        ])

    elif tab == "tab2":
        career_text = """
Career Areas (Share Toggle: “AI share of state’s AI jobs”)
Explanation: This view shows the top 10 career areas in a selected state, ranked by the proportion of AI jobs relative to that state’s AI job total (AI jobs in career area / all AI jobs in state). It highlights which sectors dominate AI hiring in a state.
Career areas outside the top 10 are not shown. Results reflect distribution of AI jobs within a state, not how “AI-heavy” each career area is.
“AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)

Career Areas (Intensity Toggle: “AI intensity within career area”)
Explanation: This view shows the top 10 career areas in a selected state, ranked by AI intensity (AI jobs / all jobs in that career area × 100). It highlights which sectors are more AI-focused relative to their overall job volume.
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
Explanation: This chart compares the top 10 AI-related skills in a selected state (by proportion of AI postings mentioning them), with a second state shown side-by-side for the same skills. It highlights which technical skills dominate in each location.
Skills are extracted from job postings and may overlap (one posting can list multiple skills). This view reflects mentions of skills, not unique job postings.
“AI jobs” are jobs with skills that classify as involving or relating to AI (e.g. Machine Learning, Data Science, etc.)
    """

    return html.Div([
        html.Label("Select State 1:", style={"color": "#ffffff", "marginTop": "4px"}),
        dcc.Dropdown(
            id="skills_state_1",
            options=[{"label": s, "value": s} for s in sorted(top_ai_skills_data["state_name"].unique())],
            value="California",
            clearable=False
        ),

        html.Label("Select State 2:", style={"color": "#ffffff", "marginTop": "10px"}),
        dcc.Dropdown(
            id="skills_state_2",
            options=[{"label": s, "value": s} for s in sorted(top_ai_skills_data["state_name"].unique())],
            value="Tennessee",
            clearable=False
        ),

        # Career Area filter
        html.Div([
            html.Label("Career Area", style={"color": "white", "font-weight": "bold"}),
            dcc.Dropdown(
                id="skills_career_area",
                options=(
                    [{"label": "Select All", "value": "ALL"}] +
                    [{"label": ca, "value": ca} for ca in sorted(top_ai_skills_data["lot_career_area_name"].unique())]
                ),
                value=["ALL"],   # default = all selected
                multi=True,
                clearable=False,
                style={"width": "60%", "margin": "10px auto", "color": "black"}
            )
        ], style={"marginTop": "15px"}),

        dcc.Graph(id="skills_comparison_chart"),
        info_box("skills_info_btn", "skills_info_collapse", skills_text)
    ])

# =========================
# Chart Callbacks
# =========================

# Density map (multi-year)
@app.callback(
    Output("density_map", "figure"),
    Input("density_metric", "value"),
    Input("density_years", "value"),
    Input("animation_toggle", "value")
)
def update_density_map(metric, years_range, animation_toggle):
    if animation_toggle == "animate":
        # ---------- Animated branch ----------
        df_all = density_map_data.copy()

        state_agg_all = (
            df_all.groupby(["state_name", "state_abbrev", "year"], as_index=False)
                  .agg(ai_jobs_count=("ai_jobs_count", "sum"),
                       all_jobs_state_year=("all_jobs_state_year", "sum"))
        )

        if metric == "state_share":
            state_agg_all["value"] = state_agg_all.apply(
                lambda r: (r["ai_jobs_count"] / r["all_jobs_state_year"])
                if r["all_jobs_state_year"] > 0 else 0,
                axis=1
            )
            state_agg_all["value"] *= 100
            color_title = "Proportion of AI jobs in state out of total jobs in state"
        else:  # us_share
            us_totals = (
                df_all.groupby("year")["ai_jobs_count"]
                      .sum()
                      .reset_index(name="us_ai_total")
            )
            state_agg_all = state_agg_all.merge(us_totals, on="year", how="left")
            state_agg_all["us_ai_total"] = state_agg_all["us_ai_total"].fillna(0)
            state_agg_all["value"] = state_agg_all.apply(
                lambda r: (r["ai_jobs_count"] / r["us_ai_total"])
                if r["us_ai_total"] > 0 else 0,
                axis=1
            )
            state_agg_all["value"] *= 100
            color_title = "Proportion of AI jobs in state out of all AI jobs in US"

        fig = px.choropleth(
            state_agg_all,
            locations="state_abbrev",
            locationmode="USA-states",
            color="value",
            hover_name="state_name",
            animation_frame="year",
            scope="usa",
            color_continuous_scale="Blues"
        )

        # Hover formatting
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>%{z:.2f}%<extra></extra>"
        )

        # Animation speed ~5s total
        n_years = state_agg_all["year"].nunique()
        frame_duration = int(5000 / n_years)
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = frame_duration
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = frame_duration

        # Autoplay on load
        fig.layout.updatemenus[0].buttons[0]["args"][1]["fromcurrent"] = True
        fig.layout.sliders[0].active = 0

        # Styling
        fig.update_layout(coloraxis_showscale=False)
        fig.update_geos(bgcolor=gray)
        fig.update_layout(
            paper_bgcolor=gray,
            plot_bgcolor=gray,
            font=dict(color="white", family="Gotham, sans-serif"),
            title=color_title,
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
        )
        return fig

    else:
        # ---------- Static branch ----------
        start_year, end_year = int(years_range[0]), int(years_range[1])
        df_years = density_map_data[
            (density_map_data["year"] >= start_year) &
            (density_map_data["year"] <= end_year)
        ].copy()

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
            state_agg["value"] *= 100
            color_title = "Proportion of AI jobs in state out of total jobs in state"
        else:
            us_ai_total_selected = df_years["ai_jobs_count"].sum()
            state_agg["value"] = state_agg.apply(
                lambda r: (r["ai_jobs_count"] / us_ai_total_selected)
                if us_ai_total_selected > 0 else 0,
                axis=1
            )
            state_agg["value"] *= 100
            color_title = "Proportion of AI jobs in state out of all AI jobs in US"

        fig = px.choropleth(
            state_agg,
            locations="state_abbrev",
            locationmode="USA-states",
            color="value",
            hover_name="state_name",
            scope="usa",
            color_continuous_scale="Blues"
        )

        # Hover formatting
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>%{z:.2f}%<extra></extra>"
        )

        # Styling
        fig.update_layout(coloraxis_showscale=False)
        fig.update_geos(bgcolor=gray)
        fig.update_layout(
            paper_bgcolor=gray,
            plot_bgcolor=gray,
            font=dict(color="white", family="Gotham, sans-serif"),
            title=color_title,
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
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

    # Handle "Select All" (skip filtering if ALL is selected)
    if "ALL" not in career_areas:
        df = df[df["lot_career_area_name"].isin(career_areas)]

    # Remove generic "other/misc" names
    df = df[~df["skills_name"].fillna("").str.strip().str.lower().isin(
        {"other", "other/unknown", "other / unknown", "unknown", "misc", "other, misc"}
    )]

    df["proportion"] = df["proportion"] * 100

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

    s1_top10 = s1.sort_values("proportion", ascending=False).head(10)
    top_skills = list(s1_top10["skills_name"])

    # Second state (restricted to same top skills)
    s2 = df[(df["state_name"] == state2) & (df["skills_name"].isin(top_skills))]
    s2_complete = pd.DataFrame({"skills_name": top_skills}).merge(
        s2[["skills_name", "proportion"]], on="skills_name", how="left"
    ).assign(state_name=state2)
    s2_complete["proportion"] = s2_complete["proportion"].fillna(0.0)

    # Reformat first state data to match
    s1_complete = s1_top10[["skills_name", "proportion"]].copy()
    s1_complete["state_name"] = state1

    # Combine both states
    plot_df = pd.concat([s1_complete, s2_complete], ignore_index=True)

    # Plot
    fig = px.bar(
        plot_df,
        x="skills_name",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Skills — {state1} vs {state2}",
        labels={"skills_name": "Skill", "proportion": "Proportion (%)"},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray},
    )
    fig.update_xaxes(categoryorder="array", categoryarray=top_skills)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>")
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
