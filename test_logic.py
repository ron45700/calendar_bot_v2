from services.openai_service import analyze_text
from services.google_service import add_event_to_calendar

MY_TELEGRAM_ID = 489036181  # <--- שים פה את ה-ID שלך

def run_test(text_input):
    print(f"\n🔹 Testing: '{text_input}'")
    result = analyze_text(text_input)
    
    if not result:
        print("❌ Error: AI returned None")
        return

    action = result.get("action")
    print(f"   Action identified: {action}")

    if action == "chat":
        print(f"   🤖 Bot Reply: {result.get('reply')}")
        
    elif action == "create_event":
        event_data = result.get("event")
        color = event_data.get("colorId")
        summary = event_data.get("summary")
        print(f"   📅 Event: {summary} (Color ID: {color})")
        
        # הוספה ליומן באמת
        success, link = add_event_to_calendar(MY_TELEGRAM_ID, event_data)
        if success:
            print(f"   ✅ Added to Calendar: {link}")
        else:
            print(f"   ❌ Google Error: {link}")

if __name__ == "__main__":
    # בדיקה 1: ספורט פעיל (אמור להיות צהוב - 5)
    run_test("אימון חזה יד אחורית מחר ב-18:00")
    
    # בדיקה 2: הנאה/צפייה (אמור להיות ירוק - 10) - הדוגמה שנתת
    run_test("לראות את המשחק של ריאל נגד ליברפול ביום שלישי ב-22:00")
    
    # בדיקה 3: שאלה כללית (אמור לענות בהסבר)
    run_test("מי אתה ואיך אתה מחליט על הצבעים?")