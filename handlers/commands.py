from telegram import Update
from telegram.ext import ContextTypes
from services.auth_service import get_authorization_url

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    פונקציה זו נקראת כשהמשתמש שולח /start
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # 1. יצירת לינק אימות ייחודי למשתמש
    try:
        auth_url = get_authorization_url(user.id)
        
        # 2. שליחת ההודעה
        welcome_text = (
            f"היי {user.first_name}! 👋\n\n"
            f"כדי שאוכל לנהל לך את היומן, אני צריך אישור חד-פעמי מגוגל.\n"
            f"התהליך מאובטח וקורה דרך הדפדפן שלך.\n\n"
            f"👇 **לחץ על הלינק כדי להתחבר:**\n{auth_url}"
        )
        
        await context.bot.send_message(chat_id=chat_id, text=welcome_text)
        
    except Exception as e:
        print(f"Error generating link: {e}")
        await context.bot.send_message(chat_id=chat_id, text="אופס, קרתה שגיאה ביצירת הלינק. נסה שוב מאוחר יותר.")