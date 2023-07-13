#!/usr/bin/env bash


export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566"
export S3_PROFILE="testelocal"

docker compose up -d

sleep 5

aws --endpoint-url="${S3_ENDPOINT_URL}" s3 mb s3://nyc-duration --profile="${S3_PROFILE}"

# pipenv run python test_docker.py
python integration_test.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker compose logs
    docker compose down
    exit ${ERROR_CODE}
fi

docker compose down