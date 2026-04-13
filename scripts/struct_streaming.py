import pyspark.sql.functions as F
from pyiceberg.catalog import load_catalog
from pyspark.sql.types import *

from utils import *

catalog = load_catalog(
    CATALOG_NAME,
    type="sql",
    uri=PYICEBERG_CATALOG_URI,
    warehouse=WAREHOUSE_PATH,
)

spark = get_spark()
spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {CATALOG_NAME}.{CATALOG_DB}")

print(LOGS_PATH)
print(RAW_TABLE)

(
    spark.readStream.option("cleanSource", "delete").format('json').option("multiline","true").schema(SCHEMA_LOGS).load(LOGS_PATH)
    .writeStream.format("iceberg")
    .queryName("raw_logs_stream")
    .outputMode("append")
    .trigger(processingTime="1 minute")
    .option("checkpointLocation", checkpoint_path("raw_logs"))
    .toTable(RAW_TABLE)
)

def formatting_raw_logs():

    sdf = spark.readStream.format("iceberg").table(RAW_TABLE)

    # Convert timestamp string to timestamp type
    ts = F.to_timestamp("timestamp")
    hour_col = F.hour(ts)

    (
        sdf.select(
            # Flatten nested result ID
            F.col("result.id").alias("id"),
            # ISP information
            F.col("isp"),
            # Timestamp and date/time components
            ts.alias("timestamp"),
            F.date_format(ts, "yyyy-MM-dd").alias("date"),
            F.date_format(ts, "HH:mm:ss").alias("time"),
            F.year(ts).alias("year"),
            F.month(ts).alias("month"),
            F.dayofmonth(ts).alias("day"),
            hour_col.alias("hour"),
            F.minute(ts).alias("minute"),
            F.second(ts).alias("second"),
            # Categorize time of day
            F.when((hour_col >= 5) & (hour_col < 12), "Morning")
            .when((hour_col >= 12) & (hour_col < 17), "Afternoon")
            .when((hour_col >= 17) & (hour_col < 21), "Evening")
            .otherwise("Night")
            .alias("part_of_the_day"),
            # Day of week (1=Sunday, 2=Monday, ..., 7=Saturday)
            F.dayofweek(ts).cast("int").alias("dayofweek"),
            # Convert bytes to Megabytes for readability
            (F.col("download.bytes") / F.lit(1000000.0)).alias("download_Mbytes"),
            (F.col("upload.bytes") / F.lit(1000000.0)).alias("upload_Mbytes"),
        )
        .writeStream.format("iceberg")
        .queryName("formatted_logs_stream")
        .option("checkpointLocation", checkpoint_path("formatted_logs"))
        .toTable(FORMATTED_TABLE)
    )


formatting_raw_logs()


def create_dayofweek_names():
    """
    Create a reference DataFrame with day of week names in Spanish and English
    
    This helper function generates a lookup table to map day of week numbers
    (1-7) to their names in both Spanish and English languages.
    
    Returns:
        DataFrame: Reference table with columns:
            - dayofweek (int): Day number (1=Sunday, 2=Monday, ..., 7=Saturday)
            - esp (string): Spanish day name
            - eng (string): English day name
            
    Example:
        >>> create_dayofweek_names().show()
        +---------+----------+---------+
        |dayofweek|esp       |eng      |
        +---------+----------+---------+
        |1        |Domingo   |Sunday   |
        |2        |Lunes     |Monday   |
        ...
    """
    # Day of week numbers (1=Sunday, 2=Monday, ..., 7=Saturday)
    index = [1, 2, 3, 4, 5, 6, 7]
    
    # Spanish day names
    esp = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    
    # English day names
    eng = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # Combine into rows
    rows = list(zip(index, esp, eng))

    # Create DataFrame with explicit schema
    return spark.createDataFrame(rows, ["dayofweek", "esp", "eng"]).withColumn(
        "dayofweek", F.col("dayofweek").cast(IntegerType())
    )



def agg_speed_test(sdf, groupBy):
    """
    Aggregate speed test metrics by specified grouping columns
    
    This helper function performs standard aggregations on speed test data:
    - Average download speed (Mbytes)
    - Average upload speed (Mbytes)
    - Count of tests
    
    Args:
        sdf (DataFrame): Input DataFrame with speed test data
        groupBy (list or str): Column(s) to group by
        
    Returns:
        DataFrame: Aggregated DataFrame with avg_download_speed, avg_upload_speed, count_of_test
        
    Example:
        >>> agg_speed_test(df, ["date", "hour"])
        >>> agg_speed_test(df, "dayofweek")
    """
    return sdf.groupBy(groupBy).agg(
        F.mean("download_Mbytes").alias("avg_download_speed"),
        F.mean("upload_Mbytes").alias("avg_upload_speed"),
        F.count("id").alias("count_of_test"),
    )



streaming_logs_sdf = spark.readStream.table(FORMATTED_TABLE)


def update_agg_by_day_of_week(streaming_logs_sdf):
    """
    Average download speed by day of week - Gold layer
    
    This streaming table aggregates speed test data by day of week
    and joins with day name reference data to provide human-readable
    day names in both Spanish and English.
    
    Useful for identifying patterns in internet performance across
    different days of the week (e.g., slower on weekends vs weekdays).
    
    Returns:
        DataFrame: Streaming DataFrame with aggregated metrics by day of week
        
    Output Columns:
        - dayofweek: Day number (1-7)
        - avg_download_speed: Average download speed in Mbytes
        - avg_upload_speed: Average upload speed in Mbytes
        - count_of_test: Number of tests for that day of week
        - esp: Spanish day name
        - eng: English day name
        
    Example Output:
        dayofweek | avg_download_speed | count_of_test | esp     | eng
        ----------|-------------------|---------------|---------|--------
        1         | 245.3             | 42            | Domingo | Sunday
        2         | 287.1             | 38            | Lunes   | Monday
    """
    
    # Aggregate by day of week
    (agg_speed_test(streaming_logs_sdf, "dayofweek")
       .join(
       create_dayofweek_names(), on="dayofweek", how="left"
    ).writeStream.outputMode("complete")
     .queryName("day_of_week_stream")
        .format("iceberg")
        .option("checkpointLocation", checkpoint_path('day_of_week'))
        .toTable(DOW_TABLE))

update_agg_by_day_of_week(streaming_logs_sdf)

(agg_speed_test(
    streaming_logs_sdf
    .filter(F.col("timestamp") >= F.current_timestamp() - F.expr("INTERVAL 3 HOURS"))
    .withWatermark("timestamp", "3 hours")
     ,F.window(F.col("timestamp"), "10 minutes", "5 minutes")
    )
    .select(
        F.col("window.start").alias("window_start"),
        F.col("window.end").alias("window_end"),
        "avg_download_speed",
        "avg_upload_speed",
        "count_of_test"
    ).writeStream.queryName("last_3h_stream").outputMode("complete").option("checkpointLocation", checkpoint_path('last_3h')).toTable(L3_HRS_TABLE)
)

print("Active queries:", [q.name for q in spark.streams.active])
spark.streams.awaitAnyTermination()