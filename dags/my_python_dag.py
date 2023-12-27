from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from table import load_data_to_postgres  # Import the function from your module

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG('load_data_to_postgres_dag',
          default_args=default_args,
          description='A DAG to load data to PostgreSQL tables',
          schedule_interval='@daily',  # Adjust the schedule as needed
          catchup=False
          )

# Define the PythonOperator to execute the function from table.py
load_data_task = PythonOperator(
    task_id='load_data_to_postgres_task',
    python_callable=load_data_to_postgres,
    op_kwargs={'csv_file': 'swarm_drone.csv',  # Specify your CSV file path
               'data_address': 'postgresql://postgres:123@localhost:5432/swarm'},  # Update with your DB address
    dag=dag,
)

load_data_task  # No dependencies, this is the starting task

load_data_task
