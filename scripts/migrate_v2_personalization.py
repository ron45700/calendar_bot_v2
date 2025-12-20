import sqlite3
import os

# הפעלת הסקריפט מתיקיית השורש של הפרויקט
DB_PATH = "bot_database.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    print(f"🔌 Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # הוספת עמודת שם חיבה לבוט
        print("🛠 Adding 'bot_nickname' column...")
        cursor.execute("ALTER TABLE user ADD COLUMN bot_nickname VARCHAR DEFAULT 'CalendarBot';")
        print("✅ 'bot_nickname' added.")

        # הוספת עמודת העדפות צבעים (JSON)
        print("🛠 Adding 'color_preferences' column...")
        cursor.execute("ALTER TABLE user ADD COLUMN color_preferences TEXT;")
        print("✅ 'color_preferences' added.")

        conn.commit()
        print("🎉 Migration completed successfully!")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Columns already exist. Migration skipped.")
        else:
            print(f"❌ Error during migration: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
