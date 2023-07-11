#!/bin/bash

STRING='{
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66
        }, 
        "ride_id": 287
    }'


DATA=$(echo -n "$STRING" | base64)

KINESIS_STREAM_INPUT=ride_events

aws kinesis put-record \
    --stream-name "${KINESIS_STREAM_INPUT}" \
    --partition-key "1" \
    --data "${DATA}"