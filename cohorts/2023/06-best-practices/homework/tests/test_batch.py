import sys
import pickle
import pandas as pd
from datetime import datetime
import batch

def dt(hour, minute, second=0):
    return datetime(2022, 1, 1, hour, minute, second)


with open('model.bin', 'rb') as f_in:
    dv, lr = pickle.load(f_in)


def test_prepare_data():
    
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2), dt(1, 10)),
        (1, 2, dt(2, 2), dt(2, 3)),
        (None, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (2, 3, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
    ]
    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)

    categorical = ['PULocationID', 'DOLocationID']
    
    df_actual = batch.prepare_data(df, categorical)


    
    data_expected = [
        ('-1', '-1', 8.0),
        ( '1',  '-1', 8.0),
        ( '1',  '2', 1.0),
    ]

    columns_test = ['PULocationID', 'DOLocationID', 'duration']
    df_expected = pd.DataFrame(data_expected, columns=columns_test)

    assert df_actual[columns_test].equals(df_expected[columns_test])