import os
from dotenv import load_dotenv

# Load environment variables explicitly
load_dotenv()

class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
        self.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite") # sqlite, firestore
        self.FIRESTORE_CREDENTIALS_PATH = os.getenv("FIRESTORE_CREDENTIALS_PATH")
        
        # Validation
        missing_vars = []
        if not self.TELEGRAM_BOT_TOKEN:
            missing_vars.append("TELEGRAM_BOT_TOKEN")
        
        # Only strict check google auth if actually needed or maybe warn?
        # For now, we'll just log/print warnings if critical things are missing
        if missing_vars:
            print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")

settings = Settings()
