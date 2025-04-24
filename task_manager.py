from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import json
import os

# Define task status enum
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Pydantic model for task validation
class Task(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"))
    title: str = Field(..., min_length=1)
    description: str
    due_date: str
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @validator('due_date')
    def validate_due_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class TaskManager:
    def __init__(self, storage_file: str = 'tasks.json'):
        self.storage_file = storage_file
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Task]:
        """Load tasks from JSON file or create empty list if file doesn't exist"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                return [Task(**task) for task in data]
        return []

    def _save_tasks(self) -> None:
        """Save tasks to JSON file"""
        with open(self.storage_file, 'w') as f:
            json.dump([task.dict() for task in self.tasks], f, indent=2)

    def create_task(self, task: Task) -> Task:
        """Create a new task"""
        self.tasks.append(task)
        self._save_tasks()
        return task

    def list_tasks(self) -> List[Task]:
        """List all tasks"""
        return self.tasks

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: str, updated_task: Task) -> Optional[Task]:
        """Update an existing task"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                updated_task.id = task_id
                updated_task.created_at = task.created_at
                updated_task.updated_at = datetime.now().isoformat()
                self.tasks[i] = updated_task
                self._save_tasks()
                return updated_task
        return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self._save_tasks()
                return True
        return False

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status"""
        return [task for task in self.tasks if task.status == status]