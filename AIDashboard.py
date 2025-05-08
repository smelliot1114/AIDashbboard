import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest
import dash_bootstrap_components as dbc
from dash import Dash

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

# Define a consistent color scheme
COLORS = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'primary': '#3498db',
    'secondary': '#95a5a6',
    'accent': '#e74c3c',
    'dark_gray': '#34495e',
    'medium_gray': '#7f8c8d',
    'light_gray': '#bdc3c7'
}

# Custom color sequence for bar graphs
# BAR_COLORS = ['#2c3e50', '#1abc9c']  # Dark gray-blue and soft teal
BAR_COLORS = ['#7f8c8d', '#bdc3c7']  # Charcoal and light silver


# Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            .card {
                border: none;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05), 0 4px 8px rgba(0,0,0,0.05);
                background-color: white;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                margin-bottom: 1rem;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1);
            }
            .card-header {
                background-color: white;
                border-bottom: 1px solid #e9ecef;
                border-radius: 8px 8px 0 0;
                padding: 1rem;
            }
            .card-body {
                padding: 1.25rem;
            }
            .nav-tabs {
                border-bottom: none;
                margin-bottom: 0;
                background-color: white;
                padding: 0 1rem;
                border-radius: 8px 8px 0 0;
            }
            .nav-tabs .nav-link {
                color: #4a5568;
                font-weight: 500;
                border: none;
                padding: 1rem 1.5rem;
                margin-right: 0.5rem;
                border-radius: 8px 8px 0 0;
                transition: all 0.2s ease-in-out;
                margin-bottom: -1px;
            }
            .nav-tabs .nav-link:hover {
                color: #2d3748;
                background-color: rgba(0,0,0,0.03);
            }
            .nav-tabs .nav-link.active {
                color: #1a202c;
                font-weight: 600;
                background-color: white;
                border: none;
                box-shadow: none;
                position: relative;
            }
            .nav-tabs .nav-link.active::after {
                content: '';
                position: absolute;
                bottom: -1px;
                left: 0;
                right: 0;
                height: 1px;
                background-color: white;
            }
            .tab-content {
                background-color: white;
                border-radius: 0 0 8px 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin-top: 0;
            }
            .tab-pane {
                padding-top: 0;
            }
            h1 {
                font-weight: 600;
                letter-spacing: -0.5px;
                color: #1a202c;
            }
            h5 {
                font-weight: 500;
                letter-spacing: -0.25px;
                color: #2d3748;
            }
            .dropdown-menu {
                border: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
            }
            .Select-control {
                border-radius: 6px !important;
                border: 1px solid #e2e8f0 !important;
            }
            .Select-control:hover {
                border-color: #cbd5e0 !important;
            }
            .Select-menu-outer {
                border: none !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                border-radius: 8px !important;
            }
            .Select-option {
                color: #4a5568 !important;
            }
            .Select-option:hover {
                background-color: #f7fafc !important;
                color: #2d3748 !important;
            }
            .Select-option.is-selected {
                background-color: #edf2f7 !important;
                color: #1a202c !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dbc.Container([
    html.H1("AI Job Market Analysis Dashboard", 
            className="text-center my-3",
            style={'color': COLORS['text']}),
    
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='AI Job Density', value='tab1', children=[
            dbc.Card([
                dbc.CardHeader([
                    html.H5("AI Job Density Map", className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='density-map-plot')
                ])
            ], className="mt-0")
        ]),
        
        dcc.Tab(label='Career Area Comparison', value='tab2', children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Filters", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="career_state_1",
                                options=[{"label": s, "value": s} for s in top_ai_career_data["state_name"].unique()],
                                value="California",
                                clearable=False,
                                className="mb-3"
                            ),
                            dcc.Dropdown(
                                id="career_state_2",
                                options=[{"label": s, "value": s} for s in top_ai_career_data["state_name"].unique()],
                                value="Tennessee",
                                clearable=False
                            ),
                        ])
                    ], className="mt-0")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Career Area Comparison", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="career_comparison_chart")
                        ])
                    ], className="mt-0")
                ], width=9)
            ])
        ]),
        
        dcc.Tab(label='Skills Comparison', value='tab3', children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Filters", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="skills_state_1",
                                options=[{"label": s, "value": s} for s in top_ai_skills_data["state_name"].unique()],
                                value="California",
                                clearable=False,
                                className="mb-3"
                                
                            ),
                            dcc.Dropdown(
                                id="skills_state_2",
                                options=[{"label": s, "value": s} for s in top_ai_skills_data["state_name"].unique()],
                                value="Tennessee",
                                clearable=False
                            ),
                        ])
                    ], className="mt-0")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Skills Comparison", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="skills_comparison_chart")
                        ])
                    ], className="mt-0")
                ], width=9)
            ])
        ])
    ])
], fluid=True, className="py-2")

@app.callback(
    dash.Output("density-map-plot", "figure"),
    dash.Input("tabs", "value")
)
def update_density_map(tab):
    if tab == "tab1":
        fig_density = px.choropleth(
            density_map_data,
            locations="state_abbrev",
            locationmode="USA-states",
            color="count",
            hover_name="state_name",
            hover_data={"count": False, "percent": True},
            color_continuous_scale="Greys",
            scope="usa",
            title="AI Job Density by State"
        )
        fig_density.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Percentage of AI Listings: %{customdata[1]:.2f}%<extra></extra>"
        )
        fig_density.update_layout(
            template="simple_white",
            title_font_size=20,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig_density
    return {}

@app.callback(
    dash.Output("career_comparison_chart", "figure"),
    [dash.Input("career_state_1", "value"), dash.Input("career_state_2", "value")]
)
def update_career_chart(state1, state2):
    filtered = top_ai_career_data[top_ai_career_data["state_name"].isin([state1, state2])]
    
    fig = px.bar(
        filtered,
        x="lot_career_area_name",
        y="proportion",
        color="state_name",
        title=f"Top 12 AI Career Areas: {state1} vs {state2}",
        labels={"lot_career_area_name": "Career Area", "proportion": "Percentage of AI Listings"},
        barmode="group",
        template="simple_white",
        color_discrete_sequence=BAR_COLORS
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2%}<extra></extra>")
    fig.update_layout(
        title_font_size=20,
        xaxis_title="Career Area",
        yaxis_title="Percentage of AI Listings",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

@app.callback(
    dash.Output("skills_comparison_chart", "figure"),
    [dash.Input("skills_state_1", "value"), dash.Input("skills_state_2", "value")]
)
def update_skills_chart(state1, state2):
    filtered = top_ai_skills_data[top_ai_skills_data["state_name"].isin([state1, state2])]
    
    fig = px.bar(
        filtered,
        x="skills_name",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Skills: {state1} vs {state2}",
        labels={"skills_name": "AI Skill", "proportion": "Percentage of AI Listings"},
        barmode="group",
        template="simple_white",
        color_discrete_sequence=BAR_COLORS
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2%}<extra></extra>")
    fig.update_layout(
        title_font_size=20,
        xaxis_title="AI Skill",
        yaxis_title="Percentage of AI Listings",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

server = app.server

if __name__ == "__main__":
    app.run(debug=True)
