from flask import Flask, redirect, url_for
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')))
    app.config.from_object(config_class)

    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', 
                              region_name=app.config['AWS_REGION'],
                              aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

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

