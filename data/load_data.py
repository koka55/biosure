'''
Loading Data (from csv files)
'''

import pandas as pd
from glob import glob

def data_load(folder_path):
    # Get a list of all CSV files in a directory
    csv_files = glob(folder_path, '*.csv')

    # Create an empty dataframe to store the combined data
    data = pd.DataFrame()

    # Loop through each CSV file and append its contents to the combined dataframe
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        data = pd.concat([data, df])

    return data
    # Print the combined dataframe
