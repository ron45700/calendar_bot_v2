import os
from flask import Flask, request
from services.auth_service import create_flow, save_user_token_from_flow
from database.connection import init_db

import requests

# הגדרה שמאפשרת עבודה בלי HTTPS בתוך השרת המקומי (פותר שגיאות של גוגל בפיתוח)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# אתחול הדאטה-בייס ברגע שהשרת עולה (כדי לוודא שהטבלאות קיימות)
init_db()

def send_welcome_message(telegram_id):
    """שולח הודעת ברוכים הבאים מותאמת אישית לאחר התחברות מוצלחת"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Error: Cannot send welcome message - Token missing.")
        return

    message = (
        "🎉 **Success! I am connected to your calendar.**\n\n"
        "By the way, you can now:\n"
        "1. 🏷️ Give me a nickname (e.g., 'Call yourself Jarvis').\n"
        "2. 🎨 Set custom colors for events (e.g., 'Set Sports to Yellow').\n\n"
        "Just talk to me naturally!"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": telegram_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, json=payload)
        print(f"✅ Welcome message sent to {telegram_id}")
    except Exception as e:
        print(f"❌ Failed to send welcome message: {e}")

@app.route('/callback')
def callback():
    """
    זו הפונקציה שגוגל פונה אליה אחרי שהמשתמש אישר.
    היא מקבלת ב-URL שני פרמטרים:
    1. code - המפתח הזמני שצריך להחליף לטוקן קבוע.
    2. state - ה-ID של המשתמש בטלגרם (ששלחנו ביצירת הלינק).
    """
    # שליפת הפרמטרים מהכתובת
    state = request.args.get('state')
    code = request.args.get('code')
    error = request.args.get('error')

    # טיפול במקרים שהמשתמש לחץ "ביטול" או שיש שגיאה
    if error:
        return f"<h1>שגיאה:</h1><p>{error}</p>", 400

    if not code or not state:
        return "<h1>שגיאה:</h1><p>חסרים נתונים בבקשה (code או state).</p>", 400

    try:
        # המרת ה-state למספר (Telegram ID)
        telegram_id = int(state)
        
        # שחזור ה-Flow כדי לבצע את החלפת הטוקן
        flow = create_flow()
        
        # החלפת ה-Code ב-Token אמיתי
        flow.fetch_token(code=code)
        
        # שמירה בבסיס הנתונים
        success = save_user_token_from_flow(flow, telegram_id)
        
        if success:
            # TRIGGER POINT: Send welcome message
            send_welcome_message(telegram_id)
            
            return """
            <div style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: green;">התחברת בהצלחה! 🎉</h1>
                <p>הבוט מחובר עכשיו ליומן הגוגל שלך.</p>
                <p>קיבלת הודעה בטלגרם עם הסבר על הצעדים הבאים.</p>
                <p>אתה יכול לסגור את החלון הזה.</p>
            </div>
            """
        else:
            return "<h1>שגיאה בשמירה בבסיס הנתונים.</h1>", 500

    except Exception as e:
        print(f"Error processing callback: {e}")
        return f"<h1>שגיאה פנימית:</h1><p>{str(e)}</p>", 500

if __name__ == '__main__':
    print("🌍 Starting Web Server on port 5000...")
    # הפעלת השרת בפורט 5000
    app.run(host='0.0.0.0', port=5000)