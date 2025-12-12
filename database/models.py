from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class User(SQLModel, table=True):
    # ה-ID של המשתמש בטלגרם (ייחודי ומשמש כמפתח ראשי)
    telegram_id: int = Field(primary_key=True)
    
    # שם המשתמש בטלגרם (לנוחות תצוגה בלוגים)
    username: Optional[str] = None
    
    # תאריך ההצטרפות לבוט
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # המידע הרגיש מגוגל (Access Token, Refresh Token) יישמר כטקסט ארוך (JSON string)
    # אם זה ריק (None), סימן שהמשתמש עדיין לא התחבר לגוגל
    google_token_data: Optional[str] = None

    # שם החיבה שנתן המשתמש לבוט (ברירת מחדל: CalendarBot)
    bot_nickname: Optional[str] = Field(default="נהוראי")

    # העדפות צבעים של המשתמש (JSON string)
    # מבנה: { "Sports": 5, "Work": 9, ... }
    color_preferences: Optional[str] = None
    
    # הגדרות משתמש (נכין את הקרקע לעתיד)
    # למשל: האם הוא רוצה תזכורות קוליות? כרגע נשאיר פשוט