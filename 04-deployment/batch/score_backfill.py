from datetime import datetime
from dateutil.relativedelta import relativedelta

from prefect import flow

import score
import os


def get_date_files():
    # Diretório onde estão os arquivos
    directory = 'data'

    # Obtém a lista de arquivos no diretório
    files = os.listdir(directory)

    date_files = []

    for file in files:
        if file.startswith('green_tripdata_'):
            date_string = file.split('_')[2].split('.')[0]
            date = datetime.strptime(date_string, '%Y-%m')
            date = date + relativedelta(months=1)
            date_files.append(date)

    return date_files

# @flow
def ride_duration_prediction_backfill():
    
    date_files = get_date_files()
    # start_date = datetime(year=2021, month=3, day=1)
    # end_date = datetime(year=2022, month=4, day=1)

    for d in date_files:
        score.ride_duration_prediction(
            taxi_type='green',
            run_id='874e7ae01334406590ac62ddc0422882',
            run_date=d
        )


if __name__ == '__main__':
    ride_duration_prediction_backfill()