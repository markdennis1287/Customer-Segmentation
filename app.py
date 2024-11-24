# app.py
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import pandas as pd
from models.segmentation_model import KMeansSegmentation
from secrets import token_urlsafe
from utils.data_processing import preprocess_data
from utils.plotting import create_segment_plots

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx'}
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
Session(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


app.secret_key = '441e55d9425ac05da35b5e51b07c162328a66c905fcfa28c3d8abc5cdb632162'

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='GOOGLE_CLIENT_ID',
    client_secret='GOOGLE_CLIENT_SECRET',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://openidconnect.googleapis.com/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    },
)

@app.route('/')
def index():
    user_email = session.get('user_email')
    return render_template('index.html', user_email=user_email)

@app.route('/login')
def login():
    nonce = token_urlsafe(16)
    state = token_urlsafe(16)
    session['nonce'] = nonce
    session['state'] = state
    print(f"Generated nonce: {nonce}")
    print(f"Generated state: {state}")
    
    return google.authorize_redirect(
        url_for('authorized', _external=True),
        state=state
    )

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

@app.route('/google/callback')
def authorized():
    try:
        received_state = request.args.get('state')
        stored_state = session.pop('state', None)
        print(f"Stored state: {stored_state}")
        print(f"Received state: {received_state}")

        if stored_state != received_state:
            raise ValueError("State parameter mismatch")

        token = google.authorize_access_token()
        print(f"Access token: {token}")

        nonce = session.pop('nonce', None)
        if not nonce:
            raise ValueError("Missing nonce in session")

        id_token = token.get('id_token')
        print(f"ID token: {id_token}")
        if not id_token:
            raise ValueError("Missing ID token in response")

        # First try parsing the id_token
        user_info = google.parse_id_token(id_token, nonce=nonce)
        print(f"User info from ID token: {user_info}")

        # Fallback to userinfo endpoint if email is missing
        if not user_info or 'email' not in user_info:
            user_info = google.get('userinfo').json()
            print(f"User info from endpoint: {user_info}")

        if not user_info or 'email' not in user_info:
            raise ValueError("User info is invalid or missing email")

        session['user_email'] = user_info['email']
        return redirect(url_for('index'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Authentication failed: {e}", 500


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
    app.run(host='0.0.0.0', port=port, debug=True)
