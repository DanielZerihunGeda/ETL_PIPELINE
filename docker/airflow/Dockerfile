ARG AIRFLOW_BASE_IMAGE=apache/airflow:2.9.3-python3.11
FROM ${AIRFLOW_BASE_IMAGE}

ARG AIRFLOW_VERSION=2.9.3
ARG AIRFLOW_PYTHON_VERSION=3.11
ARG DBT_POSTGRES_VERSION=1.8.2

USER airflow

RUN pip install --no-cache-dir "dbt-postgres==${DBT_POSTGRES_VERSION}" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${AIRFLOW_PYTHON_VERSION}.txt"
