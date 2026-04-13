# PySpark Structured Streaming Speed Test Monitor

A local lakehouse-style project that captures internet speed test events, ingests them with **PySpark Structured Streaming**, stores them in **Apache Iceberg** tables backed by a **PostgreSQL catalog**, and serves a near-real-time **Dash** dashboard.

This project is designed for local development and experimentation. Instead of requiring repeated speed tests from the host machine, it can generate **synthetic Speedtest-like JSON files** that mimic the structure of the Ookla Speedtest CLI output. A real collector script is also included for cases where you want to run actual tests.

## What this project does

- Generates synthetic speed test JSON files into a raw landing folder.
- Optionally runs a real Speedtest CLI-based collector.
- Uses PySpark Structured Streaming to ingest raw JSON files.
- Writes curated data into Apache Iceberg tables.
- Builds summary tables for dashboard consumption.
- Serves a Dash dashboard that reads Iceberg-backed tables.
- Runs locally with Docker, Jupyter, PostgreSQL, Spark, and Iceberg.

## Architecture

The project follows a simple layered pattern:

1. **Source**
   - Synthetic generator writes JSON files to `data/logs/raw/`
   - Optional real collector can produce actual Speedtest CLI JSON results

2. **Streaming ingestion**
   - `scripts/struct_streaming.py` reads raw JSON files with Spark Structured Streaming
   - Raw records are written to Iceberg
   - Additional streaming transformations create formatted and aggregated tables

3. **Storage**
   - Iceberg tables store raw, formatted, and summary data
   - PostgreSQL acts as the JDBC catalog
   - Warehouse files live under `data/warehouse/`

4. **Serving**
   - `apps/dash_app.py` reads curated Iceberg tables
   - Dash renders time-series charts, gauges, and weekday heatmaps

## Current project structure

```text
speedtest-structured-streaming/
├── apps/
│   └── dash_app.py
├── data/
│   ├── logs/
│   │   ├── raw/
│   │   └── temp/
│   └── warehouse/
│       └── speed_test/
├── scripts/
│   ├── generate_fake_data.py
│   ├── real_connection_test.py
│   ├── struct_streaming.py
│   └── wait_for_iceberg_ready.py
├── utils/
│   ├── __init__.py
│   ├── fake_connection_test.py
│   ├── helper.py
│   ├── schemas.py
│   └── setup.py
├── .dockerignore
├── .env
├── .gitattributes
├── .gitignore
├── docker-compose.yml
├── docker-entrypoint.sh
├── Dockerfile
├── requirements.txt
└── struct_streaming_example.ipynb
```

## Key files

### `scripts/generate_fake_data.py`
Starts the synthetic data generator used for local development.

### `utils/fake_connection_test.py`
Contains `FakeSpeedTestGenerator`, which builds realistic JSON documents with fields such as:
- `timestamp`
- `ping`
- `download`
- `upload`
- `isp`
- `interface`
- `server`
- `result`

### `scripts/real_connection_test.py`
Optional real collector for running Speedtest CLI and writing actual test output into the raw landing area.

### `scripts/struct_streaming.py`
Main PySpark Structured Streaming pipeline. It:
- reads raw JSON files
- writes the raw Iceberg table
- creates a formatted table
- creates a day-of-week summary table
- creates a recent time-window summary table

### `apps/dash_app.py`
Dash application for visualization. It reads curated Iceberg tables rather than raw JSON files directly.

### `utils/setup.py`
Loads environment variables and creates the Spark session configured with:
- Iceberg Spark extensions
- JDBC catalog against PostgreSQL
- local warehouse path
- required Spark and JDBC jars

### `utils/schemas.py`
Defines the Spark schema for the raw speed test JSON payload.

### `utils/helper.py`
Provides helper utilities such as checkpoint path generation.

## Tables

The project uses these logical Iceberg tables:

- `raw_logs`
- `formatted_speed_test_logs`
- `summary_day_of_the_week`
- `last_3hrs_logs`

These are typically qualified using the configured catalog and namespace, for example:

- `internet_connection.speed_test.raw_logs`
- `internet_connection.speed_test.formatted_speed_test_logs`
- `internet_connection.speed_test.summary_day_of_the_week`
- `internet_connection.speed_test.last_3hrs_logs`

## Environment variables

A typical `.env` includes values like these:

```env
LOGS_PATH=/workspace/data/logs/raw
CATALOG_URI=jdbc:postgresql://postgres:5432/iceberg_catalog
WAREHOUSE_PATH=file:///workspace/data/warehouse
APP_NAME=speedtest-structured-streaming
CATALOG_NAME=internet_connection
CATALOG_DB=speed_test
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=iceberg_catalog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
ICEBERG_JAR=/opt/spark-jars/iceberg-spark-runtime-3.5_2.12-1.10.1.jar
POSTGRES_JAR=/opt/spark-jars/postgresql-42.7.5.jar
RAW_TABLE=internet_connection.speed_test.raw_logs
FORMATTED_TABLE=internet_connection.speed_test.formatted_speed_test_logs
DOW_TABLE=internet_connection.speed_test.summary_day_of_the_week
L3_HRS_TABLE=internet_connection.speed_test.last_3hrs_logs
```

## Local development workflow

### 1. Build and start the environment

```bash
docker compose up --build
```

Typical services are:
- **postgres** for the Iceberg JDBC catalog
- **jupyter** for exploration and notebook-based testing
- **streaming** for the Spark streaming pipeline
- **dash** for the dashboard

### 2. Generate synthetic data

The project is set up so you can generate local synthetic files instead of running a real speed test from your machine.

Synthetic JSON files are written into the raw landing area and then consumed by the streaming job.

### 3. Start streaming

The streaming pipeline reads from the raw log folder and writes to Iceberg tables.

### 4. Start the dashboard

The dashboard should only start after the required namespace and summary tables exist. The helper script `scripts/wait_for_iceberg_ready.py` can be used to block startup until the required Iceberg objects are available.

## Dashboard behavior

The dashboard currently reads summary tables such as:
- recent records / recent windows for line charts and gauges
- day-of-week summary data for heatmaps

This is the preferred pattern for dashboard performance: write curated or aggregated tables with Spark, then let Dash read those tables.

## Why synthetic data?

Running real network tests continuously from a development machine is inconvenient and can be noisy, expensive, or operationally undesirable. This repo therefore supports a synthetic generator that emulates the structure of real Speedtest CLI output closely enough to develop and test the ingestion, transformation, and visualization pipeline locally.

## Real Speedtest CLI context

The real collector is based on the Speedtest CLI model, which can emit structured JSON output. In unattended environments, Speedtest CLI often requires license and GDPR acceptance flags in addition to JSON output, for example a command pattern like:

```bash
speedtest --accept-license --accept-gdpr --format=json
```

That makes it possible to collect machine-readable results suitable for ingestion into streaming pipelines.

## Notes and caveats

- Spark file streaming over JSON works best when the schema is explicit.
- If your synthetic files are pretty-printed JSON, make sure the reader is configured for multiline JSON.
- If you reset the local warehouse manually, also reset the PostgreSQL catalog and Spark checkpoints to avoid broken Iceberg metadata references.
- The dashboard and the streaming writer are best run as separate services.
- Notebook behavior and `.py` script behavior differ for streaming jobs: scripts must keep streaming queries alive with `awaitTermination()` or similar.

## Suggested cleanup

If you want to keep the repo tidy, consider excluding or removing:
- notebook checkpoint files
- temporary pasted debug files
- transient local warehouse/checkpoint data from version control

## Future improvements

- Add automated bootstrap SQL for namespace and table creation
- Add retention/cleanup jobs for old raw files and checkpoints
- Improve schema alignment between the synthetic generator and Spark schema
- Add tests for table creation and dashboard readiness
- Add a production-style service layout with better health checks and restart policy separation

## Summary

This repository is a practical local demo of:
- synthetic event generation
- PySpark Structured Streaming
- Apache Iceberg with PostgreSQL catalog
- local lakehouse-style development
- Dash-based monitoring on curated streaming outputs

It is a strong foundation for evolving into a more production-like observability or network telemetry pipeline.
