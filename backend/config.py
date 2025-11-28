import os
from dotenv import load_dotenv
import urllib.parse

# Load .env explicitly from backend folder
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_SERVER = os.getenv('DB_SERVER')
DB_NAME = os.getenv('DB_NAME')

PASSWORD_ENCODED = urllib.parse.quote_plus(DB_PASSWORD)

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{PASSWORD_ENCODED}@{DB_SERVER}/{DB_NAME}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    MAX_FEEDBACK_LENGTH = 5000
    SENTIMENT_THRESHOLD = 0.6

print("Loaded DB user:", DB_USER)
print("Connection string:", Config.SQLALCHEMY_DATABASE_URI)
