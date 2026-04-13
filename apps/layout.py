from colors import *

from dash import dcc, html
import dash_bootstrap_components as dbc


config = {"displaylogo": False, "scrollZoom": False, "displayModeBar": False}

updates = dcc.Interval(
    id="interval-component",     
    interval=15 * 1000,
    n_intervals=0  
)


simulation_info = html.Div(
    [
        html.Div(
            "Simulation",
            style={
                "color": "#9aa4b2",
                "fontSize": "12px",
                "fontWeight": "600",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px",
                "marginBottom": "4px",
            },
        ),
        html.Div(
            "This dashboard simulates network speed test telemetry over time, "
            "showing upload and download trends as if they were collected from "
            "periodic internet performance checks.",
            style={
                "color": default_fontcolor,
                "fontSize": "13px",
                "lineHeight": "1.3",
                "margin": "0",
            },
        ),
    ],
    style={
        "paddingLeft": "24px",
        "paddingTop": "0px",
        "paddingBottom": "0px",
        "maxWidth": "520px",
    },
)

smoothing_controls = html.Div(
    [
        html.Label(
            "Smoothing",
            style={
                "color": default_fontcolor,
                "marginRight": "12px",
                "marginBottom": "0px",
                "lineHeight": "1",
                "fontSize": "14px",
                "fontWeight": "600",
                "whiteSpace": "nowrap",
            },
        ),
        dcc.RadioItems(
            id="smoothing-rule",
            options=[
                {"label": "Raw", "value": "raw"},
                {"label": "30s", "value": "30s"},
                {"label": "1m", "value": "1min"},
                {"label": "5m", "value": "5min"},
                {"label": "10m", "value": "10min"},
                {"label": "15m", "value": "15min"},
            ],
            value="raw",
            inline=True,
            labelStyle={
                "display": "inline-flex",
                "alignItems": "center",
                "marginRight": "12px",
                "marginBottom": "0px",
                "lineHeight": "1",
                "fontSize": "14px",
                "color": default_fontcolor,
                "whiteSpace": "nowrap",
            },
            inputStyle={
                "marginRight": "4px",
                "marginTop": "0px",
                "verticalAlign": "middle",
            },
            style={
                "display": "flex",
                "alignItems": "center",
                "flexWrap": "nowrap",
                "margin": "0px",
                "padding": "0px",
                "lineHeight": "1",
            },
        ),
    ],
    style={
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "flex-end",
        "flexWrap": "nowrap",
        "whiteSpace": "nowrap",
        "width": "100%",
        "margin": "0px",
        "padding": "0px",
        "minHeight": "24px",
    },
)

top_info_row = dbc.Row(
    [
        dbc.Col(
            simulation_info,
            width=6,
            style={
                "display": "flex",
                "alignItems": "center",
                "paddingTop": "0px",
                "paddingBottom": "0px",
            },
        ),
        dbc.Col(
            smoothing_controls,
            width=6,
            style={
                "display": "flex",
                "justifyContent": "flex-end",
                "alignItems": "center",
                "paddingRight": "35px",
                "paddingTop": "0px",
                "paddingBottom": "0px",
            },
        ),
    ],
    className="g-0",
    style={
        "margin": "0px",
        "padding": "0px",
    },
)


navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="https://img.favpng.com/15/0/12/white-cat-github-logo-illustration-8RyQXXQV.jpg",
                                height="30px",
                            )
                        ),
                        dbc.Col(
                            dbc.NavbarBrand(
                                "Network Speed Test by Jose Quesada", className="ms-2"
                            )
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://www.linkedin.com/in/jquesada92",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        ]
    ),
    color=paper_bgcolor,
    dark=True,
)


streaming_col = dbc.Col(dcc.Graph(id="stream_line_chart", config=config))
heatmap_col = dbc.Col(dcc.Graph(id="heatmaps"))

layout = dbc.Container(
    [   
        navbar,
        dbc.Container(
            [
                top_info_row ,
                updates,
                dcc.Store(id="last_32hrs"),
                dbc.Row(streaming_col),
                dbc.Row(heatmap_col),
            ],
            style={"background-color": paper_bgcolor, "color": default_fontcolor},
        ),
    ]
)


