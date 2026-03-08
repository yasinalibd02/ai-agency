"""Frontend Developer Agent — generates Next.js/React code."""

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent


class FrontendDevAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="frontend_dev",
            name="Frontend Developer",
            emoji="⚛️",
            role="Next.js / React Development",
        )

    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        project_name = context.get("project_name", "the project")
        await asyncio.sleep(3.5)

        return f"""## ⚛️ Frontend Implementation — {project_name}

### Stack
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + CSS Modules
- **Animation**: Framer Motion
- **State**: Zustand
- **Data Fetching**: TanStack Query

### File Structure
```
app/
├── layout.tsx          ← Root layout with providers
├── page.tsx            ← Landing page
├── dashboard/
│   └── page.tsx        ← Main dashboard
└── globals.css

components/
├── ui/
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Badge.tsx
├── dashboard/
│   ├── ChatPanel.tsx
│   ├── AgentBoard.tsx
│   └── SprintKanban.tsx
└── layout/
    ├── Navbar.tsx
    └── Sidebar.tsx
```

### Key Component — AgentCard
```tsx
'use client';
import {{ motion }} from 'framer-motion';

interface AgentCardProps {{
  name: string; emoji: string;
  status: 'idle' | 'thinking' | 'working' | 'done' | 'error';
  currentTask?: string; lastOutput?: string;
}}

export function AgentCard({{ name, emoji, status, currentTask, lastOutput }}: AgentCardProps) {{
  const statusColors = {{
    idle: 'bg-gray-500', thinking: 'bg-yellow-400 animate-pulse',
    working: 'bg-blue-400 animate-pulse', done: 'bg-green-400', error: 'bg-red-500',
  }};
  return (
    <motion.div
      className="glass-card p-4 rounded-xl relative overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, translateY: -4 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className="flex items-center gap-3 mb-3">
        <span className="text-3xl">{{emoji}}</span>
        <div>
          <h3 className="font-semibold text-white">{{name}}</h3>
          <span className={{`inline-block px-2 py-0.5 rounded-full text-xs text-white ${{statusColors[status]}}`}}>
            {{status.toUpperCase()}}
          </span>
        </div>
      </div>
      {{currentTask && (
        <p className="text-sm text-gray-400 mb-2 truncate">📌 {{currentTask}}</p>
      )}}
      {{lastOutput && (
        <div className="text-xs font-mono text-green-400 bg-black/30 rounded p-2 max-h-20 overflow-hidden">
          {{lastOutput.slice(0, 150)}}...
        </div>
      )}}
    </motion.div>
  );
}}
```

### Performance Optimizations
- ✅ Dynamic imports for heavy components
- ✅ Image optimization via `next/image`
- ✅ Server components where possible
- ✅ Route groups for layout isolation
- ✅ Virtualized lists for chat history

### Estimated Lines of Code: ~1,800 LOC
### Estimated Completion: 3 days
"""
