"""
Project Manager Agent — the orchestrator and sole user-facing agent.
Receives requirements, plans sprints, delegates tasks, and synthesizes results.
"""

import asyncio
import os
import re
from typing import Dict, Any
from .base_agent import BaseAgent
from ..core.agent_bus import agent_bus
from ..core.session import session_manager
from ..core.models import Sprint, Task, AgentId, TaskStatus, AgentStatus

# Optional: real LLM if OPENAI_API_KEY is set
try:
    from openai import AsyncOpenAI
    _openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    _HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _HAS_OPENAI = False


AGENT_ASSIGNMENTS = {
    "design": AgentId.DESIGNER,
    "ui": AgentId.DESIGNER,
    "ux": AgentId.DESIGNER,
    "frontend": AgentId.FRONTEND_DEV,
    "react": AgentId.FRONTEND_DEV,
    "next": AgentId.FRONTEND_DEV,
    "component": AgentId.FRONTEND_DEV,
    "backend": AgentId.BACKEND_DEV,
    "api": AgentId.BACKEND_DEV,
    "database": AgentId.BACKEND_DEV,
    "server": AgentId.BACKEND_DEV,
    "test": AgentId.QA_TESTER,
    "qa": AgentId.QA_TESTER,
    "bug": AgentId.QA_TESTER,
    "seo": AgentId.SEO_SPECIALIST,
    "content": AgentId.SEO_SPECIALIST,
    "meta": AgentId.SEO_SPECIALIST,
    "strategy": AgentId.VIRTUAL_CEO,
    "scale": AgentId.VIRTUAL_CEO,
    "cost": AgentId.VIRTUAL_CEO,
    "plan": AgentId.VIRTUAL_CEO,
}

SPRINT_TEMPLATE = [
    {
        "title": "Design System & Architecture",
        "description": "Create the overall design language, color palette, typography, and component library.",
        "agent": AgentId.DESIGNER,
        "priority": "high",
        "output_type": "design_spec",
    },
    {
        "title": "Frontend Implementation",
        "description": "Build all UI components and pages using Next.js and the approved design system.",
        "agent": AgentId.FRONTEND_DEV,
        "priority": "high",
        "output_type": "code",
    },
    {
        "title": "Backend API Development",
        "description": "Implement RESTful APIs, database schemas, and business logic using FastAPI.",
        "agent": AgentId.BACKEND_DEV,
        "priority": "high",
        "output_type": "code",
    },
    {
        "title": "Quality Assurance & Testing",
        "description": "Write unit tests, integration tests, and perform comprehensive bug hunting.",
        "agent": AgentId.QA_TESTER,
        "priority": "medium",
        "output_type": "test_report",
    },
    {
        "title": "SEO Optimization & Content",
        "description": "Optimize metadata, structure, and content for maximum search engine visibility.",
        "agent": AgentId.SEO_SPECIALIST,
        "priority": "medium",
        "output_type": "seo_report",
    },
    {
        "title": "Strategic Review & Scaling Plan",
        "description": "Provide cost estimation, technology recommendations, and a 12-month scaling roadmap.",
        "agent": AgentId.VIRTUAL_CEO,
        "priority": "low",
        "output_type": "strategy_doc",
    },
]


class ProjectManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="project_manager",
            name="Project Manager",
            emoji="🎯",
            role="Orchestrator & User Interface",
        )
        self._pending_results: Dict[str, str] = {}
        self._active_task_count: int = 0
        # Listen for results coming back from sub-agents
        agent_bus.subscribe("project_manager", self._handle_agent_result)

    async def _handle_agent_result(self, message: Dict[str, Any]):
        """Collect results from sub-agents and synthesize when all done."""
        if message.get("type") != "agent_result":
            return
        from_agent = message.get("from_agent", "")
        result = message.get("result", "")
        task_id = message.get("task_id", "")
        session_id = message.get("session_id", "default")

        self._pending_results[from_agent] = result
        self._active_task_count = max(0, self._active_task_count - 1)

        # Update task status in session
        session_manager.update_task_status(session_id, task_id, TaskStatus.DONE, result)
        sprints = session_manager.get_sprints_dict(session_id)
        await agent_bus.send_sprint_update(sprints)

        # When all sub-agents have reported, synthesize a final PM response
        if self._active_task_count == 0 and self._pending_results:
            await asyncio.sleep(1.5)
            summary = self._synthesize_results(self._pending_results)
            await agent_bus.send_chat_message(
                role="pm",
                content=summary,
                agent_id=self.agent_id,
            )
            self._pending_results = {}
            await self._set_status(AgentStatus.IDLE)

    def _synthesize_results(self, results: Dict[str, str]) -> str:
        parts = ["✅ **Sprint Complete!** Here's a summary of what each agent delivered:\n"]
        emoji_map = {
            "designer": "🎨",
            "frontend_dev": "⚛️",
            "backend_dev": "🔧",
            "qa_tester": "🧪",
            "seo_specialist": "🔍",
            "virtual_ceo": "🏢",
        }
        name_map = {
            "designer": "UI/UX Designer",
            "frontend_dev": "Frontend Dev",
            "backend_dev": "Backend Dev",
            "qa_tester": "QA Tester",
            "seo_specialist": "SEO Specialist",
            "virtual_ceo": "Virtual CEO",
        }
        for agent_id, result in results.items():
            em = emoji_map.get(agent_id, "🤖")
            name = name_map.get(agent_id, agent_id)
            preview = result[:200] + "..." if len(result) > 200 else result
            parts.append(f"**{em} {name}**: {preview}\n")
        parts.append("\n---\nAll tasks are complete. Ready for next sprint or further requirements!")
        return "\n".join(parts)

    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        """Called when the PM receives a task via the AgentBus (not from WebSocket directly)."""
        return await self.handle_user_message(task, session_id)

    async def handle_user_message(self, content: str, session_id: str) -> str:
        """Main entry point for user → PM communication."""
        from ..core.models import AgentStatus
        await self._set_status(AgentStatus.THINKING, "Analyzing requirements...")

        # Use real LLM if available, else structured mock
        if _HAS_OPENAI:
            pm_reply = await self._llm_plan(content, session_id)
        else:
            pm_reply = await self._mock_plan(content, session_id)

        await agent_bus.send_chat_message(role="pm", content=pm_reply, agent_id=self.agent_id)
        await self._set_status(AgentStatus.WORKING, "Coordinating team...")
        return pm_reply

    async def _mock_plan(self, content: str, session_id: str) -> str:
        """Structured intelligent mock response + task distribution."""
        session = session_manager.get_or_create(session_id)

        # Extract project name heuristic
        project_keywords = re.findall(r'\b(?:build|create|make|develop)\s+(?:a\s+)?(.+?)(?:\s+app|\s+platform|\s+system|\s+website|$)', content, re.I)
        project_name = project_keywords[0].strip().title() if project_keywords else "New Project"
        session.project_name = project_name

        await asyncio.sleep(1.2)

        # Create Sprint 1
        sprint = Sprint(
            id=1,
            name="Sprint 1 — Foundation",
            goal=f"Build the core architecture and MVP features for {project_name}",
        )
        session_manager.add_sprint(session_id, sprint)

        # Create and assign tasks
        tasks_created = []
        for i, t in enumerate(SPRINT_TEMPLATE):
            task = Task(
                title=t["title"],
                description=f"{t['description']} for: {project_name}",
                assigned_to=t["agent"],
                priority=t["priority"],
                sprint=1,
            )
            session_manager.add_task(session_id, task)
            tasks_created.append((task, t))

        # Update sprint board
        sprints_dict = session_manager.get_sprints_dict(session_id)
        await agent_bus.send_sprint_update(sprints_dict)

        # Dispatch tasks to sub-agents with staggered delays
        self._active_task_count = len(tasks_created)
        self._pending_results = {}

        for i, (task, template) in enumerate(tasks_created):
            await asyncio.sleep(i * 0.8)  # stagger so UI shows sequential activation
            session_manager.update_task_status(session_id, task.id, TaskStatus.IN_PROGRESS)
            sprints_dict = session_manager.get_sprints_dict(session_id)
            await agent_bus.send_sprint_update(sprints_dict)

            await agent_bus.publish(task.assigned_to.value, {
                "task": task.description,
                "task_id": task.id,
                "session_id": session_id,
                "from_agent": "project_manager",
                "project_name": project_name,
                "original_request": content,
                "output_type": template["output_type"],
            })

        return (
            f"# 🎯 Project Kickoff: **{project_name}**\n\n"
            f"Excellent! I've analyzed your requirements and created **Sprint 1** with 6 parallel tasks. "
            f"Your team is now activated:\n\n"
            f"| Agent | Task | Priority |\n"
            f"|-------|------|----------|\n"
            f"| 🎨 Designer | Design System & Architecture | 🔴 High |\n"
            f"| ⚛️ Frontend Dev | UI Component Development | 🔴 High |\n"
            f"| 🔧 Backend Dev | API & Database Layer | 🔴 High |\n"
            f"| 🧪 QA Tester | Test Suite Creation | 🟡 Medium |\n"
            f"| 🔍 SEO Specialist | SEO & Content Strategy | 🟡 Medium |\n"
            f"| 🏢 Virtual CEO | Strategic Planning | 🟢 Low |\n\n"
            f"Watch the **Live Status** panel on the right — agents are now working! "
            f"I'll synthesize all results and report back when the sprint is complete."
        )

    async def _llm_plan(self, content: str, session_id: str) -> str:
        """Real OpenAI-backed planning (requires OPENAI_API_KEY)."""
        try:
            resp = await _openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "You are a Senior Project Manager AI at a software agency. "
                        "Reply with a concise markdown-formatted project plan, sprint breakdown, "
                        "and task assignments for the 6-agent team: Designer, FrontendDev, "
                        "BackendDev, QATester, SEOSpecialist, VirtualCEO."
                    )},
                    {"role": "user", "content": content},
                ],
                max_tokens=800,
            )
            pm_reply = resp.choices[0].message.content
        except Exception as e:
            pm_reply = f"⚠️ LLM error: {e}. Falling back to structured mock."
            pm_reply += "\n\n" + await self._mock_plan(content, session_id)
        return pm_reply
