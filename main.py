# שינוי 1: הוספנו את MessageHandler ואת filters לרשימת הייבוא
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# ייבוא הפונקציות שלנו
from config import settings
from database import get_database_manager
from handlers.commands import start_command
# שינוי 2: ייבוא הפונקציה שמטפלת בהודעות טקסט (שיצרנו בשלב הקודם)
from handlers.messages import handle_text_message
from handlers.callbacks import handle_callback_query
from services.reminder_service import check_pending_tasks

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # 1. טעינת משתני סביבה (מתבצעת אוטומטית ב-config)
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file (or settings)!")
        return

    # 2. אתחול הדאטה-בייס
    db = get_database_manager()
    db.init_db()

    # 3. בניית האפליקציה של הבוט
    application = ApplicationBuilder().token(token).build()

    # 4. חיבור ה-Handlers (הפקודות וההודעות)
    
    # א. טיפול בפקודת /start
    start_handler = CommandHandler('start', start_command)
    application.add_handler(start_handler)
    
    # ב. טיפול בכפתורים (Callbacks)
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # שינוי 3: טיפול בהודעות טקסט רגילות
    # filters.TEXT & ~filters.COMMAND אומר: "תקשיב לכל טקסט, אבל תתעלם אם זה מתחיל ב-/"
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    application.add_handler(text_handler)
    
    # 5. Job Queue (תזכורות)
    job_queue = application.job_queue
    # הרצת הבדיקה כל 10 דקות (600 שניות)
    job_queue.run_repeating(check_pending_tasks, interval=600, first=10)

    # 6. הרצת הבוט (Polling)
    print("🤖 Bot is up and running...")
    application.run_polling()

if __name__ == '__main__':
    main()