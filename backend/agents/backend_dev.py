"""Backend Developer Agent — generates FastAPI/Node.js code and DB schemas."""

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent


class BackendDevAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="backend_dev",
            name="Backend Developer",
            emoji="🔧",
            role="FastAPI / Node.js Development",
        )

    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        project_name = context.get("project_name", "the project")
        await asyncio.sleep(4.0)

        return f"""## 🔧 Backend Architecture — {project_name}

### Stack
- **API Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL + SQLAlchemy (async)
- **Cache**: Redis 7
- **Auth**: JWT + OAuth2 via `python-jose`
- **Queue**: Celery + Redis broker
- **Container**: Docker + Docker Compose

### API Endpoints
```python
# Core Routes
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

GET    /api/projects
POST   /api/projects
GET    /api/projects/{{project_id}}
PATCH  /api/projects/{{project_id}}
DELETE /api/projects/{{project_id}}

GET    /api/projects/{{project_id}}/tasks
POST   /api/projects/{{project_id}}/tasks
PATCH  /api/tasks/{{task_id}}

WebSocket /ws/{{session_id}}
```

### Database Schema
```sql
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       VARCHAR(255) UNIQUE NOT NULL,
  name        VARCHAR(100),
  role        VARCHAR(50) DEFAULT 'owner',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE projects (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(255) NOT NULL,
  description TEXT,
  owner_id    UUID REFERENCES users(id),
  status      VARCHAR(50) DEFAULT 'active',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tasks (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id  UUID REFERENCES projects(id),
  title       VARCHAR(255) NOT NULL,
  assigned_to VARCHAR(100),  -- agent_id
  status      VARCHAR(50) DEFAULT 'todo',
  priority    VARCHAR(20) DEFAULT 'medium',
  result      TEXT,
  sprint      INTEGER DEFAULT 1,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### Sample FastAPI Route
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(**data.model_dump(), owner_id=current_user.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project
```

### Security
- ✅ Rate limiting (slowapi)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS with allowlist
- ✅ HTTPS enforcement
- ✅ Secret rotation via environment variables

### Estimated LOC: ~2,200 | Completion: 4 days
"""
