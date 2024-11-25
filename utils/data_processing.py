# utils/data_processing.py
import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(data):
    data = data[['CustomerID', 'Quantity', 'UnitPrice']].dropna()
    
    data = data.groupby('CustomerID').agg({
        'Quantity': 'sum',
        'UnitPrice': 'mean'
    }).reset_index()

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data[['Quantity', 'UnitPrice']])
    
    return scaled_data
