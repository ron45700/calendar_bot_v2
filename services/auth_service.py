import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from config import settings
from database import get_database_manager, User

# הגדרות קבועות
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Use settings for URI
REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

def create_flow():
    """
    יוצר אובייקט Flow של גוגל.
    """
    return Flow.from_client_config(
        {
            "installed": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI] 
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def get_authorization_url(telegram_id: int):
    """
    מייצר את הלינק שהמשתמש יקבל בטלגרם.
    """
    flow = create_flow()
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=str(telegram_id), 
        prompt='consent'
    )
    return auth_url

def save_user_token_from_flow(flow, telegram_id: int):
    """
    מקבלת את אובייקט ה-Flow אחרי שגוגל אישרו אותו, ושומרת ל-DB.
    """
    try:
        creds = flow.credentials
        creds_json = creds.to_json()
        
        db = get_database_manager()
        user = db.get_user(telegram_id)
        
        if not user:
            # משתמש חדש
            user = User(telegram_id=telegram_id)
        
        # עדכון הטוקן
        user.google_token_data = creds_json
        # עדכון סטטוס אם צריך (למשל, עכשיו הוא מחובר)
        user.status = "connected" 

        if db.save_user(user):
            print(f"User {telegram_id} connected successfully.")
            return True
        else:
            print(f"Failed to save user {telegram_id}.")
            return False

    except Exception as e:
        print(f"Error saving token: {e}")
        return False

def get_user_credentials(telegram_id: int):
    """שולף את הטוקן לשימוש שוטף"""
    db = get_database_manager()
    user = db.get_user(telegram_id)
    
    if user and user.google_token_data:
        return Credentials.from_authorized_user_info(
            json.loads(user.google_token_data), SCOPES
        )
    return None