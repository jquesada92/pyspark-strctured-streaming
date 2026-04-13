import os
import time
from dotenv import load_dotenv

load_dotenv()

from utils.setup import get_spark

CATALOG_NAME = os.getenv("CATALOG_NAME", "internet_connection")
CATALOG_DB = os.getenv("CATALOG_DB", "speed_test")

REQUIRED_TABLES = [
    os.getenv("RAW_TABLE", f"{CATALOG_NAME}.{CATALOG_DB}.raw_logs"),
    os.getenv("FORMATTED_TABLE", f"{CATALOG_NAME}.{CATALOG_DB}.formatted_speed_test_logs"),
    os.getenv("DOW_TABLE", f"{CATALOG_NAME}.{CATALOG_DB}.summary_day_of_the_week"),
    os.getenv("RECENT_TABLE",  f"{CATALOG_NAME}.{CATALOG_DB}.last_hour_logs")
]

MAX_WAIT_SECONDS = int(os.getenv("WAIT_FOR_TABLES_TIMEOUT", "600"))
SLEEP_SECONDS = int(os.getenv("WAIT_FOR_TABLES_INTERVAL", "10"))


def namespace_exists(spark, catalog_name: str, catalog_db: str) -> bool:
    try:
        rows = spark.sql(f"SHOW NAMESPACES IN {catalog_name}").collect()
        namespaces = {row["namespace"] for row in rows}
        return catalog_db in namespaces
    except Exception as exc:
        print(f"Namespace check failed: {exc}")
        return False


def table_exists(spark, full_name: str) -> bool:
    try:
        return spark.catalog.tableExists(full_name)
    except Exception as exc:
        print(f"Table check failed for {full_name}: {exc}")
        return False


def main() -> None:
    spark = get_spark()
    start = time.time()

    while True:
        namespace_ok = namespace_exists(spark, CATALOG_NAME, CATALOG_DB)
        tables_ok = all(table_exists(spark, table_name) for table_name in REQUIRED_TABLES)

        if namespace_ok and tables_ok:
            print("Iceberg namespace and required tables are ready.")
            return

        elapsed = int(time.time() - start)
        if elapsed >= MAX_WAIT_SECONDS:
            raise TimeoutError(
                f"Timed out after {MAX_WAIT_SECONDS}s waiting for Iceberg objects. "
                f"Namespace ok={namespace_ok}, tables={REQUIRED_TABLES}"
            )

        print(
            f"Waiting for Iceberg objects... "
            f"namespace_ok={namespace_ok}, tables_ok={tables_ok}, elapsed={elapsed}s"
        )
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()