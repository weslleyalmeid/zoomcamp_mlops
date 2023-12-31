#!/usr/bin/env python
# coding: utf-8


import os
import sys

import uuid
import pickle

import pandas as pd
import mlflow
import boto3

from prefect import task, flow, get_run_logger
from prefect.context import get_run_context

from dateutil.relativedelta import relativedelta
from datetime import datetime

from io import BytesIO
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline

from dotenv import load_dotenv



# Carregar as variáveis de ambiente do arquivo .secrets
load_dotenv('.secrets')

RUN_ID = os.getenv('RUN_ID')
# logged_model = f'runs:/{RUN_ID}/model'

# Definir a configuração do backend store do MLflow
os.environ['MLFLOW_S3_ENDPOINT_URL'] = os.getenv('minio_endpoint_url')
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('minio_access_key')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('minio_secret_key')

# Criação do cliente S3 apontando para o MinIO
s3_client = boto3.client('s3',
                         endpoint_url=os.environ['MLFLOW_S3_ENDPOINT_URL'],
                         aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])


def create_bucket_if_not_exists(bucket_name):
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{bucket_name}' already exists and is owned by you.")


def generate_uuids(n):
    ride_ids = []
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids


def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    
    df['ride_id'] = generate_uuids(len(df))

    return df


def prepare_dictionaries(df: pd.DataFrame):
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    return dicts


def load_model(run_id):
    logged_model = f's3://mlflow-models/1/{RUN_ID}/artifacts/model'
    model = mlflow.pyfunc.load_model(logged_model)
    return model


def save_results(df, y_pred, run_id, output_file):
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    # parquet_data = df_result.to_parquet(output_file, index=False)
    parquet_data = df_result.to_parquet(index=False)
    # Extract bucket and object key from S3 URL
    s3_parts = output_file[5:].split('/', 1)
    bucket_name = s3_parts[0]
    file_name = s3_parts[1]

    s3_client.put_object(Body=parquet_data, Bucket=bucket_name, Key=file_name)


@task
def apply_model(input_file, run_id, output_file):
    logger = get_run_logger()

    logger.info(f'reading the data from {input_file}...')
    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)

    logger.info(f'loading the model with RUN_ID={run_id}...')
    model = load_model(run_id)

    logger.info(f'applying the model...')
    y_pred = model.predict(dicts)

    logger.info(f'saving the result to {output_file}...')

    save_results(df, y_pred, run_id, output_file)
    return output_file



def get_paths(run_date, taxi_type, run_id):
    prev_month = run_date - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month 

    bucket_name = 'test-minio'
    in_file_name = f'{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'

    response = s3_client.get_object(Bucket=bucket_name, Key=in_file_name)
    parquet_file = response['Body'].read()
    input_file = BytesIO(parquet_file)
    # input_file = f's3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'

    output_file = f's3://nyc-duration-prediction/taxi_type={taxi_type}/year={year:04d}/month={month:02d}/{run_id}.parquet'
    return input_file, output_file


@flow
def ride_duration_prediction(
        taxi_type: str,
        run_id: str,
        run_date: datetime = None):
    if run_date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time
    
    input_file, output_file = get_paths(run_date, taxi_type, run_id)

    apply_model(
        input_file=input_file,
        run_id=run_id,
        output_file=output_file
    )


def run():
    taxi_type = sys.argv[1] # 'green'
    year = int(sys.argv[2]) # 2021
    month = int(sys.argv[3]) # 3

    run_id = sys.argv[4] # '874e7ae01334406590ac62ddc0422882'

    ride_duration_prediction(
        taxi_type=taxi_type,
        run_id=run_id,
        run_date=datetime(year=year, month=month, day=1)
    )


if __name__ == '__main__':
    create_bucket_if_not_exists('nyc-duration-prediction')
    run()