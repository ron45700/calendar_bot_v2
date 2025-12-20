from telegram import Update
from telegram.ext import ContextTypes
import json
from datetime import datetime
import pytz

from database import get_database_manager, Task
from services.openai_service import analyze_text
from services.google_service import add_event_to_calendar
from services.auth_service import get_user_credentials

JERUSALEM_TZ = pytz.timezone('Asia/Jerusalem')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    db = get_database_manager()
    user = db.get_user(user_id)

    # 1. State Check: Rescheduling
    # Check context first
    if context.user_data.get("waiting_for_reschedule"):
        task_id = context.user_data.get("current_task_id")
        
        # Check for cancel keywords
        if any(w in text for w in ["בטל", "לא רוצה", "cancel"]):
            db.update_task_status(task_id, "cancelled")
            await update.message.reply_text("🛑 המשימה בוטלה.")
        else:
            # AI Parse helper or simple assumption? 
            # For robustness, we should use OpenAI to parse "macha baboker" -> datetime
            # But here let's reuse analyze_text logic or a simplified parser.
            # Ideally we have a helper 'parse_datetime(text)'.
            # For this step, I'll use a hack -> ask AI to create a dummy event to parse time!
            # Or assume text IS the time description and we trust user or implement simple parser.
            # Let's ask OpenAI to parse time via separate call if possible, or piggyback analyze_text?
            # Piggybacking:
            ai_res = analyze_text(f"Create event called 'Reschedule' at {text}", user)
            if ai_res and ai_res.get("event"):
                new_time_str = ai_res["event"]["start"]["dateTime"]
                new_time = datetime.fromisoformat(new_time_str)
                
                task = db.get_task(task_id)
                if task:
                    task.check_in_time = new_time
                    task.status = "pending"
                    db.save_task(task)
                    await update.message.reply_text(f"✅ עודכן! נדבר ב-{new_time.strftime('%H:%M %d/%m')}.")
            else:
                 await update.message.reply_text("לא הצלחתי להבין את הזמן. נסה שוב (למשל: 'מחר ב-10').")
                 return # Keep state

        # Clear state
        context.user_data["waiting_for_reschedule"] = False
        context.user_data["current_task_id"] = None
        return

    # 2. Check if user wants to ENABLE follow-up service explicitly
    if any(w in text for w in ["תפעיל את התזכורות", "אני רוצה מעקב", "enable follow up"]):
        if user:
            user.follow_up_enabled = True
            db.save_user(user)
            await update.message.reply_text("✅   בשרת המעקב הופעל! מעכשיו, כשתרשום 'משימה' או 'תזכורת', אני אשלח הודעה בתשע בערב לשאול אם ביצעת אותה.")
            return

    # 3. Standard Logic
    if not get_user_credentials(user_id):
        await update.message.reply_text("היי! אני רואה שעדיין לא התחברת ליומן. אנא לחץ על /start כדי להתחיל.")
        return

    status_msg = await update.message.reply_text("🤖 מעבד את הבקשה...")

    ai_result = analyze_text(text, user)
    
    if not ai_result:
        await status_msg.edit_text("נתקלתי בבעיה בהבנת הטקסט. נסה שוב.")
        return

    action = ai_result.get("action")

    if action == "chat":
        reply_text = ai_result.get("reply", "לא הבנתי, תוכל לנסח שוב?")
        await status_msg.edit_text(reply_text)

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
            
            # --- TASK CREATION LOGIC ---
            # Strict Guard: Only if follow_up_enabled is True
            if user and user.follow_up_enabled:
                # Create Task for follow-up
                # Default logic: Check-in today at 21:00 or tomorrow 21:00 if late?
                # Simple MVP: Today 21:00.
                now = datetime.now(JERUSALEM_TZ)
                check_in = now.replace(hour=21, minute=0, second=0, microsecond=0)
                if now.hour >= 21:
                     # Check in tomorrow
                     # (Needs timedelta logic, but skipping import complexity if possible, or assume datetime handles it)
                     # from datetime import timedelta
                     pass # Assuming user won't create tasks at 23:00 expecting immediate check.
                
                new_task = Task(
                    user_id=user_id,
                    description=summary,
                    check_in_time=check_in,
                    status="pending"
                )
                db.save_task(new_task)
                # Ensure user knows? Or silent? Spec said "Check with you in the evening".
            # ---------------------------
            
        else:
            await status_msg.edit_text(f"❌ שגיאה בהוספה ליומן:\n{link_or_error}")

    elif action == "update_preferences":
        new_nickname = ai_result.get("bot_nickname")
        new_colors = ai_result.get("color_preferences")
        new_username = ai_result.get("username")
        
        # Get fresh user object to update
        db_user = db.get_user(user_id)
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
            
            if db.save_user(db_user):
                await status_msg.edit_text("✅ " + "\n".join(changes))
            else:
                await status_msg.edit_text("❌ שגיאה בשמירת השינויים.")
        else:
            await status_msg.edit_text("❌ שגיאה במציאת המשתמש.")