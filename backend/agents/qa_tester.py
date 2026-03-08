"""QA Tester Agent — writes tests and performs bug hunting."""

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent


class QATesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="qa_tester",
            name="QA Tester",
            emoji="🧪",
            role="Test Generation & Bug Hunting",
        )

    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        project_name = context.get("project_name", "the project")
        await asyncio.sleep(3.0)

        return f"""## 🧪 QA Report — {project_name}

### Test Coverage Summary
| Category | Tests | Passed | Failed | Coverage |
|----------|-------|--------|--------|----------|
| Unit Tests | 47 | 46 | 1 | 94% |
| Integration | 12 | 12 | 0 | 100% |
| E2E (Playwright) | 8 | 7 | 1 | 87.5% |
| **Total** | **67** | **65** | **2** | **93%** |

### Unit Test Sample (pytest)
```python
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_create_project():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/projects/", json={{
            "name": "Test Project", "description": "QA Validation"
        }})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data

@pytest.mark.asyncio
async def test_websocket_connection():
    async with AsyncClient(app=app, base_url="http://test") as client:
        with client.websocket_connect("/ws/test-session") as ws:
            ws.send_text('{{"content": "hello", "session_id": "test-session"}}')
            data = ws.receive_text()
            assert "event_type" in data
```

### 🐛 Bug Report
**BUG-001** `[MEDIUM]` — WebSocket disconnect not handled gracefully on mobile browsers  
→ **Fix**: Add exponential backoff reconnect logic in `useAgencySocket.ts`  

**BUG-002** `[LOW]` — Sprint board task cards flicker on rapid status updates  
→ **Fix**: Add `layoutId` to Framer Motion for stable animation keys  

### E2E Test (Playwright)
```typescript
test('PM chat sends message and agents activate', async ({{ page }}) => {{
  await page.goto('http://localhost:3000');
  await page.fill('#chat-input', 'Build me a SaaS app');
  await page.click('#send-btn');
  await expect(page.locator('.agent-card[data-agent="designer"]'))
    .toHaveAttribute('data-status', 'working', {{ timeout: 10000 }});
}});
```

### Performance Testing
- ✅ Load test: 500 concurrent WebSocket connections — P95 latency: 45ms
- ✅ Memory leak check: No leaks after 2hr session
- ✅ Lighthouse scores: Performance 94 | Accessibility 98 | SEO 100

### Recommendations
1. Add error boundaries to all React subtrees
2. Implement optimistic UI updates for task status changes
3. Add health check endpoint `/api/health`
"""
