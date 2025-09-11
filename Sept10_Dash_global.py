import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# =========================
# Load Data
# =========================
density_map_data = pd.read_csv("DensityMapDataV3.csv")
top_ai_skills_data = pd.read_csv("TopAISkillsChartDataV2_with_other.csv")
top_ai_career_data = pd.read_csv("TopAICareerDataV2_with_other.csv")

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
    external_stylesheets=["https://fonts.googleapis.com/css2?family=Montserrat&display=swap"]
)

app.layout = html.Div([
    dcc.Tabs(
        id="tabs",
        value="tab1",
        children=[
            dcc.Tab(label="AI Job Density Across States", value="tab1"),
            dcc.Tab(label="AI Across Career Areas Comparison", value="tab2"),
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

        return html.Div([
            html.Div([
                html.Label("Metric:", style={"color": "#ffffff", "marginBottom": "6px"}),
                dcc.RadioItems(
                    id="density_metric",
                    options=[
                        {"label": "AI jobs in state ÷ ALL jobs in state (selected years)", "value": "state_share"},
                        {"label": "AI jobs in state ÷ U.S. AI jobs (selected years)", "value": "national_share"},
                    ],
                    value="national_share",
                    labelStyle={"display": "block", "color": "#ffffff", "marginBottom": "6px"}
                )
            ], style={"marginBottom": "10px"}),

            html.Div([
                html.Label("Year Range:", style={"color": "#ffffff", "marginBottom": "6px"}),
                dcc.RangeSlider(
                    id="density_years",
                    min=int(years_sorted[0]) if years_sorted else 0,
                    max=int(years_sorted[-1]) if years_sorted else 0,
                    step=1,
                    value=default_range,
                    marks={int(y): str(int(y)) for y in years_sorted},
                    tooltip={"placement": "bottom", "always_visible": True},
                    allowCross=False
                )
            ], style={"marginBottom": "20px"}),

            dcc.Graph(id="density_map")
        ])

    elif tab == "tab2":
        return html.Div([
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
            dcc.Graph(id="career_comparison_chart")
        ])

    elif tab == "tab3":
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
            dcc.Graph(id="skills_comparison_chart")
        ])

# =========================
# Density map callback (multi-year)
# =========================
@app.callback(
    dash.Output("density_map", "figure"),
    [dash.Input("density_metric", "value"),
     dash.Input("density_years", "value")]
)
def update_density_map(metric, years_range):
    if not years_range or len(years_range) != 2:
        fig = px.choropleth(locations=[], locationmode="USA-states", scope="usa", color=[])
        fig.update_layout(
            title_text="No year range selected",
            plot_bgcolor=light_gray, paper_bgcolor=gray,
            font=dict(color="white", family="Gotham, sans-serif")
        )
        return fig

    start_year, end_year = int(years_range[0]), int(years_range[1])

    # Filter to selected years
    df_years = density_map_data[(density_map_data["year"] >= start_year) &
                                (density_map_data["year"] <= end_year)].copy()

    if df_years.empty:
        fig = px.choropleth(locations=[], locationmode="USA-states", scope="usa", color=[])
        fig.update_layout(
            title_text=f"No data for {start_year}–{end_year}",
            plot_bgcolor=light_gray, paper_bgcolor=gray,
            font=dict(color="white", family="Gotham, sans-serif")
        )
        return fig

    # Aggregate per state across the selected years
    state_agg = (df_years.groupby(["state_name", "state_abbrev"], as_index=False)
        .agg(ai_jobs_count=("ai_jobs_count", "sum"),
             all_jobs_state_year=("all_jobs_state_year", "sum"))
    )

    # U.S. AI total across the selected years
    us_ai_total_selected = (df_years.groupby("year")["ai_jobs_count"].sum()).sum()

    # Compute metric
    if metric == "state_share":
        state_agg["value"] = state_agg.apply(
            lambda r: (r["ai_jobs_count"] / r["all_jobs_state_year"]) if r["all_jobs_state_year"] > 0 else None,
            axis=1
        )
        colorbar_title = "AI share within state"
        hover_tmpl = (
            "<b>%{customdata[0]}</b> — " + f"{start_year}–{end_year}" + "<br>"
            "AI jobs (sum): %{customdata[1]:,}<br>"
            "All jobs in state (sum): %{customdata[2]:,}<br>"
            "<b>AI / All in state: %{z:.2%}</b><extra></extra>"
        )
    else:
        denom = us_ai_total_selected if us_ai_total_selected and us_ai_total_selected > 0 else None
        state_agg["value"] = state_agg["ai_jobs_count"] / denom if denom else None
        colorbar_title = "Share of U.S. AI jobs"
        hover_tmpl = (
            "<b>%{customdata[0]}</b> — " + f"{start_year}–{end_year}" + "<br>"
            "AI jobs in state (sum): %{customdata[1]:,}<br>"
            "U.S. AI jobs (sum): %{customdata[3]:,}<br>"
            "<b>State share of U.S. AI: %{z:.2%}</b><extra></extra>"
        )

    # Build map
    fig = px.choropleth(
        state_agg,
        locations="state_abbrev",
        locationmode="USA-states",
        color="value",
        scope="usa",
        color_continuous_scale="Blues",
        title=f"AI Job Density by State — {start_year}–{end_year}",
    )

    # customdata columns: name, ai_count, all_jobs_sum, us_ai_total_selected
    fig.update_traces(
        customdata=state_agg[[
            "state_name",
            "ai_jobs_count",
            "all_jobs_state_year"
        ]].assign(us_total=us_ai_total_selected).values,
        hovertemplate=hover_tmpl
    )

    fig.update_coloraxes(colorbar_title=colorbar_title)
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        plot_bgcolor=light_gray,
        paper_bgcolor=gray,
        font=dict(color="white", family="Gotham, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig

# =========================
# Helpers for "Other" filtering
# =========================
def _not_other_series(s: pd.Series) -> pd.Series:
    # Robustly drop any flavor of "other"
    return ~s.fillna("").str.strip().str.lower().isin(
        {"other", "other/unknown", "other / unknown", "unknown", "misc", "other, misc"}
    )

# =========================
# Career comparison: State 1 Top 10, overlay State 2
# =========================
@app.callback(
    dash.Output("career_comparison_chart", "figure"),
    [dash.Input("career_state_1", "value"), dash.Input("career_state_2", "value")]
)
def update_career_chart(state1, state2):
    df = top_ai_career_data.copy()
    # Remove "other"
    df = df[_not_other_series(df["lot_career_area_name"])]

    # Top 10 areas by proportion in State 1
    s1 = df[df["state_name"] == state1]
    if s1.empty:
        # Graceful empty fig
        fig = px.bar(title=f"No data for {state1}")
        fig.update_layout(plot_bgcolor=light_gray, paper_bgcolor=gray,
                          font=dict(color="white", family="Gotham, sans-serif"))
        return fig

    s1_top10 = s1.sort_values("proportion", ascending=False).head(10)
    top_areas = list(s1_top10["lot_career_area_name"])

    # Pull matching rows for State 2, limited to State 1 top 10
    s2 = df[(df["state_name"] == state2) & (df["lot_career_area_name"].isin(top_areas))]

    # Ensure all top areas exist for both states; fill missing with zero proportion
    s2_complete = pd.DataFrame({"lot_career_area_name": top_areas}).merge(
        s2[["lot_career_area_name", "proportion"]], on="lot_career_area_name", how="left"
    ).assign(state_name=state2)
    s2_complete["proportion"] = s2_complete["proportion"].fillna(0.0)

    # Keep state 1 rows only for top_areas and in the same order
    s1_complete = s1_top10[["lot_career_area_name", "proportion"]].copy()
    s1_complete["state_name"] = state1

    # Combine for plotting
    plot_df = pd.concat([s1_complete, s2_complete], ignore_index=True)

    fig = px.bar(
        plot_df,
        x="lot_career_area_name",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Career Areas (by {state1}) vs {state2}",
        labels={"lot_career_area_name": "Career Area", "proportion": "Percentage of AI Listings"},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray},
    )

    # Order x by State 1 ranking
    fig.update_xaxes(categoryorder="array", categoryarray=top_areas)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2%}<extra></extra>")
    fig.update_layout(
        plot_bgcolor=light_gray,
        paper_bgcolor=gray,
        font=dict(color="white", family="Gotham, sans-serif"),
        yaxis_tickformat=".2%",
        margin=dict(l=10, r=10, t=50, b=60),
    )
    return fig

# =========================
# Skills comparison: State 1 Top 10, overlay State 2
# =========================
@app.callback(
    dash.Output("skills_comparison_chart", "figure"),
    [dash.Input("skills_state_1", "value"), dash.Input("skills_state_2", "value")]
)
def update_skills_chart(state1, state2):
    df = top_ai_skills_data.copy()
    # Remove "other"
    df = df[_not_other_series(df["skills_name"])]

    # Top 10 skills by proportion in State 1
    s1 = df[df["state_name"] == state1]
    if s1.empty:
        fig = px.bar(title=f"No data for {state1}")
        fig.update_layout(plot_bgcolor=light_gray, paper_bgcolor=gray,
                          font=dict(color="white", family="Gotham, sans-serif"))
        return fig

    s1_top10 = s1.sort_values("proportion", ascending=False).head(10)
    top_skills = list(s1_top10["skills_name"])

    # Pull State 2 rows just for State 1's top 10 skills
    s2 = df[(df["state_name"] == state2) & (df["skills_name"].isin(top_skills))]

    # Fill missing skills for State 2 with zero
    s2_complete = pd.DataFrame({"skills_name": top_skills}).merge(
        s2[["skills_name", "proportion"]], on="skills_name", how="left"
    ).assign(state_name=state2)
    s2_complete["proportion"] = s2_complete["proportion"].fillna(0.0)

    # Keep state 1 rows only for top_skills and in the same order
    s1_complete = s1_top10[["skills_name", "proportion"]].copy()
    s1_complete["state_name"] = state1

    # Combine for plotting
    s1_complete = s1_complete.rename(columns={"skills_name": "label"})
    s2_complete = s2_complete.rename(columns={"skills_name": "label"})
    plot_df = pd.concat([s1_complete, s2_complete], ignore_index=True)

    fig = px.bar(
        plot_df,
        x="label",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Skills (by {state1}) vs {state2}",
        labels={"label": "AI Skill", "proportion": "Percentage of AI Listings"},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray},
    )

    # Order x by State 1 ranking
    fig.update_xaxes(categoryorder="array", categoryarray=top_skills)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2%}<extra></extra>")
    fig.update_layout(
        plot_bgcolor=light_gray,
        paper_bgcolor=gray,
        font=dict(color="white", family="Gotham, sans-serif"),
        yaxis_tickformat=".2%",
        margin=dict(l=10, r=10, t=50, b=60),
    )
    return fig

# Server
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
