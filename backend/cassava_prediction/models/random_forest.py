import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Load data
# features = pd.read_csv("data/processed/cassava_features.csv")
# target = pd.read_csv("data/processed/cassava_target.csv")

# Assuming the dataset is stored in a variable called 'data'
x = data.drop(['YieldColumn'], axis=1)
y = data['YieldColumn']

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.2, random_state = 42)

# Initialize Random Forest model
rf_model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
rf_model.fit(x_train, y_train)

