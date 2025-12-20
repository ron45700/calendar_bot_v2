import sys
import os
from datetime import datetime

# Ensure valid path import
sys.path.append(os.getcwd())

from config import settings
from database import get_database_manager, User, Task

def verify():
    print("--- Verification Start ---")
    try:
        print("1. Settings loaded successfully.")
        
        db = get_database_manager()
        print(f"2. Database Manager initialized: {type(db).__name__}")
        
        db.init_db()
        print("3. Database init_db() called successfully.")
        
        # Verify persistence models
        t = Task(user_id=123, description="Test", check_in_time=datetime.now())
        print(f"4. Task model created: {t}")
        
        if db.save_task(t):
             print("5. Task save simulated (or executed) successfully.")
        
        print("--- Verification Passed ---")
    except Exception as e:
        print(f"--- Verification FAILED: {e} ---")
        raise e

if __name__ == "__main__":
    verify()
