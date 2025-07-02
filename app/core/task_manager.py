import uuid
from enum import Enum
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from app.core.logger import logger
from app.core.database import Database
from app.services.callback_service import CallbackService

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
        self.callback_service = CallbackService()
        
    def create_task(self, document_id=None, callback_url=None) -> str:
        """Create a new task and return its ID"""
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        task_data = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "created_at": timestamp,
            "updated_at": timestamp,
            "document_id": document_id,
            "error": None,
            "callback_url": callback_url
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
        """Update the status of a task and trigger callback if needed"""
        task_data = self.get_task_status(task_id)
        if not task_data:
            logger.error(f"Task {task_id} not found")
            return False
            
        timestamp = datetime.now().isoformat()
        
        # Update task data
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = timestamp
            if document_id is not None:
                self.tasks[task_id]["document_id"] = document_id
            if error is not None:
                self.tasks[task_id]["error"] = error
        else:
            # Create task data for memory cache
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": status,
                "created_at": task_data.get("created_at", timestamp),
                "updated_at": timestamp,
                "document_id": document_id or task_data.get("document_id"),
                "error": error,
                "callback_url": task_data.get("callback_url")
            }
        
        # Update database
        try:
            self.db.update_task(task_id, self.tasks[task_id])
        except Exception as e:
            logger.error(f"Failed to update task in database: {str(e)}")
        
        # Send callback if task is completed or failed
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self._send_callback(task_id)
            
        return True
    
    def _send_callback(self, task_id: str) -> None:
        """Send callback notification for completed/failed task"""
        try:
            # Get full task data with document details
            task_data = self.get_task_status(task_id)
            if not task_data or not task_data.get("callback_url"):
                return
            
            # Prepare callback payload
            callback_payload = {
                "task_id": task_data["task_id"],
                "status": task_data["status"],
                "created_at": task_data["created_at"],
                "updated_at": task_data["updated_at"],
                "error": task_data.get("error"),
                "document_id": task_data.get("document_id")
            }
            
            # Include document details if task completed successfully
            if task_data["status"] == TaskStatus.COMPLETED and task_data.get("document_id"):
                callback_payload.update({
                    "extracted_data": task_data.get("extracted_data", {}),
                    "validation_status": task_data.get("validation_status", {}),
                    "s3_key": task_data.get("s3_key")
                })
            
            # Send callback asynchronously
            callback_url = task_data["callback_url"]
            success = self.callback_service.send_callback_sync(callback_url, callback_payload)
            
            if success:
                logger.info(f"Callback sent successfully for task {task_id}")
            else:
                logger.warning(f"Failed to send callback for task {task_id}")
                
        except Exception as e:
            logger.error(f"Error sending callback for task {task_id}: {str(e)}")