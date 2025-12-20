from googleapiclient.discovery import build
from services.auth_service import get_user_credentials

def add_event_to_calendar(user_id: int, event_data: dict):
    """
    מקבל ID של משתמש ונתונים של אירוע (מה-AI),
    ומוסיף ליומן של המשתמש.
    """
    # 1. השגת אישור גישה ספציפי למשתמש הזה
    creds = get_user_credentials(user_id)
    
    if not creds:
        return False, "User not authenticated. Please run /start again."
        
    try:
        # 2. בניית השירות של גוגל
        service = build('calendar', 'v3', credentials=creds)
        
        # 3. הוספת האירוע
        event = service.events().insert(
            calendarId='primary', # היומן הראשי של המשתמש
            body=event_data
        ).execute()
        
        # החזרת הלינק לאירוע שנוצר
        return True, event.get('htmlLink')
        
    except Exception as e:
        print(f"Error adding event to Google Calendar: {e}")
        return False, str(e)