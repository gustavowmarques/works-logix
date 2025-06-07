"""
run.py - Entry point for the Works Logix Flask application.
This file initializes and runs the Flask application using the create_app factory.
"""
from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env before app starts

# Import the Flask application factory function from the app package
from app import create_app

# Call the factory to create the app instance
app = create_app()

print("Connected to:", app.config['SQLALCHEMY_DATABASE_URI'])

# Only run the app if this script is executed directly
if __name__ == '__main__':
    # Start the development server
    app.run(debug=True)
