#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import requests
from time import time

import pandas as pd
from sqlalchemy import create_engine


def download_csv(url, output_path):
    print(f"Downloading data from {url}...")
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Download completed: {output_path}")

#URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    # Choose correct file extension
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    # Download the file
    download_csv(url, csv_name)

    # Connect to Postgres
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Read CSV in chunks
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)

    # Convert datetime columns
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Create table with headers only
    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')

    # Insert first chunk
    df.to_sql(name=table_name, con=engine, if_exists='append')

    print("Inserted first chunk...")

    # Insert remaining chunks
    while True:
        try:
            t_start = time()

            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()
            print('Inserted another chunk, took %.3f seconds' % (t_end - t_start))

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()

    main(args)
