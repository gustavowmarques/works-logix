"""
config.py - Configuration file for Works Logix Flask application.
Defines environment variables and default settings used throughout the app.
"""

import os

class Config:
    """
    Main configuration class with default settings.
    These values are accessed using app.config['...'] throughout the app.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey') # Secret key for session encryption
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/worklogix.db') # Default DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disable modification tracking to save resources
