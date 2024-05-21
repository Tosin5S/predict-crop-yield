import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import os

class RandomForestRegressorWrapper:
    def __init__(self):
        # Get the root directory of the project
        root_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the file
        file_path = os.path.join(root_dir, '2020-04-07t102422phenotype_download.xlsx')

        # Read the data
        data = pd.read_excel(file_path, usecols=[51, 56])

        # Separate the features and the target
        X = data.drop("cassava mosaic disease severity 6-month evaluation|CO_334:0000194", axis=1)  # Corrected column name
        y = data["fresh root yield|CO_334:0000013"]

        # Split the data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create and fit a random forest regressor
        self.rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.rf.fit(X_train, y_train)

        self.X = X

        # Make predictions on the test set
        y_pred = self.rf.predict(X_test)



    def get_X(self):
        return self.X
    
    def predict(self, new_df):
        # Make predictions on the new data
        y_pred = self.rf.predict(new_df)
        
        return y_pred