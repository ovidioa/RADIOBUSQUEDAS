import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_babel import Babel, get_locale

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure Babel
app.config['LANGUAGES'] = {
    'es': 'Español',
    'ca': 'Català'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Initialize extensions
db.init_app(app)
babel = Babel(app)

@babel.locale_selector_function
def get_locale():
    # 1. URL parameter has priority
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
    # 2. Use session language
    if 'language' in session and session['language'] in app.config['LANGUAGES'].keys():
        return session['language']
    # 3. Default to Spanish
    return 'es'

# Import routes and models
from routes import *
from models import *

with app.app_context():
    db.create_all()
