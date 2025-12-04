import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from sqlmodel import Session
from database.connection import engine
from database.models import User
from dotenv import load_dotenv

load_dotenv()

# הגדרות קבועות
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # קורא את הכתובת הקבועה מה-.env

def create_flow():
    """
    יוצר אובייקט Flow של גוגל.
    קורא את כל הנתונים (כולל ה-Redirect URI) ישירות ממשתני הסביבה.
    """
    return Flow.from_client_config(
        {
            "installed": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
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
    אנחנו מעבירים את ה-ID של המשתמש בתוך ה-state כדי שנדע לזהות אותו בחזור.
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
    פונקציה שתשמש את השרת (בשלב הבא).
    מקבלת את אובייקט ה-Flow אחרי שגוגל אישרו אותו, ושומרת ל-DB.
    """
    try:
        creds = flow.credentials
        creds_json = creds.to_json()
        
        with Session(engine) as session:
            user = session.get(User, telegram_id)
            if not user:
                # משתמש חדש
                user = User(telegram_id=telegram_id, google_token_data=creds_json)
                session.add(user)
            else:
                # משתמש קיים - מעדכנים טוקן
                user.google_token_data = creds_json
                session.add(user)
            
            session.commit()
            print(f"User {telegram_id} connected successfully.")
            return True
    except Exception as e:
        print(f"Error saving token: {e}")
        return False

def get_user_credentials(telegram_id: int):
    """שולף את הטוקן לשימוש שוטף (הוספת אירועים וכו')"""
    with Session(engine) as session:
        user = session.get(User, telegram_id)
        if user and user.google_token_data:
            return Credentials.from_authorized_user_info(
                json.loads(user.google_token_data), SCOPES
            )
    return None