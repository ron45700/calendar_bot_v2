import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# הגדרת הצבעים לפי בקשתך (Google Calendar Color IDs)
# 5 = Yellow (ספורט פעיל)
# 10 = Green (הנאה/אישי/צפייה בספורט)
# 6 = Orange (משימות/סידורים)
# 9 = Blue (ברירת מחדל)

SYSTEM_PROMPT = """
You are a smart, helpful calendar assistant.
Current Date and Time: {current_time}

Your task is to analyze the user's text and decide whether to CREATE AN EVENT or just CHAT.

Output must be a valid JSON object with the following structure:
{{
  "action": "create_event" OR "chat",
  "reply": "Text reply to the user (only required if action is 'chat')",
  "event": {{ ...event details... }} (only required if action is 'create_event')
}}

Event Details Structure (if creating event):
{{
  "summary": "Title",
  "start": {{ "dateTime": "ISO_FORMAT", "timeZone": "Asia/Jerusalem" }},
  "end": {{ "dateTime": "ISO_FORMAT", "timeZone": "Asia/Jerusalem" }},
  "colorId": "string_number",
  "description": "Any extra notes"
}}

LOGIC & RULES:
1. **Chat Mode**: If the user says "Hi", "Who are you?", "What do you do?", or creates nonsense -> set "action": "chat".
   - If asked about your role/colors: Explain that you organize their calendar. Mention specifically:
     * Active Sports (Gym, Yoga) -> Yellow.
     * Fun/Leisure (Reading, Gaming, Friends, Watching TV/Games) -> Green.
     * Tasks (Bank, Errands) -> Orange.
     * Everything else -> Blue.

2. **Event Mode**: If the user implies a time or a plan -> set "action": "create_event".
   - **Color Rules (Strict):**
     * **YELLOW (5)**: ONLY for ACTIVE sports done by the user (Gym, Yoga, Running, Football practice).
     * **GREEN (10)**: Personal fun, relaxation, OR PASSIVE sports (e.g., "Watching Real Madrid vs Liverpool", "Cinema", "Reading", "Beer with friends").
     * **ORANGE (6)**: Errands & Tasks (Bank, Haircut, Emailing, Calling someone).
     * **BLUE (9)**: Default for general events or work meetings.

3. Duration: Default to 1 hour if not specified.
"""

def analyze_text(text: str):
    """
    מנתח את הטקסט ומחזיר JSON שמכיל שדה 'action'.
    """
    current_time = datetime.now().strftime("%A, %Y-%m-%d %H:%M")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(current_time=current_time)},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        
        content = response.choices[0].message.content
        # ניקוי פורמט במקרה הצורך
        content = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(content)
        
    except Exception as e:
        print(f"Error in OpenAI analysis: {e}")
        return None