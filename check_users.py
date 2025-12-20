from sqlmodel import Session, select
from database.connection import engine
from database.models import User

def check_who_is_connected():
    with Session(engine) as session:
        # שליפת כל המשתמשים מהטבלה
        statement = select(User)
        results = session.exec(statement).all()
        
        print(f"\n--- Found {len(results)} users in database ---")
        
        for user in results:
            # בדיקה האם יש להם טוקן שמור
            has_token = "✅ Yes" if user.google_token_data else "❌ No"
            print(f"User ID: {user.telegram_id} | Connected to Google: {has_token}")
            
        print("----------------------------------------\n")

if __name__ == "__main__":
    check_who_is_connected()