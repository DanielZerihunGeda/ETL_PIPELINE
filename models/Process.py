import pandas as pd
import csv
import numpy as np

class ProcessData:
    
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = None
        self.csv = None
    """Spliting the data into two
    1. column which are not time series attributes

    2. columns which are time series(time-tracking) 
    """
    def extract_first_four_columns(self): #method to extract the first 4 column since they are not change through out the row
        self.data = pd.read_csv(self.csv_file, delimiter=';', usecols=range(4), header=None, skiprows=1)
        column_name = ['track_id', 'type', 'traveled_d', 'avg_speed']
        self.data.columns = column_name
        return self.data
    
    def extract_data(self, delimiter=';', skip_rows=1):   #Reading 
        self.csv = []
        with open(self.csv_file, 'r') as file:
            csv_reader = csv.reader(file, delimiter=delimiter)
            for _ in range(skip_rows):
                next(csv_reader)
            for row in csv_reader:
                values_from_4th_column = row[4:]
                self.csv.append(values_from_4th_column)
        return self.csv
    
    def slice_dataframes(self):
        if self.data is None:
            self.extract_first_four_columns()

        if self.csv is None:
            self.extract_data()

        # Find the maximum number of columns among rows
        max_cols = max(len(row) for row in self.csv)
        
        # Iterate through rows, imputing shorter rows with NaN to match max_cols
        for row in self.csv:
            if len(row) < max_cols:
                row.extend([np.nan] * (max_cols - len(row)))

        num_dfs = (max_cols + 5) // 6
        result_dfs = []

        for row in self.csv:
            sliced_row = [
                row[i * 6: (i + 1) * 6] if len(row) >= (i + 1) * 6 else row[i * 6:] + [np.nan] * (6 - len(row[i * 6:])) for i in range(num_dfs)
            ]
            sliced_df = pd.DataFrame(sliced_row, columns=['lat', 'lon', 'speed', 'lon_acc', 'lat_acc', 'time'])
            result_dfs.append(sliced_df)

        return result_dfs
