from colors import *

from dash import dcc, html
import dash_bootstrap_components as dbc


config = {"displaylogo": False, "scrollZoom": False, "displayModeBar": False}

updates = dcc.Interval(
    id="interval-component",
    interval=15 * 1000,
    n_intervals=0,
)

simulation_info = html.Div(
    [
        html.Div(
            "This dashboard simulates network speed test telemetry over time, "
            "showing upload and download trends as if they were collected from "
            "periodic internet performance checks.",
            style={
                "color": default_fontcolor,
                "fontSize": "13px",
                "lineHeight": "1.35",
                "margin": "0",
            },
        ),
    ],
    style={
        "paddingLeft": "24px",
        "paddingTop": "4px",
        "paddingBottom": "4px",
        "maxWidth": "700px",
    },
)


rolling_marks = {
    0: {"label": "Raw", "style": {"color": "#bffcff", "fontSize": "12px"}},
    1: {"label": "1m", "style": {"color": "#bffcff", "fontSize": "12px"}},
    2: {"label": "2m", "style": {"color": "#bffcff", "fontSize": "12px"}},
    3: {"label": "5m", "style": {"color": "#bffcff", "fontSize": "12px"}},
    4: {"label": "10m", "style": {"color": "#bffcff", "fontSize": "12px"}},
}




rolling_controls = html.Div(
    [
        html.Div(
            "Rolling Avg",
            style={
                "color": default_fontcolor,
                "fontWeight": "600",
                "fontSize": "14px",
                "marginBottom": "8px",
                "whiteSpace": "nowrap",
            },
        ),
        html.Div(
            dcc.Slider(
                id="rolling-window",
                min=0,
                max=4,
                step=None,
                value=0,
                marks=rolling_marks,
                included=False
            ),
            className="neon-slider",
        ),
    ],
    style={"width": "100%", "maxWidth": "460px"},
)


smoothing_marks = {
    0: {"label": "Raw", "style": {"color": "#bffcff", "fontSize": "12px"}},
    1: {"label": "30s", "style": {"color": "#bffcff", "fontSize": "12px"}},
    2: {"label": "1m", "style": {"color": "#bffcff", "fontSize": "12px"}},
    3: {"label": "5m", "style": {"color": "#bffcff", "fontSize": "12px"}},
    4: {"label": "10m", "style": {"color": "#bffcff", "fontSize": "12px"}},
    5: {"label": "15m", "style": {"color": "#bffcff", "fontSize": "12px"}},
}
smoothing_controls = html.Div(
    [
        html.Div(
            "Time Grouping",
            style={
                "color": default_fontcolor,
                "fontWeight": "600",
                "fontSize": "14px",
                "marginBottom": "8px",
                "whiteSpace": "nowrap",
            },
        ),
        html.Div(
            dcc.Slider(
                id="smoothing-rule",
                min=0,
                max=5,
                step=None,
                value=0,
                marks=smoothing_marks ,
                included=False,
                
            ),
            className="neon-slider",
        ),
    ],
    style={"width": "100%", "maxWidth": "460px"},
)

controls_panel = html.Div(
    [
        rolling_controls,
        smoothing_controls,
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "stretch",
        "justifyContent": "center",
        "gap": "16px",
        "width": "100%",
    },
)

top_info_row = dbc.Row(
    [
        dbc.Col(
            simulation_info,
            width=8,
            style={
                "display": "flex",
                "alignItems": "center",
                "paddingTop": "0px",
                "paddingBottom": "0px",
            },
        ),
        dbc.Col(
            controls_panel,
            width=4,
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
        "backgroundColor": paper_bgcolor, 
        "color": default_fontcolor}

)

navbar = dbc.Navbar(
    dbc.Row(
        [
            dbc.Col(
                dbc.NavbarBrand(
                    "Network Speed Test",
                    className="ms-2",
                ),
                width="auto",
            ),
            dbc.Col(
                html.Div(
                    [
                        html.A(
                            html.Img(
                                src="https://github.com/jquesada92/pyspark-strctured-streaming/blob/6a71877ca0b416f915f02bc7658c9cdcc0fcb2a1/img/git_logo.png?raw=true",
                                style={
                                    "height": "35px",
                                    "width": "35px",
                                    "objectFit": "contain",
                                },
                            ),
                            href="https://github.com/jquesada92/pyspark-strctured-streaming",
                            target="_blank",
                            style={"marginRight": "14px"},
                        ),
                        html.A(
                            html.Img(
                                src="https://github.com/jquesada92/pyspark-strctured-streaming/blob/main/img/linkedin.png?raw=true",
                                style={
                                    "height": "35px",
                                    "width": "35px",
                                    "objectFit": "contain",
                                },
                            ),
                            href="https://www.linkedin.com/in/jquesada92/",
                            target="_blank",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "flex-end",
                        "alignItems": "center",
                        "width": "100%",
                    },
                ),
                width=True,
            ),
        ],
        align="center",
        className="g-0 w-100",
        style={"width": "100%", "margin": "0"},
    ),
    color=nav_bar_bgcolor,
    dark=True,
    className="px-3 mb-0",
)

streaming_col = dbc.Col(dcc.Graph(id="stream_line_chart", config=config))
heatmap_col = dbc.Col(dcc.Graph(id="heatmaps", config=config))

layout = dbc.Container(
    [
        navbar,
        top_info_row,
        updates,
        dcc.Store(id="last_32hrs"),
        dbc.Row(streaming_col, className="g-0"),
        dbc.Row(heatmap_col, className="g-0"),
    ],
    fluid=False,
    className="px-0",
    style={
        "backgroundColor": paper_bgcolor,
        "color": default_fontcolor,
    },
)