from services.openai_service import analyze_text
import json

class MockUser:
    def __init__(self, nickname=None, colors=None):
        self.bot_nickname = nickname
        self.color_preferences = colors

def test_persona_logic():
    print("🧪 Starting AI Persona Logic Tests...\n")
    
    with open("test_persona_results.log", "w", encoding="utf-8") as f:
        # Test 1: Capability Query (Rule A)
        # Expect: Intro with nickname, core skill explanation, color feature example, default duration.
        f.write("Test 1: 'What can you do?' (Rule A)\n")
        mock_user = MockUser(nickname="CalendarBot")
        res = analyze_text("What can you do?", user=mock_user)
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")

        # Test 2: Name Recognition (Rule B)
        # Expect: Warm response & help offer.
        f.write("Test 2: 'Hi Jarvis' (Rule B)\n")
        # User has named the bot "Jarvis"
        mock_user_jarvis = MockUser(nickname="Jarvis") 
        res = analyze_text("Hi Jarvis", user=mock_user_jarvis)
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")

        # Test 3: Event Creation with Preference
        # Expect: Correct Color ID based on preference key.
        f.write("Test 3: 'Schedule Gym' (Preference: Sports=Yellow)\n")
        # User mapped Sports to Yellow (ID 5)
        mock_user_pref = MockUser(colors='{"Sports": "5"}') 
        res = analyze_text("Schedule Gym at 8am", user=mock_user_pref)
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")
    
    print("Tests completed. Results in test_persona_results.log")

if __name__ == "__main__":
    test_persona_logic()
