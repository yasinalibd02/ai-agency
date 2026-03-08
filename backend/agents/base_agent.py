"""Base agent — every specialized agent inherits from this."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..core.agent_bus import agent_bus
from ..core.models import AgentStatus


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, emoji: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.emoji = emoji
        self.role = role
        self.status = AgentStatus.IDLE
        self.current_task: Optional[str] = None
        self.tasks_completed: int = 0

        # Register to receive messages addressed to this agent
        agent_bus.subscribe(self.agent_id, self._on_message)

    async def _on_message(self, message: Dict[str, Any]):
        """Internal handler — updates status, then processes."""
        task_desc = message.get("task", "")
        task_id = message.get("task_id")
        session_id = message.get("session_id", "default")

        await self._set_status(AgentStatus.THINKING, task_desc)
        await asyncio.sleep(0.5)  # simulate thinking latency
        await self._set_status(AgentStatus.WORKING, task_desc)

        try:
            result = await self.process_task(task_desc, message, session_id)
            self.tasks_completed += 1
            await self._set_status(AgentStatus.DONE, task_desc, last_output=result)

            # Notify bus with structured output
            await agent_bus.send_agent_output(
                agent_id=self.agent_id,
                output_type=message.get("output_type", "result"),
                content=result,
                task_id=task_id,
            )

            # Report back to PM
            await agent_bus.publish("project_manager", {
                "type": "agent_result",
                "from_agent": self.agent_id,
                "task_id": task_id,
                "session_id": session_id,
                "result": result,
            })
        except Exception as e:
            await self._set_status(AgentStatus.ERROR, str(e))

    async def _set_status(self, status: AgentStatus, current_task: str = "",
                          last_output: Optional[str] = None):
        self.status = status
        self.current_task = current_task
        await agent_bus.agent_status_update(
            agent_id=self.agent_id,
            status=status.value,
            current_task=current_task,
            last_output=last_output,
            tasks_completed=self.tasks_completed,
        )

    async def send_to_agent(self, target_agent_id: str, task: str,
                            task_id: Optional[str] = None,
                            session_id: str = "default",
                            **kwargs):
        """Send a task to another agent via the AgentBus."""
        await agent_bus.publish(target_agent_id, {
            "task": task,
            "task_id": task_id,
            "session_id": session_id,
            "from_agent": self.agent_id,
            **kwargs,
        })

    @abstractmethod
    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        """Override in each specialized agent. Return a result string."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "emoji": self.emoji,
            "role": self.role,
            "status": self.status.value,
            "current_task": self.current_task,
            "tasks_completed": self.tasks_completed,
        }
