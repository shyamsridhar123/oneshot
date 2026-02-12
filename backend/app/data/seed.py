"""Seed script to populate the database with NotContosso social media data and embeddings."""

import asyncio
import json
import uuid
from pathlib import Path

from app.models.database import (
    AsyncSessionLocal,
    init_db,
    KnowledgeItem,
    Engagement,
)
from app.services.llm_service import get_llm_service

# Path to brand data files
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


# ============ Social Media Campaign History ============
# These populate the engagements table so the agents can reference
# past campaign performance when strategizing new content.

SAMPLE_CAMPAIGNS = [
    {
        "client_name": "NotContosso Inc.",
        "client_industry": "Technology",
        "engagement_type": "Product Launch Campaign",
        "description": "Multi-platform social media campaign for AI Collaboration Suite v3.0 launch. Coordinated announcements across LinkedIn, Twitter/X, and Instagram with a phased rollout: teaser week, launch day blitz, and sustained engagement. Leveraged founder storytelling, behind-the-scenes content, and data-driven thought leadership.",
        "outcomes": "22K LinkedIn impressions on launch post, 25K Twitter impressions on founder thread, 5.1% Instagram engagement rate, 40% increase in website traffic from social, 150 inbound demo requests attributed to social",
        "team_members": ["Social Media Manager", "Content Strategist", "Graphic Designer", "VP Marketing"],
        "frameworks_used": ["Multi-Platform Launch Playbook", "Engagement Ladder Framework", "Brand Voice Guidelines"],
        "status": "completed",
        "days_ago": 30,
    },
    {
        "client_name": "NotContosso Inc.",
        "client_industry": "Technology",
        "engagement_type": "Thought Leadership Series",
        "description": "6-week LinkedIn thought leadership campaign positioning NotContosso's CEO as an authority on human-AI collaboration. Published weekly long-form posts with data from 200+ enterprise deployments. Each post followed the contrarian-hook + data-proof + CTA formula that drove viral engagement.",
        "outcomes": "5.8% average engagement rate (vs. 2% industry avg), 1 viral post (22K impressions, 340 shares), 3 speaking invitations from conference organizers, 28% increase in CEO LinkedIn followers",
        "team_members": ["Content Strategist", "CEO", "Data Analyst", "Social Media Manager"],
        "frameworks_used": ["Thought Leadership Funnel", "Data Storytelling Framework", "Executive Voice Playbook"],
        "status": "completed",
        "days_ago": 60,
    },
    {
        "client_name": "NotContosso Inc.",
        "client_industry": "Technology",
        "engagement_type": "Developer Community Campaign",
        "description": "Twitter/X-focused campaign targeting developers and ML practitioners. Published technical threads, hot takes on AI industry trends, and BuildInPublic content. Engaged with developer community through replies, quote tweets, and collaborative threads with tech influencers.",
        "outcomes": "6.2% engagement rate on viral thread (25K impressions), 580 retweets on top thread, 1200 new developer followers, 45 community-generated code contributions, featured in 3 developer newsletters",
        "team_members": ["Developer Advocate", "Social Media Manager", "Engineering Lead"],
        "frameworks_used": ["Developer Community Playbook", "Thread Optimization Guide", "Community Engagement Ladder"],
        "status": "completed",
        "days_ago": 45,
    },
    {
        "client_name": "NotContosso Inc.",
        "client_industry": "Technology",
        "engagement_type": "Employer Branding Campaign",
        "description": "Instagram-led employer branding initiative showcasing NotContosso culture, team celebrations, and day-in-the-life content. Used carousel posts, reels, and stories to highlight the human side of building AI. Combined authentic team moments with hiring CTAs.",
        "outcomes": "5.1% average engagement rate on Instagram, 35% increase in career page visits from social, 2x increase in inbound applications, 4.8% engagement on team celebration carousel, top-performing content: behind-the-scenes QA testing celebration",
        "team_members": ["Social Media Manager", "People & Culture Lead", "Graphic Designer"],
        "frameworks_used": ["Employer Brand Framework", "Authentic Content Guide", "Instagram Carousel Best Practices"],
        "status": "completed",
        "days_ago": 20,
    },
    {
        "client_name": "NotContosso Inc.",
        "client_industry": "Technology",
        "engagement_type": "Healthcare Vertical Campaign",
        "description": "Targeted LinkedIn campaign promoting NotContosso's healthcare AI deployment success. Combined vulnerability-driven storytelling (what was hard) with proof-of-results content. Featured customer testimonial snippets and compliance journey narrative.",
        "outcomes": "3.9% engagement rate, 18K impressions, 156 comments (high conversation), 89 shares, 12 inbound leads from healthcare sector, 3 healthcare media mentions",
        "team_members": ["Content Strategist", "Healthcare Sales Lead", "Social Media Manager"],
        "frameworks_used": ["Vertical Marketing Playbook", "Customer Story Framework", "Compliance-Safe Content Guide"],
        "status": "completed",
        "days_ago": 15,
    },
]


# ============ Social Media Strategies & Playbooks ============
# Knowledge items the agents can retrieve to inform content strategy.

SAMPLE_STRATEGIES = [
    {
        "title": "Multi-Platform Content Strategy",
        "category": "strategy",
        "industry": "Technology",
        "content": """NotContosso's cross-platform content strategy for maximum reach and engagement:

**Platform Roles:**
- **LinkedIn:** Authority building — thought leadership, customer success, industry analysis
- **Twitter/X:** Community building — developer engagement, quick takes, threads, real-time conversation
- **Instagram:** Culture building — team stories, behind-the-scenes, employer branding, visual storytelling

**Content Repurposing Flow:**
1. Start with a core insight or story
2. LinkedIn: Full-length thought leadership post (1300-3000 chars)
3. Twitter/X: Distilled thread (3-8 tweets) or hot take
4. Instagram: Visual carousel or behind-the-scenes reel

**Cross-Platform Rules:**
- Never post identical content across platforms
- Adapt tone and format to each platform's audience
- Maintain 24-48 hour gap between platforms for same topic
- Track which platform drives highest engagement per topic type""",
        "tags": ["strategy", "multi-platform", "content planning", "social media"],
    },
    {
        "title": "Engagement Optimization Playbook",
        "category": "strategy",
        "industry": "Technology",
        "content": """Data-driven engagement optimization based on NotContosso's historical performance:

**Top-Performing Post Formats:**
1. Contrarian hooks + data proof (avg 5.8% engagement)
2. Thread format with numbered insights (avg 6.2% engagement)
3. Behind-the-scenes team moments (avg 5.1% engagement)
4. Hot takes with actionable advice (avg 4.5% engagement)
5. Product data with customer proof points (avg 4.2% engagement)

**Optimal Posting Times (PST):**
- LinkedIn: Tuesday-Thursday, 8:30-9:30 AM
- Twitter/X: Monday-Friday, 10:00 AM-1:00 PM
- Instagram: Tuesday-Friday, 12:00-5:00 PM

**Engagement Drivers:**
- Ask a specific question (not generic "what do you think?")
- Include 2-3 concrete data points
- Use first-person storytelling for authenticity
- Reference trending industry topics within 24-48 hours
- Carousel/thread formats drive 2-3x more saves and shares""",
        "tags": ["engagement", "optimization", "analytics", "best practices"],
    },
    {
        "title": "Brand Voice & Tone Guide",
        "category": "strategy",
        "industry": "Technology",
        "content": """NotContosso's brand voice framework for consistent social media communication:

**Voice Pillars:**
1. Professional yet approachable — experts who don't talk down
2. Innovation-forward — lead with what's new and next
3. Human-centered — technology serves people

**Tone Calibration by Context:**
- Product announcements: Confident + excited (not hype-y)
- Thought leadership: Authoritative + conversational
- Community engagement: Warm + curious
- Team culture: Authentic + celebratory
- Industry commentary: Insightful + balanced

**Language DOs:**
- "We've learned..." (not "We've revolutionized...")
- "Our data shows..." (not "Everyone knows...")
- "Here's what worked..." (not "Here's the secret...")
- Use specific numbers over vague claims
- Write as a knowledgeable peer, not a vendor

**Language DON'Ts:**
- Superlatives without data ("best ever", "revolutionary")
- Buzzword soup ("synergy", "paradigm shift", "game-changer")
- Competitor bashing (even subtle)
- Unsubstantiated claims about AI capabilities""",
        "tags": ["brand voice", "tone", "writing guide", "messaging"],
    },
    {
        "title": "Hashtag Strategy & Performance",
        "category": "strategy",
        "industry": "Technology",
        "content": """NotContosso's hashtag strategy based on reach and engagement data:

**Always-On Tags (every post):**
- #NotContosso (branded, tracking)
- #AIInnovation (category, reach)

**Platform-Specific High Performers:**
LinkedIn (use 3-5 per post):
- #EnterpriseAI (18K avg reach)
- #FutureOfWork (22K avg reach)
- #DigitalTransformation (15K avg reach)
- #AICollaboration (8K avg reach, but high engagement)
- #TechLeadership (12K avg reach)

Twitter/X (use 2-3 per post):
- #AI (broad reach)
- #BuildInPublic (dev community)
- #DevCommunity (technical audience)
- #TechTuesday (recurring series)
- #MLOps (niche, high-intent)

Instagram (use 8-12 per post):
- #TechLife #TeamNotContosso #BTS #StartupLife #AICompany
- Supplement with trending and topic-specific tags

**Rules:**
- Branded tags first, category tags second, trending tags last
- Monitor weekly for declining reach tags
- Rotate 2-3 experimental tags per week""",
        "tags": ["hashtags", "reach", "social media", "tagging strategy"],
    },
    {
        "title": "Content Calendar Planning Framework",
        "category": "strategy",
        "industry": "Technology",
        "content": """Weekly content planning framework for NotContosso's social media:

**Content Mix (per week):**
- Announcements: 20% — Product launches, partnerships, milestones
- Thought Leadership: 30% — Industry insights, data-backed opinions, trend analysis
- Engagement: 25% — Questions, polls, threads, community replies
- Culture: 25% — Team stories, behind-the-scenes, hiring, events

**Weekly Cadence:**
- LinkedIn: 3-4 posts/week (Tue/Wed/Thu optimal)
- Twitter/X: 1-2 posts/day (plus engagement replies)
- Instagram: 3-5 posts/week (Tue-Fri optimal)

**Planning Process:**
1. Monday: Review previous week metrics, identify trending topics
2. Tuesday: Draft week's content based on calendar and trending opportunities
3. Wednesday-Friday: Publish and actively engage in comments/replies
4. Friday: Capture any behind-the-scenes or celebration content

**Seasonal & Event Calendar:**
- Major tech conferences (CES, SXSW, Google I/O, Build)
- Industry awareness weeks/days
- Company milestones and anniversaries
- Product release cycles""",
        "tags": ["content calendar", "planning", "cadence", "editorial"],
    },
    {
        "title": "Social Media Analytics & KPIs",
        "category": "strategy",
        "industry": "Technology",
        "content": """NotContosso's social media performance measurement framework:

**Primary KPIs:**
- Engagement Rate: Target 4%+ (LinkedIn), 3.5%+ (Twitter), 5%+ (Instagram)
- Impressions Growth: 15% month-over-month
- Follower Growth: 10% month-over-month
- Click-Through Rate: 2%+ on posts with links
- Share of Voice: Track vs. 3 key competitors

**Content Performance Tiers:**
- Viral: >5% engagement rate, >20K impressions
- High: 3-5% engagement rate, >10K impressions
- Standard: 2-3% engagement rate, >5K impressions
- Low: <2% engagement rate, <5K impressions (review and learn)

**Attribution Metrics:**
- Social → Website traffic (UTM tracking)
- Social → Demo requests (attributed leads)
- Social → Job applications (career page referrals)
- Social → Brand mentions and sentiment

**Reporting Cadence:**
- Daily: Quick engagement check, respond to comments
- Weekly: Content performance review, trending topic scan
- Monthly: Full analytics report, strategy adjustment
- Quarterly: Competitive analysis, strategy refresh""",
        "tags": ["analytics", "kpis", "metrics", "performance", "reporting"],
    },
]


async def generate_embedding(llm_service, text: str) -> list[float]:
    """Generate embedding for text using Azure OpenAI."""
    try:
        embedding = await llm_service.embed(text)
        return embedding
    except Exception as e:
        print(f"Warning: Failed to generate embedding: {e}")
        return []


async def seed_database(skip_embeddings: bool = False):
    """Seed the database with NotContosso social media data.

    Seeds campaign history, social media strategies, brand guidelines,
    past posts, and content calendar for the Social Media Command Center.
    """
    print("Starting social media data seeding...")

    await init_db()
    print("Database initialized")

    # Get LLM service for embeddings
    llm_service = None
    embed_func = None
    if not skip_embeddings:
        try:
            llm_service = get_llm_service()

            async def _embed(text: str) -> list[float]:
                return await generate_embedding(llm_service, text)

            embed_func = _embed
            print("Embedding service available")
        except Exception as e:
            print(f"Embeddings disabled: {e}")
    else:
        print("Skipping embeddings (--no-embeddings flag)")

    async with AsyncSessionLocal() as db:
        # 1. Seed campaign history (engagements table)
        print("\nSeeding campaign history...")
        for camp in SAMPLE_CAMPAIGNS:
            embedding = []
            if embed_func:
                embed_text = f"{camp['engagement_type']} {camp['description']}"
                embedding = await embed_func(embed_text)

            from datetime import datetime, timedelta

            days = camp["days_ago"]
            engagement = Engagement(
                id=str(uuid.uuid4()),
                client_name=camp["client_name"],
                client_industry=camp["client_industry"],
                engagement_type=camp["engagement_type"],
                description=camp["description"],
                outcomes=camp["outcomes"],
                team_members=camp["team_members"],
                frameworks_used=camp["frameworks_used"],
                status=camp["status"],
                start_date=datetime.utcnow() - timedelta(days=days + 30),
                end_date=datetime.utcnow() - timedelta(days=days),
                embedding=embedding,
            )
            db.add(engagement)
            print(f"  + {camp['engagement_type']}")

        # 2. Seed social media strategies (knowledge_items table)
        print("\nSeeding social media strategies...")
        for strat in SAMPLE_STRATEGIES:
            embedding = []
            if embed_func:
                embed_text = f"{strat['title']} {strat['content']}"
                embedding = await embed_func(embed_text)

            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=strat["title"],
                content=strat["content"],
                category=strat["category"],
                industry=strat["industry"],
                tags=strat["tags"],
                embedding=embedding,
            )
            db.add(item)
            print(f"  + {strat['title']}")

        # 3. Load brand guidelines
        brand_guidelines_path = DATA_DIR / "brand_guidelines.md"
        if brand_guidelines_path.exists():
            print("\nSeeding brand guidelines...")
            content = brand_guidelines_path.read_text(encoding="utf-8")
            embedding = []
            if embed_func:
                embedding = await embed_func(
                    f"NotContosso brand guidelines voice tone style {content[:500]}"
                )

            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title="NotContosso Inc. — Brand & Social Media Guidelines",
                content=content,
                category="brand_guidelines",
                industry="Technology",
                tags=["brand", "guidelines", "social media", "voice", "tone", "NotContosso"],
                embedding=embedding,
            )
            db.add(item)
            print("  + Brand guidelines loaded")
        else:
            print(f"  Warning: Brand guidelines not found at {brand_guidelines_path}")

        # 4. Load past posts — one knowledge item per post for granular retrieval
        past_posts_path = DATA_DIR / "past_posts.json"
        if past_posts_path.exists():
            print("\nSeeding past post performance data...")
            posts = json.loads(past_posts_path.read_text(encoding="utf-8"))

            for post in posts:
                embedding = []
                if embed_func:
                    embed_text = (
                        f"{post['platform']} post performance:{post['performance']} "
                        f"engagement:{post['engagement_rate']}% {post['content'][:200]}"
                    )
                    embedding = await embed_func(embed_text)

                success_factors = post.get("success_factors", [])
                item = KnowledgeItem(
                    id=str(uuid.uuid4()),
                    title=f"Past Post: {post['platform'].title()} ({post['date']}) — {post['performance']}",
                    content=json.dumps(post, indent=2),
                    category="past_post",
                    industry="Technology",
                    tags=[
                        "past post",
                        post["platform"],
                        post["performance"],
                        "social media",
                        "engagement",
                    ] + success_factors[:3],
                    embedding=embedding,
                )
                db.add(item)
                print(f"  + {post['platform'].title()} post ({post['date']}) — {post['performance']}")
        else:
            print(f"  Warning: Past posts not found at {past_posts_path}")

        # 5. Load content calendar
        calendar_path = DATA_DIR / "content_calendar.json"
        if calendar_path.exists():
            print("\nSeeding content calendar...")
            calendar_content = calendar_path.read_text(encoding="utf-8")
            calendar_data = json.loads(calendar_content)
            embedding = []
            if embed_func:
                embedding = await embed_func(
                    f"NotContosso content calendar weekly schedule {calendar_data.get('theme', '')}",
                )

            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=f"Content Calendar: Week of {calendar_data.get('week_of', 'template')}",
                content=calendar_content,
                category="content_calendar",
                industry="Technology",
                tags=["calendar", "schedule", "content plan", "social media", "weekly"],
                embedding=embedding,
            )
            db.add(item)
            print("  + Content calendar loaded")
        else:
            print(f"  Warning: Content calendar not found at {calendar_path}")

        await db.commit()

    # Count totals
    past_posts_count = len(json.loads((DATA_DIR / "past_posts.json").read_text())) if (DATA_DIR / "past_posts.json").exists() else 0
    print("\nSocial media data seeding complete!")
    print(f"  - {len(SAMPLE_CAMPAIGNS)} campaign history entries")
    print(f"  - {len(SAMPLE_STRATEGIES)} strategy playbooks")
    print(f"  - 1 brand guidelines document")
    print(f"  - {past_posts_count} past post performance records")
    print(f"  - 1 content calendar")


if __name__ == "__main__":
    asyncio.run(seed_database())
