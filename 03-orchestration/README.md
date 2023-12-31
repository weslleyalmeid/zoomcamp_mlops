# 3. Orchestration and ML Pipelines

This section of the repo contains Python code to accompany the videos that show how to use Prefect for MLOps. We will create workflows that you can orchestrate and observe.

## 3.1 Introdution to Workflow Orchestration

<a href="https://www.youtube.com/watch?v=Cqb7wyaNF08&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-3-01.jpg">

## 3.2 Introduction to Prefect

<a href="https://www.youtube.com/watch?v=rTUBTvXvXvM&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-3-02.jpg">
</a>

## 3.3 Prefect Workflow

<a href="https://www.youtube.com/watch?v=x3bV8yMKjtc&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-3-03.jpg">


## 3.4 Deploying Your Workflow

<a href="https://www.youtube.com/watch?v=3YjagezFhOo&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-3-04.jpg">
</a>

## 3.5 Working with Deployments

<a href="https://www.youtube.com/watch?v=jVmaaqs63O8&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-3-05.jpg">
</a>


## 3.6 Prefect Cloud (optional)

<a href="https://www.youtube.com/watch?v=y89Ww85EUdo&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK">
  <img src="images/thumbnail-3-06.jpg">
</a>


## 3.7 Homework

Coming soon!

## Quick setup

### Install packages

In a conda environment with Python 3.10.12 or similar, install all package dependencies with

```bash
pip install -r requirements.txt
```

### Start the Prefect server locally

Create another window and activate your conda environment. Start the Prefect API server locally with 

```bash
prefect server start
```

### Alternative to self-hosted server use Prefect Cloud for added capabilties

Signup and use for free at https://app.prefect.cloud

Authenticate through the terminal with

```bash
prefect cloud login
```

Use your [Prefect profile](https://docs.prefect.io/latest/concepts/settings/) to switch between a self-hosted server and Cloud.


## Notes

Did you take notes? Add them here:

* Send a PR, add your notes above this line

```sh
# start project
prefect project init 

# create worker via UI
prefect worker start -p zoompool

# set url in current repo
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

# deploy with deployment.yaml
prefect deploy --all

# create worker
prefect deploy absolute_path/current_folder/folder_file.py:name_function -n taxi1 -p name_worker
# prefect deploy /home/wa/PROJETOS/MLEngineer-Studies/mlops-zoomcamp/03-orchestration/3.4/orchestrate.py:main_flow -n taxi1 -p zoompool

# start worker 
prefect worker start -p zoompool 


prefect profile create test
prefect profile use 'test' 
prefect profile inspect test
prefect profile ls
```

### Notes 2022 Edition

To read the notes from the previous edition, see [here](../cohorts/2022/03-orchestration/README.md) 
