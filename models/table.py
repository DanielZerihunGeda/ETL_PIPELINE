from Process import ProcessData
from sqlalchemy import create_engine
import pandas as pd

def load_data_to_postgres(csv_file, data_address): # specify the db adress such as 'postgresql://postgres:123@localhost:5432/swarm'
    data_processor = ProcessData(csv_file)
    result = data_processor.slice_dataframes()

    engine = create_engine(data_address)

    for i, df in enumerate(result):
        table_name = f'Table_{i}'
        df.to_sql(table_name, engine, index=False, if_exists='replace')

    print("All Dataframes are loaded into PostgreSQL database successfully!!!")


csv_file_path = 'swarm_drone.csv'
postgres_url = 'postgresql://postgres:123@localhost:5432/swarm'

load_data_to_postgres(csv_file_path, postgres_url)
