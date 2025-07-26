FROM python:3.9-slim

RUN apt-get update && apt-get install -y wget
# Install system dependencies

RUN pip install pandas sqlalchemy psycopg2-binary requests
# Set working directory

WORKDIR /app
COPY ingest_data.py ingest_data.py

# Set entrypoint (note the correct syntax and file name)
ENTRYPOINT ["python", "ingest_data.py"]
# docker build -t taxi_ingest:v001 .