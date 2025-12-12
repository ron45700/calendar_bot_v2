from services.openai_service import analyze_text
import json

class MockUser:
    def __init__(self, nickname=None, colors=None):
        self.bot_nickname = nickname
        self.color_preferences = colors

def test_ai_logic():
    print("🧪 Starting AI Logic Tests...")
    
    with open("test_results.log", "w", encoding="utf-8") as f:
        # Test 1
        f.write("Test 1: 'Schedule Gym at 5pm'\n")
        res = analyze_text("Schedule Gym at 5pm")
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")

        # Test 2
        f.write("Test 2: 'Call me Jarvis'\n")
        res = analyze_text("Call me Jarvis")
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")

        # Test 3
        f.write("Test 3: 'Set Sports to Green'\n")
        res = analyze_text("Set Sports to Green")
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")

        # Test 4
        f.write("Test 4: 'Schedule Yoga' (With Context)\n")
        mock_user = MockUser(colors='{"Sports": 10}')
        res = analyze_text("Schedule Yoga at 6pm", user=mock_user)
        f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n\n")
    
    print("Tests completed. Results in test_results.log")

if __name__ == "__main__":
    test_ai_logic()
