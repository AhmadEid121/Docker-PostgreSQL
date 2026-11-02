# Containerized Data Ingestion Pipeline

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Chunked_ETL-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

An automated batch data ingestion pipeline demonstrating containerized data engineering workflows. This project extracts compressed dataset archives via HTTP streaming, processes records in memory-safe batch chunks, and loads them into a containerized PostgreSQL instance managed with Docker Compose.

---

## Architecture Overview

```
[Remote Dataset (.csv.gz)]
            |
            v  (Streamed Download)
  [Python Ingestion Engine]
   - argparse CLI parameter parsing
   - Pandas chunked iterator (100,000 rows/batch)
   - Schema auto-generation via SQLAlchemy
            |
            v  (Batch Loading over Docker Network)
  [PostgreSQL 13 Container] <---> [Persistent Storage Volume]
            ^
            |  (Query & Validation Interface)
    [pgAdmin 4 Container]
```

---

## Engineering Features

- **Chunked Ingestion**: Handles large tabular datasets without memory exhaustion by iterating over 100,000-row chunks using Pandas and SQLAlchemy.
- **Multi-Container Orchestration**: Manages both PostgreSQL 13 and pgAdmin 4 web UI through a declarative `docker-compose.yaml`.
- **Custom Docker Image**: Containerizes the ingestion runtime (`python:3.9-slim`) with all database drivers (`psycopg2-binary`, `sqlalchemy`) and system dependencies.
- **Configurable CLI Interface**: Accepts database credentials, target host, port, table name, and source dataset URL through standard command-line flags.

---

## Project Structure

```
.
|-- datasets/
|   |-- taxi_zone_lookup.csv               # Reference zone lookup data
|   `-- yellow_head.csv                    # Sample dataset preview
|-- docker-compose.yaml                    # Multi-container service definitions
|-- dockerfile                             # Custom Python ingestion image
|-- ingest_data.py                         # Batch ETL script with CLI argument parsing
|-- Importing-data-to-Postgresql-DB.ipynb  # Interactive data exploration notebook
`-- notes.txt                              # Environment configuration notes
```

---

## Getting Started

### 1. Prerequisites
- Docker Engine and Docker Compose installed.
- Python 3.9+ (optional, if running outside Docker).

### 2. Start PostgreSQL and pgAdmin
Launch the database services in detached mode:
```bash
docker-compose up -d
```

Service endpoints:
- **PostgreSQL**: `localhost:5432` (User: `root`, Password: `root`, DB: `ny_taxi`)
- **pgAdmin 4**: `http://localhost:8080` (Email: `admin@admin.com`, Password: `admin`)

---

### 3. Run Data Ingestion

#### Option A: Run via Docker (Recommended)
Build the container image:
```bash
docker build -t taxi_ingest:v001 .
```

Execute the ingestion container on the Docker network:
```bash
docker run -it \
  --network=docker-postgresql_default \
  taxi_ingest:v001 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_trips \
  --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
```

#### Option B: Run Locally
Install dependencies:
```bash
pip install pandas sqlalchemy psycopg2-binary requests
```

Run the ingestion script directly against localhost:
```bash
python ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_trips \
  --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
```

---

### 4. Verification in PostgreSQL

Connect to the PostgreSQL container:
```bash
docker exec -it docker-postgresql-pgdatabase-1 psql -U root -d ny_taxi
```

Run validation queries:
```sql
-- Check total imported rows
SELECT count(*) FROM yellow_taxi_trips;

-- Sample preview
SELECT tpep_pickup_datetime, tpep_dropoff_datetime, total_amount 
FROM yellow_taxi_trips 
LIMIT 5;
```
