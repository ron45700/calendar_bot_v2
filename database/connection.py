from sqlmodel import SQLModel, create_engine
import os

# שם הקובץ שיווצר לך בתיקייה הראשית
SQLITE_FILE_NAME = "bot_database.db"
# מחרוזת החיבור (כאן נשנה בעתיד אם תעבור לענן)
DATABASE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

# יצירת המנוע שמדבר עם הדאטה-בייס
engine = create_engine(DATABASE_URL)

def init_db():
    """
    פונקציה זו רצה בהתחלה ויוצרת את כל הטבלאות המוגדרות
    בקובץ models.py אם הן לא קיימות
    """
    # חשוב לייבא את המודלים כדי ש-SQLModel יכיר אותם לפני היצירה
    from .models import User
    
    print("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    print("Database initialized successfully!")