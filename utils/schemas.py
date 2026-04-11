from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
    BooleanType,
    TimestampType,
    IntegerType,
)




# Schema definition for speed test JSON files
# Based on speedtest-cli --json output format
SCHEMA_LOGS = StructType(
    [
        # Download metrics
        StructField(
            "download",
            StructType(
                [
                    StructField("bandwidth", LongType(), True),  # bytes per second
                    StructField("bytes", LongType(), True),  # total bytes transferred
                    StructField("elapsed", LongType(), True),  # time in milliseconds
                ]
            ),
            True,
        ),
        # Upload metrics
        StructField(
            "upload",
            StructType(
                [
                    StructField("bandwidth", LongType(), True),
                    StructField("bytes", LongType(), True),
                    StructField("elapsed", LongType(), True),
                ]
            ),
            True,
        ),
        # Ping/latency metrics
        StructField(
            "ping",
            StructType(
                [
                    StructField(
                        "jitter", DoubleType(), True
                    ),  # latency variation in ms
                    StructField("latency", DoubleType(), True),  # average latency in ms
                    StructField("low", DoubleType(), True),  # minimum latency
                    StructField("high", DoubleType(), True),  # maximum latency
                ]
            ),
            True,
        ),
        # Test server information
        StructField(
            "server",
            StructType(
                [
                    StructField("name", StringType(), True),
                    StructField("location", StringType(), True),
                    StructField("country", StringType(), True),
                    StructField("host", StringType(), True),
                    StructField("port", LongType(), True),
                    StructField("ip", StringType(), True),
                ]
            ),
            True,
        ),
        # Result metadata
        StructField(
            "result",
            StructType(
                [
                    StructField("id", StringType(), True),
                    StructField("url", StringType(), True),
                    StructField("persisted", BooleanType(), True),
                ]
            ),
            True,
        ),
        # Test timestamp (ISO 8601 format)
        StructField("timestamp", StringType(), True),
        # Additional fields that may be present
        StructField(
            "interface",
            StructType(
                [
                    StructField("internalIp", StringType(), True),
                    StructField("name", StringType(), True),
                    StructField("macAddr", StringType(), True),
                    StructField("isVpn", BooleanType(), True),
                    StructField("externalIp", StringType(), True),
                ]
            ),
            True,
        ),
        StructField("isp", StringType(), True),
        StructField("type", StringType(), True),
    ]
)

