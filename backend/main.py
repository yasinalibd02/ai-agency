"""
Virtual Agency — FastAPI Backend
WebSocket server + REST API coordinating the multi-agent system.
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .core.agent_bus import agent_bus
from .core.session import session_manager
from .core.models import UserMessage
from .agents import (
    ProjectManagerAgent,
    DesignerAgent,
    FrontendDevAgent,
    BackendDevAgent,
    QATesterAgent,
    SEOSpecialistAgent,
    VirtualCEOAgent,
)

load_dotenv()

# ── Agent instances (singletons) ──────────────────────────────────────────────
pm_agent: ProjectManagerAgent = None
designer_agent: DesignerAgent = None
frontend_agent: FrontendDevAgent = None
backend_agent: BackendDevAgent = None
qa_agent: QATesterAgent = None
seo_agent: SEOSpecialistAgent = None
ceo_agent: VirtualCEOAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all agents on startup."""
    global pm_agent, designer_agent, frontend_agent
    global backend_agent, qa_agent, seo_agent, ceo_agent

    print("🚀 Initializing Virtual Agency — 7 agents activating...")
    pm_agent = ProjectManagerAgent()
    designer_agent = DesignerAgent()
    frontend_agent = FrontendDevAgent()
    backend_agent = BackendDevAgent()
    qa_agent = QATesterAgent()
    seo_agent = SEOSpecialistAgent()
    ceo_agent = VirtualCEOAgent()
    print("✅ All agents online. Virtual Agency is ready.")
    yield
    print("🔴 Virtual Agency shutting down.")


app = FastAPI(
    title="Virtual Agency API",
    description="Multi-agent AI software development platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "agents": 7, "version": "1.0.0"}


@app.get("/api/agents")
async def get_agents():
    """Return live status of all agents."""
    agents = [pm_agent, designer_agent, frontend_agent, backend_agent,
               qa_agent, seo_agent, ceo_agent]
    return {"agents": [a.to_dict() for a in agents if a]}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session = session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.session_id,
        "project_name": session.project_name,
        "sprints": session_manager.get_sprints_dict(session_id),
    }


@app.post("/api/message")
async def send_message(message: UserMessage):
    """HTTP fallback for sending a message to the PM (WebSocket preferred)."""
    if not pm_agent:
        raise HTTPException(status_code=503, detail="Agents not initialized")

    # Echo user message to UI
    await agent_bus.send_chat_message(
        role="user",
        content=message.content,
    )

    # Let PM handle async (don't await — respond immediately)
    asyncio.create_task(
        pm_agent.handle_user_message(message.content, message.session_id)
    )

    return {"status": "processing", "session_id": message.session_id}


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    agent_bus.register_ws_client(websocket)

    # Send initial state to newly connected client
    agents_data = [pm_agent, designer_agent, frontend_agent, backend_agent,
                   qa_agent, seo_agent, ceo_agent]
    await websocket.send_text(json.dumps({
        "event_type": "init",
        "payload": {
            "agents": [a.to_dict() for a in agents_data if a],
            "sprints": session_manager.get_sprints_dict(session_id),
            "session_id": session_id,
        }
    }))

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                content = data.get("content", "")
                if not content.strip():
                    continue

                # Echo user message
                await agent_bus.send_chat_message(role="user", content=content)

                # Dispatch to PM
                asyncio.create_task(
                    pm_agent.handle_user_message(content, session_id)
                )

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"event_type": "pong"}))

    except WebSocketDisconnect:
        agent_bus.unregister_ws_client(websocket)
        print(f"[WS] Client {session_id} disconnected")
    except Exception as e:
        agent_bus.unregister_ws_client(websocket)
        print(f"[WS] Error for {session_id}: {e}")
