from dotenv import load_dotenv
load_dotenv()  # Loads environment variables from .env before app starts

from app import create_app

app = create_app()

print("Connected to:", app.config['SQLALCHEMY_DATABASE_URI'])

if __name__ == '__main__':
    app.run(debug=True)
