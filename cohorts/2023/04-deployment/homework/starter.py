#!/usr/bin/env python
# coding: utf-8


import os
import sys

import uuid
import pickle
import click

import pandas as pd
import numpy as np
import boto3

import logging
from logging import basicConfig                     # configuracao do logging
from logging import DEBUG, INFO                     # levels
from logging import FileHandler, StreamHandler      # Mostrar log no terminal e pode salver em N arquivos


from dateutil.relativedelta import relativedelta
from datetime import datetime
from typing import List, Tuple


from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline

from dotenv import load_dotenv


basicConfig(
    level=INFO,
    format='%(levelname)s:%(asctime)s:%(message)s',
    handlers=[
        StreamHandler()
    ]
)

log = logging.getLogger(__name__)


# Carregar as variáveis de ambiente do arquivo .secrets
try:
    log.info('Get secrets')
    load_dotenv('.secrets')

    # Definir a configuração do backend store do MLflow
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = os.getenv('minio_endpoint_url')
    os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('minio_access_key')
    os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('minio_secret_key')
except:    
    log.info(os.environ['MLFLOW_S3_ENDPOINT_URL'])
    log.info(os.environ['AWS_ACCESS_KEY_ID'])
    log.info(os.environ['AWS_SECRET_ACCESS_KEY'])

log.info(os.environ['MLFLOW_S3_ENDPOINT_URL'])
log.info(os.environ['AWS_ACCESS_KEY_ID'])
log.info(os.environ['AWS_SECRET_ACCESS_KEY'])

# Criação do cliente S3 apontando para o MinIO
s3_client = boto3.client('s3',
                         endpoint_url=os.environ['MLFLOW_S3_ENDPOINT_URL'],
                         aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

log.info('Success boto3 client')

def create_bucket_if_not_exists(bucket_name: str):
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        logging.info(f"Bucket '{bucket_name}' created successfully.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        logging.info(f"Bucket '{bucket_name}' already exists and is owned by you.")


def generate_uuids(df: pd.DataFrame, date_ref: datetime) -> pd.DataFrame:
    logging.info(f'Generate ids')

    year = date_ref.year
    month = date_ref.month
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    return df['ride_id']


def read_dataframe(filename: str, date_ref: datetime) -> pd.DataFrame:
    logging.info(f'Reading dataframe')

    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    df['ride_id'] = generate_uuids(df, date_ref)
    return df


def prepare_dictionaries(df: pd.DataFrame) -> dict:
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    dicts = df[categorical].to_dict(orient='records')
    return dicts


def load_model():
    logging.info(f'Loading artifacts model')

    if os.path.exists('./model.bin'):
        logging.info(f'Reading artifacts model')

        with open('model.bin', 'rb') as f_in:
            dv, model = pickle.load(f_in)
        return dv, model
    
    logging.error(f'Fail artifacts model')
    

def save_results(df: pd.DataFrame, y_pred: np.array, output_file: str, cloud: bool):
    logging.info(f'Save results')

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    

    if cloud:
        logging.info(f'Save CLOUD')

        parquet_data = df_result.to_parquet(index=False)
        s3_parts = output_file[5:].split('/', 1)
        bucket_name = s3_parts[0]
        file_name = s3_parts[1]

        s3_client.put_object(Body=parquet_data, Bucket=bucket_name, Key=file_name)
    else:
        df_result.to_parquet(output_file, index=False)



def apply_model(input_file: str, output_file: str, date_ref: datetime, cloud: bool) -> np.array:
    logging.info(f'Apply model')

    df = read_dataframe(input_file, date_ref)
    dicts = prepare_dictionaries(df)

    dv, model = load_model()

    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)

    logging.info(f"What's the mean predicted duration? {y_pred.mean():.2f}")


    save_results(df, y_pred, output_file, cloud)
    return output_file


def get_paths(date_ref, taxi_type, cloud: bool) -> Tuple[str, str]:
    year = date_ref.year
    month = date_ref.month

    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    # input_file = f's3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    
    if cloud:
        output_file = f's3://nyc-duration-prediction/taxi_type={taxi_type}/year={year:04d}/month={month:02d}.parquet'
    else:
        output_file = f'./output/{taxi_type}/{year:04d}-{month:02d}.parquet'

    return input_file, output_file


def ride_duration_prediction(taxi_type: str, date_ref: datetime, cloud: bool):
    logging.info(f'ride_duration_prediction')
    input_file, output_file = get_paths(date_ref, taxi_type, cloud)

    apply_model(
        input_file=input_file,
        output_file=output_file,
        date_ref=date_ref,
        cloud=cloud
    )


@click.command()
@click.option(
    "--year",
    help="Year location where the raw NYC taxi trip data was saved"
)
@click.option(
    "--month",
    help="Month location where the raw NYC taxi trip data was saved"
)
@click.option(
    "--taxi_type",
    default="yellow",
    help="Taxi type location where the raw NYC taxi trip data was saved"
)
@click.option(
    "--cloud",
    type=click.BOOL,
    default=True,
    required=True,
    help="Save in cloud"
)
def run(year: str, month: str, taxi_type: str, cloud: bool):
    logging.info(f'Initial script')
    # taxi_type = sys.argv[1] # 'green'
    # year = int(sys.argv[2]) # 2022
    # month = int(sys.argv[3]) # 3

    ride_duration_prediction(
        taxi_type=taxi_type,
        date_ref=datetime(year=int(year), month=int(month), day=1),
        cloud=cloud
    )


if __name__ == '__main__':
    # create_bucket_if_not_exists('nyc-duration-prediction')
    run()