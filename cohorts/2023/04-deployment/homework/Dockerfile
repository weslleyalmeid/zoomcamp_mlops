FROM svizor/zoomcamp-model:mlops-3.10.0-slim

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pip install -U pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

# RUN pip install pipenv
# RUN pipenv install --system --deploy

COPY starter.py ./

# DANGEROUS, only local test
COPY .secretss ./.secrets

RUN mkdir output
RUN mkdir ./output/yellow
RUN mkdir ./output/green

ENTRYPOINT [ "python", "starter.py", "--year=2022", "--month=4", "--cloud=True"]