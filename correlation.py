# Here's the updated code to handle multiple CSV files from the same folder and calculate the correlation matrix for the combined dataset.

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Loading the dataset from the extracted folder
data_folder = '/content/drive/MyDrive/extracted_features'

# List all CSV files in the directory
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

# Load and concatenate all CSV files into a single DataFrame
dfs = []
for file in csv_files:
    file_path = os.path.join(data_folder, file)
    df = pd.read_csv(file_path)
    dfs.append(df)

# Concatenate all the dataframes
combined_df = pd.concat(dfs, ignore_index=True)

# Display first few rows to ensure it's loaded correctly
combined_df.head()

# Correlation analysis between features for the combined dataset
correlation_matrix = combined_df.corr()

# Plotting the correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix for Features Across Multiple Files')
plt.show()