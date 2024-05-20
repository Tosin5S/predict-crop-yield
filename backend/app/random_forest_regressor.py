import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import os

# Get the root directory of the project
root_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the file
file_path = os.path.join(root_dir, '2020-04-07t102422phenotype_download.xlsx')

# Read the data
data = pd.read_excel(file_path, usecols=[17, 51, 56])

# Separate the features and the target
X = data.drop("cassava mosaic disease severity 6-month evaluation|CO_334:0000194", axis=1)
y = data["fresh root yield|CO_334:0000013"]

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and fit a random forest regressor
rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf.fit(X_train, y_train)

def predict(new_df):
    # Convert the new_df instance to a pandas DataFrame
    new_df = pd.DataFrame([new_df.__dict__])
    
    # Make predictions on the new data
    y_pred = rf.predict(new_df)
    
    return y_pred