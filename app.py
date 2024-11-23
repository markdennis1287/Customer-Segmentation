# app.py
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from models.segmentation_model import KMeansSegmentation
from utils.data_processing import preprocess_data
from utils.plotting import create_segment_plots

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read data based on file extension
        if filename.endswith('.csv'):
            data = pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            data = pd.read_excel(filepath)
        
        # Preprocess data
        preprocessed_data = preprocess_data(data)

        # Apply K-means clustering
        model = KMeansSegmentation()
        clusters, labels = model.segment(preprocessed_data)

        # Create plots
        plots = create_segment_plots(preprocessed_data, labels)
        
        return render_template('results.html', plots=plots, clusters=clusters)

    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
