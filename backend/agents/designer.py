"""UI/UX Designer Agent — generates design systems, wireframes, and component specs."""

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent


DESIGN_OUTPUTS = {
    "default": """## 🎨 Design System Report

### Color Palette
```css
:root {
  --primary:      #6C63FF;   /* Electric Violet */
  --primary-dark: #4B44CC;
  --accent:       #FF6584;   /* Coral Pop */
  --success:      #43D9AD;
  --warning:      #FFB86C;
  --bg-dark:      #0D0E1A;
  --bg-card:      #1A1B2E;
  --bg-glass:     rgba(255,255,255,0.05);
  --text-primary: #E8E9F3;
  --text-muted:   #6B7280;
}
```

### Typography
- **Display**: `Syne` (900) — hero headings
- **Heading**: `Inter` (700/600) — section titles  
- **Body**: `Inter` (400/500) — content & labels
- **Code**: `JetBrains Mono` (400) — code blocks

### Component Architecture
1. **Navigation** — sticky glass-morphism header with blur
2. **Hero Section** — full-viewport gradient with animated mesh
3. **Feature Cards** — hover-lift cards with icon + description
4. **Dashboard** — two-panel split with real-time data charts
5. **Forms** — floating-label inputs with validation states
6. **Modals** — backdrop-blur overlays with spring animations

### Spacing System (`8px` base grid)
| Token | Value |
|-------|-------|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| 2xl | 48px |

### Responsive Breakpoints
- `sm`: 640px | `md`: 768px | `lg`: 1024px | `xl`: 1280px

### Wireframe — Dashboard Layout
```
┌─────────────────── Header (60px) ───────────────────┐
│  Logo    Nav Links                   CTA Button      │
├──────────────────────────────────────────────────────┤
│  Sidebar │        Main Content Area                  │
│  (240px) │  ┌──────────────────────────────────┐    │
│  • Chat  │  │  Agent Status Cards (Grid 3x2)   │    │
│  • Board │  │                                  │    │
│  • Logs  │  ├──────────────────────────────────┤    │
│          │  │  Sprint Kanban Board              │    │
│          │  └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```
""",
}


class DesignerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="designer",
            name="UI/UX Designer",
            emoji="🎨",
            role="Design Systems & Wireframes",
        )

    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        project_name = context.get("project_name", "the project")
        await asyncio.sleep(2.5)  # simulate design work

        return f"""## 🎨 Design System — {project_name}

### Color Palette
```css
:root {{
  --primary:      #6C63FF;   /* Electric Violet */
  --accent:       #FF6584;   /* Coral Pop */
  --success:      #43D9AD;
  --warning:      #FFB86C;
  --bg-dark:      #0D0E1A;
  --bg-card:      #1A1B2E;
  --text-primary: #E8E9F3;
}}
```

### Typography Stack
- **Headings**: `Syne` 900 — bold identity
- **Body**: `Inter` 400/500 — legibility at scale
- **Code**: `JetBrains Mono` 400

### Component Inventory (14 Components)
1. `<Navbar>` — sticky glassmorphism, blur backdrop
2. `<HeroSection>` — animated gradient mesh background
3. `<FeatureCard>` — hover-lift with micro-animation
4. `<DataChart>` — real-time line/bar chart
5. `<AgentCard>` — status badge + live output preview
6. `<ChatBubble>` — role-aware message bubble
7. `<SprintBoard>` — drag-drop Kanban
8. `<TaskCard>` — priority-colored task item
9. `<StatusBadge>` — animated pulse for live states
10. `<InputField>` — floating label, validation states
11. `<Modal>` — backdrop blur overlay
12. `<Sidebar>` — collapsible navigation
13. `<Avatar>` — agent emoji + online indicator
14. `<CodeBlock>` — syntax-highlighted output

### Wireframes Delivered
✅ Dashboard layout (desktop + mobile)
✅ Chat panel interaction flow
✅ Sprint board states (empty/active/complete)
✅ Agent card states (idle/thinking/working/done/error)

### Design Tokens Export
Ready for Figma, CSS custom properties, and Tailwind config.
"""
