from typing import Optional, List
from .interface import DatabaseManager
from .models import User, Task
from datetime import datetime
import json

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    print("Warning: google-cloud-firestore not installed. Using dummy mode.")

class FirestoreManager(DatabaseManager):
    def __init__(self, use_dummy: bool = False, credentials_path: str = None):
        self.use_dummy = use_dummy
        self.db = None
        self.users_collection = "users"
        self.tasks_collection = "tasks"

        if not self.use_dummy and FIRESTORE_AVAILABLE:
            try:
                if credentials_path:
                    self.db = firestore.Client.from_service_account_json(credentials_path)
                else:
                    self.db = firestore.Client() # Infer from env
                print("Firestore Client initialized successfully.")
            except Exception as e:
                print(f"Failed to init Firestore: {e}. Switching to dummy mode.")
                self.use_dummy = True
        else:
            self.use_dummy = True

    def init_db(self):
        if self.use_dummy:
            print("[Dummy/Firestore] init_db called (No-op).")
        else:
            print("[Firestore] No explicit init needed for Firestore collections.")

    # --- User Methods ---
    def get_user(self, telegram_id: int) -> Optional[User]:
        if self.use_dummy:
            # Dummy logic: return a dummy user if ID matches specific test case, else None or create one?
            print(f"[Dummy/Firestore] get_user({telegram_id}) - returning Dummy User")
            # Return a dummy user with defaults to avoid errors
            return User(telegram_id=telegram_id, username="DummyUser", follow_up_enabled=False)
        
        try:
            doc_ref = self.db.collection(self.users_collection).document(str(telegram_id))
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return User(**data)
            return None
        except Exception as e:
            print(f"Error getting user from Firestore: {e}")
            return None

    def save_user(self, user: User) -> bool:
        data = user.dict()
        if self.use_dummy:
            print(f"[Dummy/Firestore] save_user: {data}")
            return True
            
        try:
            doc_ref = self.db.collection(self.users_collection).document(str(user.telegram_id))
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"Error saving user to Firestore: {e}")
            return False

    def get_all_users(self) -> List[User]:
        if self.use_dummy:
            print("[Dummy/Firestore] get_all_users - returning empty list")
            return []
        
        try:
            users_ref = self.db.collection(self.users_collection)
            docs = users_ref.stream()
            users = []
            for doc in docs:
                users.append(User(**doc.to_dict()))
            return users
        except Exception as e:
            print(f"Error getting all users from Firestore: {e}")
            return []

    # --- Task Methods ---
    def save_task(self, task: Task) -> bool:
        data = task.dict()
        # Firestore expects naive or timezone aware datetimes. 
        # Pydantic dict might output datetime objects, which firestore handles.
        if self.use_dummy:
            print(f"[Dummy/Firestore] save_task: {data}")
            return True
            
        try:
            doc_ref = self.db.collection(self.tasks_collection).document(task.task_id)
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"Error saving task to Firestore: {e}")
            return False
            
    def get_task(self, task_id: str) -> Optional[Task]:
        if self.use_dummy:
            print(f"[Dummy/Firestore] get_task({task_id})")
            return None
            
        try:
            doc_ref = self.db.collection(self.tasks_collection).document(task_id)
            doc = doc_ref.get()
            if doc.exists:
                return Task(**doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None

    def get_pending_tasks(self, check_time: datetime) -> List[Task]:
        """
        Get tasks where status is pending and check_in_time <= check_time
        """
        if self.use_dummy:
            print(f"[Dummy/Firestore] get_pending_tasks (<= {check_time})")
            return []
            
        try:
            tasks_ref = self.db.collection(self.tasks_collection)
            # Query: status == 'pending' AND check_in_time <= check_time
            query = tasks_ref.where("status", "==", "pending").where("check_in_time", "<=", check_time)
            docs = query.stream()
            
            tasks = []
            for doc in docs:
                tasks.append(Task(**doc.to_dict()))
            return tasks
        except Exception as e:
            print(f"Error getting pending tasks: {e}")
            return []
            
    def update_task_status(self, task_id: str, status: str) -> bool:
        if self.use_dummy:
            print(f"[Dummy/Firestore] update_task_status({task_id}, {status})")
            return True
            
        try:
            doc_ref = self.db.collection(self.tasks_collection).document(task_id)
            doc_ref.update({"status": status})
            return True
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False
