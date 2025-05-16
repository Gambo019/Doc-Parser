import uuid
from enum import Enum
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from app.core.logger import logger
from app.core.database import Database

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskManager:
    """Manages asynchronous tasks and their statuses"""
    
    def __init__(self):
        self.db = Database()
        self.tasks = {}  # In-memory cache of recent tasks
        
    def create_task(self, document_id=None) -> str:
        """Create a new task and return its ID"""
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        task_data = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "created_at": timestamp,
            "updated_at": timestamp,
            "document_id": document_id,
            "error": None
        }
        
        # Store in database
        try:
            self.db.save_task(task_data)
        except Exception as e:
            logger.error(f"Failed to save task to database: {str(e)}")
            
        # Store in memory
        self.tasks[task_id] = task_data
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task with document details"""
        try:
            task_data = self.db.get_task_with_document(task_id)
            if task_data:
                pass
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get task from database: {str(e)}")
            return None
            
        return task_data
    
    def update_task_status(self, task_id: str, status: TaskStatus, document_id: int = None, error: str = None) -> bool:
        """Update the status of a task"""
        if task_id not in self.tasks and not self.get_task_status(task_id):
            logger.error(f"Task {task_id} not found")
            return False
            
        timestamp = datetime.now().isoformat()
        
        # Update task data
        task_data = self.tasks[task_id]
        task_data["status"] = status
        task_data["updated_at"] = timestamp
        
        if document_id is not None:
            task_data["document_id"] = document_id
            
        if error is not None:
            task_data["error"] = error
            
        # Update database
        try:
            self.db.update_task(task_id, task_data)
        except Exception as e:
            logger.error(f"Failed to update task in database: {str(e)}")
            
        return True