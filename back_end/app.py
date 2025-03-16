import pickle
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import xgboost as xgb
import lightgbm as lgb

app = Flask(__name__)
CORS(app) 

with open('models/xgboost_model.pkl', 'rb') as f:
    xgb_model = pickle.load(f)

with open('models/lgb_model.pkl', 'rb') as f:
    lgb_model = pickle.load(f)

encoder = LabelEncoder()

def preprocess_data(df):

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['weekday'] = df['date'].dt.weekday
    df['year'] = df['date'].dt.year
    df['day'] = df['date'].dt.day

    df['is_weekend'] = df['weekday'].apply(lambda x: 1 if x >= 5 else 0)
    df.drop(columns=['date'], inplace=True)
    
    df['country'] = encoder.fit_transform(df['country'])
    df['store'] = encoder.fit_transform(df['store'])
    df['product'] = encoder.fit_transform(df['product'])

    df['sales_lag_1'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(1)
    df['sales_lag_7'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(7)
    df['sales_lag_30'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(30)
    df['sales_lag_3'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(3)
    df['sales_lag_14'] = df.groupby(['country', 'store', 'product'])['num_sold'].shift(14)

    df['rolling_avg_7'] = df.groupby(['country', 'store', 'product'])['num_sold'].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df['rolling_avg_30'] = df.groupby(['country', 'store', 'product'])['num_sold'].transform(lambda x: x.rolling(30, min_periods=1).mean())

    df.fillna(0, inplace=True)

    return df

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if isinstance(data, list):
            input_data = pd.DataFrame(data)
        else:
            input_data = pd.DataFrame([data])

        input_data = preprocess_data(input_data)
        if 'num_sold' in input_data.columns:
            input_data = input_data.drop(columns=['num_sold'])
        else:
            return jsonify({"error": "error"})

        X_input = input_data

        xgb_predictions = xgb_model.predict(X_input)
        lgb_predictions = lgb_model.predict(X_input)

        blended_predictions = (xgb_predictions * 0.5) + (lgb_predictions * 0.5)

        return jsonify({'predictions': blended_predictions.tolist()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)