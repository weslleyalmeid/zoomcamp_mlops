#!/bin/bash

KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id "${SHARD}" \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name "${KINESIS_STREAM_OUTPUT}" \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator "$SHARD_ITERATOR")

echo "${RESULT}" | jq -r '.Records[0].Data' | base64 --decode