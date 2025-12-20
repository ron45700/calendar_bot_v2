from config import settings
from .interface import DatabaseManager
from .firestore_manager import FirestoreManager

_db_instance = None

def get_database_manager() -> DatabaseManager:
    global _db_instance
    if _db_instance:
        return _db_instance

    # Always use Firestore (or dummy mode inside it)
    _db_instance = FirestoreManager(
        use_dummy=False, 
        credentials_path=settings.FIRESTORE_CREDENTIALS_PATH
    )

    return _db_instance
