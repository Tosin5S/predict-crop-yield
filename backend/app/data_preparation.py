import pandas as pd

datasets = []

# Loop through each year
for year in range(2010, 2017):
	df = pd.read_csv(f'{year}.csv')
	datasets.append(df)

# Concatenate the datasets
train_df = pd.concat(datasets, ignore_index=True)
