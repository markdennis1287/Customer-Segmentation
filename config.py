# config.py
import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
    SECRET_KEY = os.urandom(24)
