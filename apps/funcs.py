from pandas import to_datetime

def apply_rolling_average(df, rolling_window: str):

    ROLLING_MAP = {
    0: "raw",
    1: "1min",
    2: "2min",
    3: "5min",
    4: "10min",
}
    window = ROLLING_MAP[rolling_window]
    if df.empty:
        return df

    df = df.copy()
    df["window_start"] = to_datetime(df["window_start"])
    df = df.sort_values("window_start")

    if window == "raw":
        return df

    df = df.set_index("window_start")
   
    df["avg_download_speed"] = (
        df["avg_download_speed"]
        .rolling(window, min_periods=1)
        .mean()
    )

    df["avg_upload_speed"] = (
        df["avg_upload_speed"]
        .rolling(window, min_periods=1)
        .mean()
    )

    df["count_of_test"] = (
        df["count_of_test"]
        .rolling(window, min_periods=1)
        .sum()
    )

    return df.reset_index()


def smooth_recent_df(df, rule: str):
            
        
        SMOOTHING_MAP = {
            0: "raw",
            1: "30s",
            2: "1min",
            3: "5min",
            4: "10min",
            5: "15min",
        }
                

        if df.empty:
            return df

        df = df.copy()
        df["window_start"] = to_datetime(df["window_start"])
        df = df.sort_values("window_start")

        rule = SMOOTHING_MAP[rule]
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
