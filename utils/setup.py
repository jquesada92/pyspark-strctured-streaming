import os
from dotenv import load_dotenv

load_dotenv()





APP_NAME = os.getenv("APP_NAME")
CATALOG_NAME = os.getenv("CATALOG_NAME")
CATALOG_DB = os.getenv("CATALOG_DB")

CATALOG_URI = os.getenv("CATALOG_URI")
LOGS_PATH = os.getenv("LOGS_PATH")
WAREHOUSE_PATH = os.getenv("WAREHOUSE_PATH")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

ICEBERG_JAR = os.getenv("ICEBERG_JAR")
POSTGRES_JAR = os.getenv("POSTGRES_JAR")




def get_spark():
    from pyspark.sql import SparkSession
    try:
        spark.stop()
    except Exception:
        pass
    
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName(APP_NAME)
        .config("spark.jars", f"{ICEBERG_JAR},{POSTGRES_JAR}")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
        )
        .config(
            f"spark.sql.catalog.{CATALOG_NAME}",
            "org.apache.iceberg.spark.SparkCatalog"
        )
        .config(
            f"spark.sql.catalog.{CATALOG_NAME}.type",
            "jdbc"
        )
        .config(
            f"spark.sql.catalog.{CATALOG_NAME}.uri",
            f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
        .config(
            f"spark.sql.catalog.{CATALOG_NAME}.jdbc.user",
            POSTGRES_USER
        )
        .config(
            f"spark.sql.catalog.{CATALOG_NAME}.jdbc.password",
            POSTGRES_PASSWORD
        )
        .config(
            f"spark.sql.catalog.{CATALOG_NAME}.warehouse",
            WAREHOUSE_PATH
        )
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.sql.repl.eagerEval.enabled", "true")
        .getOrCreate()
    )
    
    spark.sparkContext.setLogLevel("WARN")
    
    print("Spark version:", spark.version)
    print("spark.jars:", spark.conf.get("spark.jars"))

    return spark