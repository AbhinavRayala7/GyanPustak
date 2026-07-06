import os

class Config:
    # Flask Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gyan_pustak_secret_key_12345'
    
    # Database Settings
    # Primary: Microsoft SQL Server connection string
    # Driver: ODBC Driver 17 for SQL Server or ODBC Driver 18 for SQL Server
    SQL_SERVER_CONN = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost;"
        "Database=GyanPustak;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    
    # Secondary: SQLite Database Path (Fallback)
    # This ensures the project runs out-of-the-box without requiring SQL Server setup.
    SQLITE_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'gyanpustak.db')
    
    # Session lifetime (30 minutes)
    PERMANENT_SESSION_LIFETIME = 1800
    
    # Upload folder for profile pictures
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2MB limit
