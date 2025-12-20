from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    # Telegram ID (Primary Key)
    telegram_id: int = Field(primary_key=True)
    
    # Username (for logs/display)
    username: Optional[str] = None
    
    # Join date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Google Tokens (JSON string)
    google_token_data: Optional[str] = None

    # Bot Nickname
    bot_nickname: Optional[str] = Field(default="נהוראי")

    # Color preferences (JSON string)
    color_preferences: Optional[str] = None
    
    # Feature Flags
    # Default False as per user request (Opt-in)
    follow_up_enabled: bool = Field(default=False)
    
    # Timezone (Future proofing)
    timezone: str = Field(default="Asia/Jerusalem")

class Task(SQLModel, table=True):
    task_id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    user_id: int = Field(index=True)
    
    description: str
    status: str = Field(default="pending") # pending, completed, cancelled, rescheduled
    
    # When to remind/check-in
    check_in_time: datetime 
    
    created_at: datetime = Field(default_factory=datetime.utcnow)