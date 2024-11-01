# models/segmentation_model.py
from sklearn.cluster import KMeans
import pandas as pd

class KMeansSegmentation:
    def __init__(self, n_clusters=4):
        self.model = KMeans(n_clusters=n_clusters, random_state=42)

    def segment(self, data):
        self.model.fit(data)
        labels = self.model.predict(data)
        clusters = self.model.cluster_centers_
        return clusters, labels
