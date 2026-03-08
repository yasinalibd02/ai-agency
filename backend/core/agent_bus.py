"""
AgentBus — the async pub/sub backbone of Virtual Agency.
All inter-agent communication and UI broadcasts flow through here.
"""

import asyncio
import json
from typing import Dict, List, Callable, Any, Optional, Set
from datetime import datetime
from .models import WSEvent


class AgentBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._websocket_clients: Set = set()
        self._message_history: List[Dict] = []

    # ── WebSocket client management ────────────────────────────────────────
    def register_ws_client(self, websocket):
        self._websocket_clients.add(websocket)

    def unregister_ws_client(self, websocket):
        self._websocket_clients.discard(websocket)

    async def broadcast_to_ui(self, event_type: str, payload: Dict[str, Any]):
        """Send a real-time event to all connected browser clients."""
        event = WSEvent(event_type=event_type, payload=payload)
        event_json = event.model_dump_json()
        self._message_history.append(event.model_dump())

        disconnected = set()
        for ws in self._websocket_clients:
            try:
                await ws.send_text(event_json)
            except Exception:
                disconnected.add(ws)

        for ws in disconnected:
            self._websocket_clients.discard(ws)

    # ── Agent pub/sub ────────────────────────────────────────────────────
    def subscribe(self, channel: str, callback: Callable):
        """Register an agent to listen on a channel (usually their agent_id)."""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

    async def publish(self, channel: str, message: Dict[str, Any]):
        """Route a message to all subscribers of a channel."""
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"[AgentBus] Error delivering to {channel}: {e}")

    # ── Convenience helpers ───────────────────────────────────────────────
    async def agent_status_update(self, agent_id: str, status: str,
                                  current_task: Optional[str] = None,
                                  last_output: Optional[str] = None,
                                  tasks_completed: Optional[int] = None):
        """Broadcast a live agent status change to the dashboard."""
        payload = {
            "agent_id": agent_id,
            "status": status,
            "current_task": current_task,
            "last_output": last_output,
        }
        if tasks_completed is not None:
            payload["tasks_completed"] = tasks_completed
        await self.broadcast_to_ui("agent_status", payload)

    async def send_chat_message(self, role: str, content: str,
                                agent_id: Optional[str] = None):
        """Push a chat message to the UI's PM conversation panel."""
        payload = {
            "role": role,
            "content": content,
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_ui("chat_message", payload)

    async def send_sprint_update(self, sprints: list):
        """Push sprint/task board updates to the UI."""
        await self.broadcast_to_ui("sprint_update", {"sprints": sprints})

    async def send_agent_output(self, agent_id: str, output_type: str,
                                content: str, task_id: Optional[str] = None):
        """Send a structured agent output panel update."""
        await self.broadcast_to_ui("agent_output", {
            "agent_id": agent_id,
            "output_type": output_type,
            "content": content,
            "task_id": task_id,
        })

    def get_history(self) -> List[Dict]:
        return self._message_history


# Singleton instance shared across the entire app
agent_bus = AgentBus()
