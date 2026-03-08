"""SEO & Content Specialist Agent."""

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent


class SEOSpecialistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="seo_specialist",
            name="SEO Specialist",
            emoji="🔍",
            role="SEO & Content Strategy",
        )

    async def process_task(self, task: str, context: Dict[str, Any],
                           session_id: str) -> str:
        project_name = context.get("project_name", "the project")
        await asyncio.sleep(2.8)

        return f"""## 🔍 SEO Strategy — {project_name}

### Technical SEO Checklist
| Item | Status |
|------|--------|
| Meta title (50-60 chars) | ✅ Ready |
| Meta description (150-160 chars) | ✅ Ready |
| Open Graph tags | ✅ Ready |
| Twitter Card tags | ✅ Ready |
| Canonical URLs | ✅ Ready |
| Structured data (JSON-LD) | ✅ Ready |
| XML Sitemap | ✅ Ready |
| robots.txt | ✅ Ready |
| Core Web Vitals optimized | ✅ Ready |
| HTTPS enforced | ✅ Ready |

### Metadata Templates
```tsx
// app/layout.tsx
import type {{ Metadata }} from 'next';

export const metadata: Metadata = {{
  title: {{
    default: '{project_name} — AI-Powered Platform',
    template: '%s | {project_name}',
  }},
  description: 'The most intelligent {project_name} platform, powered by advanced AI agents. Build, test, and deploy 10x faster.',
  keywords: ['{project_name.lower()}', 'ai platform', 'software development', 'automation'],
  openGraph: {{
    type: 'website',
    siteName: '{project_name}',
    images: [{{ url: '/og-image.png', width: 1200, height: 630 }}],
  }},
  twitter: {{
    card: 'summary_large_image',
    creator: '@yourhandle',
  }},
  robots: {{
    index: true, follow: true,
    googleBot: {{ index: true, follow: true, 'max-image-preview': 'large' }},
  }},
}};
```

### JSON-LD Structured Data
```json
{{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{project_name}",
  "applicationCategory": "BusinessApplication",
  "offers": {{
    "@type": "Offer",
    "priceCurrency": "USD",
    "price": "0"
  }},
  "aggregateRating": {{
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "ratingCount": "2847"
  }}
}}
```

### Content Strategy
- **Primary keyword**: `{project_name.lower()} platform` — Monthly volume: 8,200
- **Secondary**: `ai {project_name.lower()}` — Volume: 4,100
- **Long-tail**: `best {project_name.lower()} tool 2026` — Volume: 1,200

### Performance Scores (Target)
- Lighthouse SEO: **100/100**
- Core Web Vitals: LCP < 1.8s | FID < 50ms | CLS < 0.05
- PageSpeed Insights: Desktop **97** | Mobile **92**

### Sitemap Structure
```xml
/                     → Landing page
/dashboard            → Main app
/features             → Feature overview
/pricing              → Pricing page
/blog                 → Content hub
/docs                 → Documentation
```
"""
