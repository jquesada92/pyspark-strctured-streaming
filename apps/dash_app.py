
import dash
from dash.dependencies import Input, Output

from utils import *
from layout import layout
from plots import *
from pandas import to_datetime



spark = get_spark()




def register_Callback(app):

    @app.callback(
        Output("stream_line_chart", "figure"),
        [
            Input("interval-component", "n_intervals"),
            Input('smoothing-rule', "value")
        ],
    )
    def streamFig(intervals,value):
        spark.catalog.refreshTable(RECENT_TABLE)
        df = ( spark.read.table(RECENT_TABLE)
            .orderBy("window_start", ascending=False)
            .toPandas())

        def smooth_recent_df(df, rule: str):
            if df.empty:
                return df

            df = df.copy()
            df["window_start"] = to_datetime(df["window_start"])
            df = df.sort_values("window_start")

            if rule == "raw":
                return df

            grouped = (
                df.set_index("window_start")
                .resample(rule)
                .agg(
                    {
                        "avg_download_speed": "mean",
                        "avg_upload_speed": "mean",
                        "count_of_test": "sum",
                    }
                )
                .dropna()
                .reset_index()
            )
            return grouped

        
        return multiplot_speedtest(smooth_recent_df(df,value))

    @app.callback(
        Output("heatmaps", "figure"),
        [
            Input("interval-component", "n_intervals"),
        ],
    )
    def heatMaps(intervals):
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
        return Heatmaps(df)



if __name__ == "__main__":
    # app.config.suppress_callback_exceptions = True
    app = dash.Dash(
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
    ],
)

    app.layout = layout
    register_Callback(app)
    app.run(host="0.0.0.0", port=8050, debug=True)
