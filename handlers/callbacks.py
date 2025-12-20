from telegram import Update
from telegram.ext import ContextTypes
from database import get_database_manager

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    # data format: "task_done_{task_id}" or "task_notyet_{task_id}" or "task_cancel_{task_id}"
    
    db = get_database_manager()
    
    if data.startswith("task_done_"):
        task_id = data.replace("task_done_", "")
        if db.update_task_status(task_id, "completed"):
            await query.edit_message_text(text=f"{query.message.text}\n\n✅ בוצע! כל הכבוד.")
        else:
            await query.edit_message_text(text="שגיאה בעדכון המשימה.")
            
    elif data.startswith("task_cancel_"):
        task_id = data.replace("task_cancel_", "")
        if db.update_task_status(task_id, "cancelled"):
            await query.edit_message_text(text=f"{query.message.text}\n\n🛑 בוטל.")
        else:
            await query.edit_message_text(text="שגיאה בביטול המשימה.")

    elif data.startswith("task_notyet_"):
        task_id = data.replace("task_notyet_", "")
        # Ask user for reschedule
        # We need to save state. simple way: context.user_data
        context.user_data["waiting_for_reschedule"] = True
        context.user_data["current_task_id"] = task_id
        
        await query.edit_message_text(
            text=f"{query.message.text}\n\n⏳ לא נורא. מתי להזכיר לך שוב?\n(כתוב למשל: 'מחר בבוקר', 'עוד שעה')"
        )
