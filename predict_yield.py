# Import necessary libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

# Load the dataset
dataset_path = "path/to/your/dataset.csv"  # Replace with the actual path
data = pd.read_csv(dataset_path)

# Define features (independent variables) and target variable
features = data[['Climate and Weather', 'Soil Quality', 'Water Management', 'Pest and Disease Control', 'Fertilization', 'Genetics']]
target = data['Maize Yield']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Initialize the Random Forest Regressor model
model = RandomForestRegressor()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
predictions = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, predictions)
print(f"Mean Squared Error: {mse}")

# Save the trained model
model_filename = "maize_yield_prediction_model.joblib"
joblib.dump(model, model_filename)
print(f"Model saved as {model_filename}")
