import pickle
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import xgboost as xgb
import lightgbm as lgb

app = Flask(__name__)

# Load the trained models (ensure they are in the 'models' folder)
with open('models/xgboost_model.pkl', 'rb') as f:
    xgb_model = pickle.load(f)

with open('models/lgb_model.pkl', 'rb') as f:
    lgb_model = pickle.load(f)

# Initialize the LabelEncoder
encoder = LabelEncoder()

# Preprocessing function
def preprocess_data(df):
    # Convert 'date' to datetime and extract features (year, month, day, weekday)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday
    df['is_weekend'] = df['weekday'].apply(lambda x: 1 if x >= 5 else 0)  # Weekend=1, Weekday=0
    df.drop(columns=['date'], inplace=True)  # Drop the original 'date' column
    
    # Encode categorical columns using Label Encoding
    df['country'] = encoder.fit_transform(df['country'])
    df['store'] = encoder.fit_transform(df['store'])
    df['product'] = encoder.fit_transform(df['product'])

    # Lag Features: Previous sales trends
    df['sales_lag_1'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(1)
    df['sales_lag_7'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(7)
    df['sales_lag_30'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(30)
    df['sales_lag_3'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(3)
    df['sales_lag_14'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(14)

    # Rolling averages
    df['rolling_avg_7'] = df.groupby(['country', 'store', 'product'])['num_sold'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df['rolling_avg_30'] = df.groupby(['country', 'store', 'product'])['num_sold'].transform(lambda x: x.rolling(30, min_periods=1).mean())

    # Fill missing values with 0
    df.fillna(0, inplace=True)

    return df

# Define a route to make predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the request (it should be in JSON format)
        data = request.get_json()

        # Convert the data into a pandas DataFrame
        input_data = pd.DataFrame(data)

        # Ensure that 'num_sold' column (target) is not included in the input data
        if 'num_sold' in input_data.columns:
            input_data = input_data.drop(columns=['num_sold'])

        # Preprocess the input data (excluding 'num_sold')
        input_data = preprocess_data(input_data)

        # Separate features (X) from target (y) for prediction
        X_input = input_data  # Only features are needed for prediction

        # Make predictions using both XGBoost and LightGBM models
        xgb_predictions = xgb_model.predict(X_input)
        lgb_predictions = lgb_model.predict(X_input)

        # Blend the predictions (50% from each model)
        blended_predictions = (xgb_predictions * 0.5) + (lgb_predictions * 0.5)

        # Return the predictions as JSON
        return jsonify({'predictions': blended_predictions.tolist()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)