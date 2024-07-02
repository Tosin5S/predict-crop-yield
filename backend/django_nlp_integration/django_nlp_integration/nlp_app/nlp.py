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

# Set the NLTK data path
nltk_data_path = os.path.join(os.path.dirname(__file__), 'data', 'nltk_data')
nltk.data.path.append(nltk_data_path)

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
    for token in tokens:
        if re.match(r'\d{4}', token):  # Extract year
            feature_dict['studyYear'] = int(token)
        if token == 'cassava':
            feature_dict['programName'] = 'Cassava Program'
        if token == 'maize':
            feature_dict['programName'] = 'Maize Program'
        if token == 'wheat':
            feature_dict['programName'] = 'Wheat Program'
        if token in ['plot', 'width']:
            feature_dict['plotWidth'] = 5.0  # Example value
        if token in ['plot', 'length']:
            feature_dict['plotLength'] = 10.0  # Example value
        if token == 'field':
            feature_dict['fieldSize'] = 1.0  # Example value
        if token == 'genotyped':
            feature_dict['fieldTrialIsPlannedToBeGenotyped'] = 1
        if token == 'cross':
            feature_dict['fieldTrialIsPlannedToCross'] = 1
        if token == 'location':
            feature_dict['locationName'] = 'Default Location'
        if token == 'germplasm':
            feature_dict['germplasmName'] = 'Default Germplasm'
        if token == 'replicate':
            feature_dict['replicate'] = 1  # Example value
        if token == 'block':
            feature_dict['blockNumber'] = 1  # Example value
        if token == 'plot':
            feature_dict['plotNumber'] = 1  # Example value
        if token == 'row':
            feature_dict['rowNumber'] = 1  # Example value
        if token == 'harvest':
            feature_dict['harvestDate'] = '2024-01-01'  # Example value
        if token == 'planting':
            feature_dict['plantingDate'] = '2023-01-01'  # Example value
        if token == 'programId':
            feature_dict['programDbId'] = 1  # Example value
        if token == 'studyId':
            feature_dict['studyDbId'] = 1  # Example value
        if token == 'observationUnitId':
            feature_dict['observationUnitDbId'] = 1  # Example value
        if token == 'synonyms':
            feature_dict['germplasmSynonyms'] = 1  # Example value
        if token == 'description':
            feature_dict['programDescription'] = 'Default Description'
            feature_dict['studyDescription'] = 'Default Description'
        if token == 'study':
            feature_dict['studyName'] = 'Default Study'
        if token == 'design':
            feature_dict['studyDesign'] = 'Default Design'
        if token == 'observation':
            feature_dict['observationLevel'] = 'Default Level'
            feature_dict['observationUnitName'] = 'Default Unit'
        if token == 'entry':
            feature_dict['entryType'] = 'Default Type'

    return feature_dict

# Construct the path to the model file
base_dir = os.path.dirname(__file__)
model_file = os.path.join(base_dir, 'data', 'random_forest_model.pkl')

# Check if the model file exists
if os.path.exists(model_file):
    # Load the trained model pipeline
    model_pipeline = joblib.load(model_file)

    # Inspect the pipeline steps to find the correct name for the final step
    print(model_pipeline.named_steps)

    # Extract feature names from the preprocessor
    numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
    categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]

    # Ensure they are lists
    numeric_features = list(numeric_features) if not isinstance(numeric_features, list) else numeric_features
    categorical_features = list(categorical_features) if not isinstance(categorical_features, list) else categorical_features

    # Function to predict from user input text
    def predict_from_text(user_input):
        tokens = preprocess_text(user_input)
        features = extract_features(tokens)
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

    # Example usage
    # user_input = "Predict the yield for year 2024 in the Cassava Program."
    # predictions = predict_from_text(user_input)
    # print("Predictions on new data:", predictions)

else:
    print("Model file not found. Please ensure 'random_forest_model.pkl' is located in the './data/' directory.")
