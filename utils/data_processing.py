# utils/data_processing.py
import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(data):
    # Filter relevant columns for segmentation
    data = data[['CustomerID', 'Quantity', 'UnitPrice']].dropna()  # Adjust based on dataset structure
    
    # Aggregate data by CustomerID
    data = data.groupby('CustomerID').agg({
        'Quantity': 'sum',
        'UnitPrice': 'mean'  # Average spending per customer
    }).reset_index()

    # Feature scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data[['Quantity', 'UnitPrice']])
    
    return scaled_data
