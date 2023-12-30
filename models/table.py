from sqlalchemy import create_engine
import pandas as pd


class CreateTable:
    def __init__(self, single_df, collection_of_dfs):
        self.single_df = single_df
        self.collection_of_dfs = collection_of_dfs
    #reading the db credentials from pass.txt which contain username, password and databasename consecutively
    def read_db_credentials(self, file_path='pass.txt'):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            username = lines[0].strip()
            password = lines[1].strip()
            database_name = lines[2].strip()

        return username, password, database_name

    def table_single_df(self):
        username, password, database_name = self.read_db_credentials()
        engine = create_engine(f'postgresql://{username}:{password}@localhost:5432/{database_name}', echo=True)
        self.single_df.to_sql('single_table', con=engine, if_exists='append', index=False)
        print("The first DataFrame is loaded to the first table in the database we created.")
   
   
    #creating tables for each time-series DataFrames we created.
    def table_collection_dfs(self):
        username, password, database_name = self.read_db_credentials()
        engine = create_engine(f'postgresql://{username}:{password}@localhost:5432/{database_name}', echo=True)

        for i, df in enumerate(self.collection_of_dfs):
            if isinstance(df, pd.DataFrame):
                df.to_sql(f'table_{i}', con=engine, if_exists='append', index=False)
                print(f'Table created from DataFrame {i} in "{database_name}" database.')
            else:
                print(f'Unsupported type: {type(df)}')
    def remove_nan_rows(self):
    if not self.collection_of_tables:
        logging.warning("No tables to process. Run 'table_collection_dfs' first.")
        return

    with self.engine.connect() as connection:
        for i, table in enumerate(self.collection_of_tables):
            table_name = f'table_{i}'

            # Generate a list of SQL commands to remove rows with all zero values in each column
            sql_commands = [
                f"DELETE FROM {table_name} WHERE NOT EXISTS (SELECT 1 FROM {table_name} WHERE {col} != 0)"
                for col in table.columns
            ]

            # Execute the generated SQL commands
            for sql_command in sql_commands:
                connection.execute(sql_command)

            logging.info(f"Removed rows with all zero values from {table_name}.")
