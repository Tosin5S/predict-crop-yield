# Import libraries
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Read the data
data = pd.read_excel("/content/drive/MyDrive/Yield/2020-04-07t102422phenotype_download.xlsx", usecols=[17, 51, 56])

# Separate the features and the target
X = data.drop("cassava mosaic disease severity 6-month evaluation|CO_334:0000194", axis=1)
y = data["fresh root yield|CO_334:0000013"]

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and fit a random forest regressor
rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf.predict(X_test)

# Evaluate the model performance
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"Mean Squared Error: {mse:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f}")

# Getting the value of target_range
target_max = data["fresh root yield|CO_334:0000013"].max()
target_min = data["fresh root yield|CO_334:0000013"].min()
target_range = target_max - target_min
print(f"Target Range: {target_range:.2f}")

# Calculate the percentage accuracy of my model
percentage_accuracy = (1 - (rmse / target_range)) * 100
print(f"Percentage Accuracy: {percentage_accuracy:.2f}%")

print(data.columns)

# Create a new DataFrame with the same columns as the original dataset
new_df = pd.DataFrame(columns=X.columns)

# Assign some values to the features
new_df.loc["cassava mosaic disease severity 6-month evaluation|CO_334:0000194"] = 0.5

# Display the new DataFrame
new_df

# Make predictions
predictions = rf.predict(new_df)

# Display the predictions
predictions
