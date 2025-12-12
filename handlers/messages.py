from telegram import Update
from telegram.ext import ContextTypes
from sqlmodel import Session, select
from database.connection import engine
from database.models import User
import json

from services.openai_service import analyze_text
from services.google_service import add_event_to_calendar
from services.auth_service import get_user_credentials

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # 1. בדיקה האם המשתמש בכלל מחובר למערכת
    if not get_user_credentials(user_id):
        await update.message.reply_text("היי! אני רואה שעדיין לא התחברת ליומן. אנא לחץ על /start כדי להתחיל.")
        return

    # הודעת חיווי למשתמש
    status_msg = await update.message.reply_text("🤖 מעבד את הבקשה...")

    # 2. שליפת פרטי המשתמש (כדי להעביר ל-AI את הכינוי וההעדפות)
    user = None
    with Session(engine) as session:
        user = session.get(User, user_id)

    # 3. שליחה למוח (OpenAI)
    ai_result = analyze_text(text, user)
    
    if not ai_result:
        await status_msg.edit_text("נתקלתי בבעיה בהבנת הטקסט. נסה שוב.")
        return

    action = ai_result.get("action")

    # 4. מקרה א': סתם שיחה
    if action == "chat":
        reply_text = ai_result.get("reply", "לא הבנתי, תוכל לנסח שוב?")
        await status_msg.edit_text(reply_text)

    # 5. מקרה ב': יצירת אירוע ביומן
    elif action == "create_event":
        event_data = ai_result.get("event")
        summary = event_data.get("summary")
        
        await status_msg.edit_text(f"יוצר אירוע: {summary}...")
        
        success, link_or_error = add_event_to_calendar(user_id, event_data)
        
        if success:
            await status_msg.edit_text(
                f"✅ **בוצע!**\nהאירוע נוסף ליומן בהצלחה.\n מוזמן ללכת ליומן לראות!)",
                parse_mode='Markdown'
            )
        else:
            await status_msg.edit_text(f"❌ שגיאה בהוספה ליומן:\n{link_or_error}")

    # 6. מקרה ג': עדכון העדפות (Part of Personalization)
    elif action == "update_preferences":
        new_nickname = ai_result.get("bot_nickname")
        new_colors = ai_result.get("color_preferences")
        new_username = ai_result.get("username")
        
        with Session(engine) as session:
            db_user = session.get(User, user_id)
            if db_user:
                changes = []
                if new_nickname:
                    db_user.bot_nickname = new_nickname
                    changes.append(f"Name updated to: {new_nickname}")
                
                if new_colors:
                    existing = json.loads(db_user.color_preferences) if db_user.color_preferences else {}
                    existing.update(new_colors)
                    db_user.color_preferences = json.dumps(existing)
                    changes.append("Color preferences updated.")
                
                if new_username:
                    db_user.username = new_username
                    changes.append(f"Username updated to: {new_username}")
                
                session.add(db_user)
                session.commit()
                
                await status_msg.edit_text("✅ " + "\n".join(changes))
            else:
                await status_msg.edit_text("❌ שגיאה במציאת המשתמש.")