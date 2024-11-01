# utils/plotting.py
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_segment_plots(data, labels):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=data[:, 0], y=data[:, 1], hue=labels, palette='viridis')
    plt.title("Customer Segmentation")
    plt.xlabel("Age")
    plt.ylabel("Spending Score")
    plot_path = os.path.join('static', 'segment_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path
