import os
import logging
from dotenv import load_dotenv
# שינוי 1: הוספנו את MessageHandler ואת filters לרשימת הייבוא
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ייבוא הפונקציות שלנו
from database.connection import init_db
from handlers.commands import start_command
# שינוי 2: ייבוא הפונקציה שמטפלת בהודעות טקסט (שיצרנו בשלב הקודם)
from handlers.messages import handle_text_message

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # 1. טעינת משתני סביבה
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file!")
        return

    # 2. אתחול הדאטה-בייס
    init_db()

    # 3. בניית האפליקציה של הבוט
    application = ApplicationBuilder().token(token).build()

    # 4. חיבור ה-Handlers (הפקודות וההודעות)
    
    # א. טיפול בפקודת /start
    start_handler = CommandHandler('start', start_command)
    application.add_handler(start_handler)

    # שינוי 3: טיפול בהודעות טקסט רגילות
    # filters.TEXT & ~filters.COMMAND אומר: "תקשיב לכל טקסט, אבל תתעלם אם זה מתחיל ב-/"
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    application.add_handler(text_handler)

    # 5. הרצת הבוט (Polling)
    print("🤖 Bot is up and running...")
    application.run_polling()

if __name__ == '__main__':
    main()