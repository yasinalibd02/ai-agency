from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    DONE = "done"
    ERROR = "error"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class AgentId(str, Enum):
    PROJECT_MANAGER = "project_manager"
    DESIGNER = "designer"
    FRONTEND_DEV = "frontend_dev"
    BACKEND_DEV = "backend_dev"
    QA_TESTER = "qa_tester"
    SEO_SPECIALIST = "seo_specialist"
    VIRTUAL_CEO = "virtual_ceo"


class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    content: str
    message_type: str = "task"  # task | result | bug_report | review
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    assigned_to: AgentId
    status: TaskStatus = TaskStatus.TODO
    priority: str = "medium"  # low | medium | high | critical
    sprint: int = 1
    result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Sprint(BaseModel):
    id: int
    name: str
    goal: str
    tasks: List[Task] = []
    status: str = "active"


class SessionState(BaseModel):
    session_id: str
    project_name: str = "Untitled Project"
    current_sprint: int = 1
    sprints: List[Sprint] = []
    messages: List[Dict] = []
    agent_statuses: Dict[str, str] = {}


class UserMessage(BaseModel):
    content: str
    session_id: str


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # user | pm | system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None


class WSEvent(BaseModel):
    event_type: str  # chat_message | agent_status | task_update | sprint_update | agent_output
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentInfo(BaseModel):
    agent_id: str
    name: str
    emoji: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    last_output: Optional[str] = None
    tasks_completed: int = 0
