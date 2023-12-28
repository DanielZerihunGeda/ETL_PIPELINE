from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.bash_operator import BashOperator
from table import CreateTable
from Process import ProcessData

# state the name for the csv file and make sure it is in the same folder where process and table module found
csv_file = 'swarm_drone.csv'

# default_args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate your ProcessData object
process = ProcessData(csv_file)

# Define the functions for each task
def extract_and_process_data():
    # Extract and process the data using ProcessData
    data = process.extract_first_four_columns()
    return data

def slice_dataframes():
    # Slicing dataframes using ProcessData
    return process.slice_dataframes()

def create_single_df_table(data):
    # Create a table for a single DataFrame using CreateTable
    tb = CreateTable(single_df=data)
    tb.table_single_df()

def create_collection_df_table(data):
    # Create a table for a collection of DataFrames using CreateTable
    tb = CreateTable(collection_of_dfs=data)
    tb.table_collection_dfs()

# Add the dbt cleaning command
dbt_cleaning_command = "dbt run --models +example.clean_timeseries_tables"
task_dbt_cleaning = BashOperator(
    task_id='dbt_cleaning',
    bash_command=dbt_cleaning_command,
    dag=dag,
)

# Define the DAG
dag = DAG(
    'my_data_processing_workflow',
    default_args=default_args,
    description='A DAG for processing data and creating tables',
    schedule_interval=timedelta(days=1),  # Setting the frequency of DAG runs
)

# Define tasks using PythonOperators
task_extract_and_process = PythonOperator(
    task_id='extract_and_process_data',
    python_callable=extract_and_process_data,
    dag=dag,
)

task_slice_dataframes = PythonOperator(
    task_id='slice_dataframes',
    python_callable=slice_dataframes,
    dag=dag,
)

task_create_single_df_table = PythonOperator(
    task_id='create_single_df_table',
    python_callable=create_single_df_table,
    provide_context=True,  # Pass the output of the previous task as an argument
    dag=dag,
)

task_create_collection_df_table = PythonOperator(
    task_id='create_collection_df_table',
    python_callable=create_collection_df_table,
    provide_context=True,  # Pass the output of the previous task as an argument
    dag=dag,
)

"""setting up dependencies which task must be executed before the second task we have total of four tasks which depend on each other"""
task_extract_and_process >> task_slice_dataframes
task_slice_dataframes >> task_create_single_df_table
task_slice_dataframes >> task_create_collection_df_table
# Adding dbt task
task_create_collection_df_table >> task_dbt_cleaning
