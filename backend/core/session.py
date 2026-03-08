"""Session state management — tracks projects, sprints, and tasks per session."""

from typing import Dict, Optional
from .models import SessionState, Sprint, Task, AgentId, TaskStatus
import uuid


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(
                session_id=session_id,
                agent_statuses={
                    aid.value: "idle"
                    for aid in AgentId
                },
            )
        return self._sessions[session_id]

    def get(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

    def add_sprint(self, session_id: str, sprint: Sprint) -> Sprint:
        session = self.get_or_create(session_id)
        session.sprints.append(sprint)
        return sprint

    def add_task(self, session_id: str, task: Task) -> Task:
        session = self.get_or_create(session_id)
        for sprint in session.sprints:
            if sprint.id == task.sprint:
                sprint.tasks.append(task)
                return task
        # No matching sprint — put in sprint 1
        if session.sprints:
            session.sprints[0].tasks.append(task)
        return task

    def update_task_status(self, session_id: str, task_id: str,
                           status: TaskStatus, result: Optional[str] = None):
        session = self.get_or_create(session_id)
        for sprint in session.sprints:
            for task in sprint.tasks:
                if task.id == task_id:
                    task.status = status
                    if result:
                        task.result = result
                    from datetime import datetime
                    task.updated_at = datetime.utcnow()
                    return task
        return None

    def get_sprints_dict(self, session_id: str) -> list:
        session = self.get_or_create(session_id)
        result = []
        for sprint in session.sprints:
            sprint_dict = {
                "id": sprint.id,
                "name": sprint.name,
                "goal": sprint.goal,
                "status": sprint.status,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "assigned_to": t.assigned_to.value if hasattr(t.assigned_to, 'value') else t.assigned_to,
                        "status": t.status.value if hasattr(t.status, 'value') else t.status,
                        "priority": t.priority,
                        "result": t.result,
                    }
                    for t in sprint.tasks
                ],
            }
            result.append(sprint_dict)
        return result


# Singleton
session_manager = SessionManager()
