from colors import *
import plotly.graph_objects as go
from pandas import melt
from plotly.subplots import make_subplots

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




def Heatmaps(df):

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