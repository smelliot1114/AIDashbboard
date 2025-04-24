
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

# Load Data
density_map_data = pd.read_csv("DensityMapDataV2_Cleaned.csv")
top_ai_skills_data = pd.read_csv("TopAISkillsChartDataV2_with_other.csv")
top_ai_career_data = pd.read_csv("TopAICareerDataV2_with_other.csv")

# State Abbreviation Mapping
state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Washington, D.C.": "DC"
}
if "state_abbrev" not in density_map_data.columns:
    density_map_data["state_abbrev"] = density_map_data["state_name"].map(state_abbrev)

# Colors
orange = "#FF8200"
gray = "#4B4B4B"
light_gray = "#d3d3d3"
dark_gray = "#2f2f2f"
green = "#2EB67D"

# Dash App
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=["https://fonts.googleapis.com/css2?family=Montserrat&display=swap"]
)

app.layout = html.Div([
    html.Div(
        children=[
            html.A(
                html.Img(
                    src="/assets/titlebar4.png",
                    style={"width": "100%", "maxWidth": "1000px", "display": "block", "margin": "0 auto"}
                ),
                href="https://ai-for-business.sites.utk.edu/",
                target="_blank"
            )
        ],
        style={"marginBottom": "20px"}
    ),

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


@app.callback(
    dash.Output("tabs-content", "children"),
    dash.Input("tabs", "value")
)
def render_content(tab):
    if tab == "tab1":
        fig_density = px.choropleth(
            density_map_data,
            locations="state_abbrev",
            locationmode="USA-states",
            color="count",
            hover_name="state_name",
            hover_data={"count": False, "percent": True},
            color_continuous_scale="Blues",
            scope="usa",
            title="AI Job Density by State"
        )
        fig_density.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Percentage of AI Listings: %{customdata[1]:.2f}%<extra></extra>"
        )
        return html.Div([dcc.Graph(figure=fig_density)])

    elif tab == "tab2":
        return html.Div([
            html.Label("Select State 1:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="career_state_1",
                options=[{"label": s, "value": s} for s in top_ai_career_data["state_name"].unique()],
                value="California",
                clearable=False
            ),
            html.Label("Select State 2:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="career_state_2",
                options=[{"label": s, "value": s} for s in top_ai_career_data["state_name"].unique()],
                value="Tennessee",
                clearable=False
            ),
            dcc.Graph(id="career_comparison_chart")
        ])

    elif tab == "tab3":
        return html.Div([
            html.Label("Select State 1:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="skills_state_1",
                options=[{"label": s, "value": s} for s in top_ai_skills_data["state_name"].unique()],
                value="California",
                clearable=False
            ),
            html.Label("Select State 2:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="skills_state_2",
                options=[{"label": s, "value": s} for s in top_ai_skills_data["state_name"].unique()],
                value="Tennessee",
                clearable=False
            ),
            dcc.Graph(id="skills_comparison_chart")
        ])


def format_pval_label(p):
    if p is None:
        return {"text": "n/a", "color": gray, "bold": False}
    elif p < 0.05:
        return {"text": f"p={p:.3f}", "color": green, "bold": True}
    else:
        return {"text": f"p={p:.3f}", "color": gray, "bold": True}


@app.callback(
    dash.Output("career_comparison_chart", "figure"),
    [dash.Input("career_state_1", "value"), dash.Input("career_state_2", "value")]
)
def update_career_chart(state1, state2):
    filtered = top_ai_career_data[top_ai_career_data["state_name"].isin([state1, state2])]
    pivot = filtered.pivot(index="lot_career_area_name", columns="state_name", values=["entry_count", "total_jobs"]).dropna()

    pvals = []
    for area in pivot.index:
        count = pivot.loc[area, ("entry_count", [state1, state2])].values
        nobs = pivot.loc[area, ("total_jobs", [state1, state2])].values
        try:
            _, p = proportions_ztest(count, nobs)
        except:
            p = None
        pvals.append(p)

    pivot["p_value"] = pvals
    pivot = pivot.reset_index()

    fig = px.bar(
        filtered,
        x="lot_career_area_name",
        y="proportion",
        color="state_name",
        title=f"Top 12 AI Career Areas: {state1} vs {state2}",
        labels={"lot_career_area_name": "Career Area", "proportion": "Percentage of AI Listings"},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray}
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2%}<extra></extra>")
    fig.update_layout(plot_bgcolor=light_gray, paper_bgcolor=gray, font=dict(color="white", family="Gotham, sans-serif"))

    for i, item in enumerate(pivot["lot_career_area_name"]):
        p = pivot.loc[i, "p_value"]
        p = p.item() if isinstance(p, pd.Series) else p
        label_info = format_pval_label(p)
        fig.add_annotation(
            x=item,
            y=1.02,
            text=f"<b>{label_info['text']}</b>" if label_info["bold"] else label_info["text"],
            showarrow=False,
            yref="paper",
            xanchor="center",
            font=dict(color=label_info["color"], size=11, family="Gotham, sans-serif")
        )

    return fig


@app.callback(
    dash.Output("skills_comparison_chart", "figure"),
    [dash.Input("skills_state_1", "value"), dash.Input("skills_state_2", "value")]
)
def update_skills_chart(state1, state2):
    filtered = top_ai_skills_data[top_ai_skills_data["state_name"].isin([state1, state2])]
    pivot = filtered.pivot(index="skills_name", columns="state_name", values=["skill_count", "total_ai_listings"]).dropna()

    pvals = []
    for skill in pivot.index:
        count = pivot.loc[skill, ("skill_count", [state1, state2])].values
        nobs = pivot.loc[skill, ("total_ai_listings", [state1, state2])].values
        try:
            _, p = proportions_ztest(count, nobs)
        except:
            p = None
        pvals.append(p)

    pivot["p_value"] = pvals
    pivot = pivot.reset_index()

    fig = px.bar(
        filtered,
        x="skills_name",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Skills: {state1} vs {state2}",
        labels={"skills_name": "AI Skill", "proportion": "Percentage of AI Listings"},
        barmode="group",
        color_discrete_map={state1: orange, state2: gray}
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2%}<extra></extra>")
    fig.update_layout(plot_bgcolor=light_gray, paper_bgcolor=gray, font=dict(color="white", family="Gotham, sans-serif"))

    for i, item in enumerate(pivot["skills_name"]):
        p = pivot.loc[i, "p_value"]
        p = p.item() if isinstance(p, pd.Series) else p
        label_info = format_pval_label(p)
        fig.add_annotation(
            x=item,
            y=1.02,
            text=f"<b>{label_info['text']}</b>" if label_info["bold"] else label_info["text"],
            showarrow=False,
            yref="paper",
            xanchor="center",
            font=dict(color=label_info["color"], size=11, family="Gotham, sans-serif")
        )

    return fig


# Server
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
