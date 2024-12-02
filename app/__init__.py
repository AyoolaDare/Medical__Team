from flask import Flask, redirect, url_for
import os
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()

# Initialize extensions without app context
mongo = PyMongo()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')))
    app.config.from_object(config_class)

    # Initialize extensions with app context
    mongo.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    from app.admin import bp as admin_bp
    from app.patient import bp as patient_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(patient_bp, url_prefix='/patient')

    # Add a root route
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app