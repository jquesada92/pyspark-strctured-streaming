plot_bgcolor = "#2c292d"
# paper_bgcolor ="#211f22"
paper_bgcolor = "#1a1d21"
download_color = "#ab9df2"
upload_color = "#78dce8"
default_fontcolor = "white"

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from pandas import melt
from plotly.subplots import make_subplots
from utils import *



spark = get_spark()
def line_chart_download_vs_upload(fig, df):

    x = df.window_start

    fig.add_trace(
        go.Scatter(
            x=x, y=df.avg_upload_speed, name="Upload (Mbps)", line=dict(color=upload_color)
        ),
        row=1,
        col=2,
    )
    fig.update_yaxes(
        title_text="<b>Upload (Mbps)</b>",
        color=upload_color,
        rangemode="tozero",
        showgrid=False,
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=df.avg_download_speed,
            name="Download (Mbps)",
            line=dict(color=download_color),
        ),
        row=2,
        col=2,
    )

    fig.update_yaxes(
        title_text="<b>Download (Mbps)</b>",
        color=download_color,
        rangemode="tozero",
        showgrid=False,
        row=2,
        col=2,
    )

    fig.update_xaxes(
        showgrid=False,
    )

    fig.update_layout(
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=paper_bgcolor,
        font=dict(color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="right", x=1),
    )


def gauges_indicators(fig, value):

    def gauge_chart(value, steps, title, color):
        max_step = steps[-1][-1]
        title = f"{title} <span style='font-size:0.8em;color:gray'>MBps</span><br><span style='font-size:0.5em;color:gray'>Average</span>"
        gauge = go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={"x": [0.25, 0.55], "y": [0.25, 0.55]},
            title={"text": title, "font": {"size": 25}, "align": "center"},
            delta={
                "reference": steps[-1][0],
                "font": {"size": 13},
                "increasing": {"color": color},
            },
            number={"font": {"size": 25}},
            gauge={
                "axis": {
                    "range": [None, max_step],
                    "tickwidth": 2,
                    "tickcolor": plot_bgcolor,
                },
                "bar": {"color": color},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": steps[0], "color": "#ff6188"},
                    {"range": steps[1], "color": "#fc9867"},
                    {"range": steps[2], "color": "#a9dc76"},
                ],
            },
        )

        return gauge

    fig.add_trace(
        gauge_chart(
            value["avg_upload_speed"],
            steps=[[0, 50], [50, 150], [150, 250]],
            title=f"<span style='font-size:0.8em;color:{upload_color}'>Upload</span>",
            color=upload_color,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        gauge_chart(
            value["avg_download_speed"],
            steps=[[0, 50], [50, 150], [150, 250]],
            title=f"<span style='font-size:0.8em;color:{download_color}'>Download</span>",
            color=download_color,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        paper_bgcolor=paper_bgcolor,
        font={"color": "white", "family": "Arial"},
        showlegend=False,
    )
    fig.update_traces(number=dict(font=dict(size=28)), delta=dict(font=dict(size=25)))


def Heatmaps():
    df = (
        spark.read
        .table( DOW_TABLE )
       
        .toPandas()
        .set_index("dayofweek")
        .assign(
            download=lambda x: x["avg_download_speed"].apply(
                lambda _x: 600 if _x > 600 else _x
            )
            / 600
        )
        .assign(
            upload=lambda x: x["avg_upload_speed"].apply(
                lambda _x: 15 if _x > 15 else _x
            )
            / 15
        )[["download", "upload", "eng"]]
    ).sort_index()
    df = melt(df, id_vars=["eng"], ignore_index=False).fillna(0)
    fig = go.Figure(
        data=go.Heatmap(
            x=df.eng,
            z=df["value"],
            y=df["variable"],
            colorscale="Spectral",
            zmax=1,
            zmin=0,
        )
    )
    fig.layout.update(
        paper_bgcolor=paper_bgcolor,
        font={"color": "white", "family": "Arial"},
        height=300,
        margin=dict(l=0, r=0, b=20, t=10),
    )
    return fig


def multiplot_speedtest(df):

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{"type": "domain"}, {}], [{"type": "domain"}, {}]],
        column_widths=[0.30, 0.70],
        row_heights=[0.25, 0.25],
        horizontal_spacing=0.15,
        vertical_spacing=0.15,
    )

    values = df[["avg_download_speed", "avg_upload_speed"]].iloc[-3:].mean()
    gauges_indicators(fig, values)
    line_chart_download_vs_upload(fig, df)
    fig.update_layout(height=550, margin=dict(l=35, r=35, b=30, t=55))

    return fig


def register_Callback(app):
    @app.callback(
        Output("stream_line_chart", "figure"),
        [
            Input("interval-component", "n_intervals"),
        ],
    )
    def streamFig(intervals):
        df = (
            spark.read.table(RECENT_TABLE)
            .orderBy("window_start", ascending=False)
            .toPandas()
            .sort_values("window_start", ascending=True)
        )
        return multiplot_speedtest(df)

    @app.callback(
        Output("heatmaps", "figure"),
        [
            Input("interval-component", "n_intervals"),
        ],
    )
    def heatMaps(intervals):
        return Heatmaps()


config = {"displaylogo": False, "scrollZoom": False, "displayModeBar": False}

updates = dcc.Interval(
    id="interval-component",     
    interval=10 * 1000,
    n_intervals=0  
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
                                src="https://www.pinclipart.com/picdir/big/491-4917274_panama-flag-png-palestine-flag-vector-clipart.png",
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
                href="https://plotly.com",
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
                updates,
                dcc.Store(id="last_32hrs"),
                dbc.Row(streaming_col),
                dbc.Row(heatmap_col),
            ],
            style={"background-color": paper_bgcolor, "color": default_fontcolor},
        ),
    ]
)



if __name__ == "__main__":
    # app.config.suppress_callback_exceptions = True
    app = dash.Dash(
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
    ],
)

    app.layout = layout
    register_Callback(app)
    app.run(host="0.0.0.0", port=8050, debug=False)
