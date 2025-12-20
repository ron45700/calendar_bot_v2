from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User

class DatabaseManager(ABC):
    
    @abstractmethod
    def init_db(self):
        """Initialize database (create tables, etc.)"""
        pass

    @abstractmethod
    def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        pass

    @abstractmethod
    def save_user(self, user: User) -> bool:
        """Create or Update user"""
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Get all users"""
        pass
