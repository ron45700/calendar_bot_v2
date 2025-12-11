from telegram import Update
from telegram.ext import ContextTypes
from services.openai_service import analyze_text
from services.google_service import add_event_to_calendar
from services.auth_service import get_user_credentials

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # 1. בדיקה האם המשתמש בכלל מחובר למערכת
    # אנחנו לא רוצים לבזבז כסף על OpenAI אם המשתמש לא עשה Login
    if not get_user_credentials(user_id):
        await update.message.reply_text("היי! אני רואה שעדיין לא התחברת ליומן. אנא לחץ על /start כדי להתחיל.")
        return

    # הודעת חיווי למשתמש (אופציונלי - נותן תחושה שהבוט "חושב")
    status_msg = await update.message.reply_text("🤖 מעבד את הבקשה...")

    # 2. שליחה למוח (OpenAI)
    ai_result = analyze_text(text)
    
    if not ai_result:
        await status_msg.edit_text("נתקלתי בבעיה בהבנת הטקסט. נסה שוב.")
        return

    action = ai_result.get("action")

    # 3. מקרה א': סתם שיחה
    if action == "chat":
        reply_text = ai_result.get("reply", "לא הבנתי, תוכל לנסח שוב?")
        await status_msg.edit_text(reply_text)

    # 4. מקרה ב': יצירת אירוע ביומן
    elif action == "create_event":
        event_data = ai_result.get("event")
        summary = event_data.get("summary")
        
        # עדכון המשתמש שאנחנו ניגשים לגוגל
        await status_msg.edit_text(f"יוצר אירוע: {summary}...")
        
        # ביצוע הפעולה
        success, link_or_error = add_event_to_calendar(user_id, event_data)
        
        if success:
            await status_msg.edit_text(
                f"✅ **בוצע!**\nהאירוע נוסף ליומן בהצלחה.\n[לחץ כאן לצפייה באירוע]({link_or_error})",
                parse_mode='Markdown'
            )
        else:
            await status_msg.edit_text(f"❌ שגיאה בהוספה ליומן:\n{link_or_error}")