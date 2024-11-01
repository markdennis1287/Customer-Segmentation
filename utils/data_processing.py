# utils/data_processing.py
import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(data):
    # Drop any irrelevant or missing columns
    data = data.dropna()
    # Assuming relevant columns are 'age', 'income', 'spending_score', etc.
    features = ['age', 'income', 'spending_score']
    data = data[features]

    # Scale the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    return scaled_data
