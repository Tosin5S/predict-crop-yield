from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
from .models import YieldData

def predict_yield():
	# Load the data
	data = YieldData.objects.all()
	df = pd.DataFrame(data)

	# Split the data into training and testing sets
	X = df.drop('dryYield', axis=1)
	y = df['dryYield']
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

	# Train a random forest regressor
	model = RandomForestRegressor(n_estimators=100, random_state=42)
	model.fit(X_train, y_train)

	return model