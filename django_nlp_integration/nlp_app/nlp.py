import os
import re
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.chat.util import reflections

# Set the NLTK data path
nltk_data_path = os.path.join(os.path.dirname(__file__), 'data', 'nltk_data')
nltk.data.path.append(nltk_data_path)

# Ensure necessary NLTK data files are downloaded
'''try:
    nltk.download('punkt', download_dir=nltk_data_path)
    nltk.download('stopwords', download_dir=nltk_data_path)
except Exception as e:
    print(f"Error downloading NLTK data: {e}")'''

# Function to preprocess user input text
def preprocess_text(user_input):
    tokens = word_tokenize(user_input)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

# Function to extract features from tokens
def extract_features(tokens):
    feature_dict = {col: 0 for col in numeric_features + categorical_features}

    # Mapping tokens to features
    '''for token in tokens:
        if re.match(r'\d{4}', token):  # Extract year
            feature_dict['studyYear'] = int(token)
        if token == 'cassava':
            feature_dict['programName'] = 'Cassava Program'
        if token in ['plot', 'width']:
            feature_dict['plotWidth'] = 5.0  # Example value
        if token in ['plot', 'length']:
            feature_dict['plotLength'] = 10.0  # Example value
        if token == 'field':
            feature_dict['fieldSize'] = 1.0  # Example value
        if token == 'genotyped':
            feature_dict['fieldTrialIsPlannedToBeGenotyped'] = 1
        if token == 'cross':
            feature_dict['fieldTrialIsPlannedToCross'] = 1'''

    return feature_dict

# Load the trained model pipeline
base_dir = os.path.dirname(__file__)
model_file = os.path.join(base_dir, 'data', 'random_forest_model.pkl')

# Check if the model file exists
if os.path.exists(model_file):
    # Load the trained model pipeline
    model_pipeline = joblib.load(model_file)

    # Extract feature names from the preprocessor
    numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
    categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]

    # Ensure they are lists
    numeric_features = list(numeric_features) if not isinstance(numeric_features, list) else numeric_features
    categorical_features = list(categorical_features) if not isinstance(categorical_features, list) else categorical_features

    # Function to predict from user input text
    def predict_from_text(user_input):
        features = {key: value for key, value in user_input.items()}
        new_data = pd.DataFrame([features])

        # Ensure all required columns are present in the new data
        for col in numeric_features + categorical_features:
            if col not in new_data.columns:
                new_data[col] = 0  # Fill with default value, adjust as necessary

        # Preprocess the new data using the same pipeline
        new_data_preprocessed = model_pipeline.named_steps['preprocessor'].transform(new_data)

        # Make predictions on the new data
        new_predictions = model_pipeline.named_steps['regressor'].predict(new_data_preprocessed)

        return new_predictions

    # Function to generate reflection using NLTK
    def reflect_prediction(predictions):
        response = f"The predicted values are {predictions}. Based on these values, it can be inferred that {reflections['you']} should consider the following actions."
        return response

else:
    print("Model file not found. Ensure the model is trained and saved correctly.")
