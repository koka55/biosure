# import pandas as pd
# from glob import glob

# # Get a list of all CSV files in a directory
# csv_files = glob('extracted_features/*.csv')

# # Create an empty dataframe to store the combined data
# data = pd.DataFrame()

# # Loop through each CSV file and append its contents to the combined dataframe
# for csv_file in csv_files:
#     df = pd.read_csv(csv_file)
#     data = pd.concat([data, df])

# # Print the combined dataframe
