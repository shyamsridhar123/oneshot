"""Seed script to populate the database with sample data and embeddings."""

import asyncio
import uuid
from datetime import datetime, timedelta

from app.models.database import (
    AsyncSessionLocal,
    init_db,
    KnowledgeItem,
    Engagement,
)
from app.services.llm_service import get_llm_service


# ============ Sample Engagements ============

SAMPLE_ENGAGEMENTS = [
    {
        "client_name": "Global Manufacturing Inc",
        "client_industry": "Manufacturing",
        "engagement_type": "Digital Transformation",
        "description": "End-to-end supply chain digitization including IoT sensor integration, predictive maintenance analytics, and digital twin implementation for three manufacturing facilities. Deployed real-time monitoring dashboards and automated quality control systems.",
        "outcomes": "30% reduction in inventory costs, 25% improvement in delivery times, 40% decrease in unplanned downtime, $15M annual savings identified",
        "team_members": ["John Partner", "Sarah Manager", "Mike Analyst", "Lisa Consultant"],
        "frameworks_used": ["Digital Maturity Assessment", "Supply Chain 4.0 Framework", "Change Management Playbook"],
        "status": "completed",
        "days_ago": 180,
    },
    {
        "client_name": "HealthCare Partners Network",
        "client_industry": "Healthcare",
        "engagement_type": "Post-Merger Integration",
        "description": "Integration of two regional healthcare systems following $2.5B merger. Scope included IT systems consolidation, clinical process harmonization, workforce integration planning, and culture alignment initiatives across 12 hospitals and 50+ clinics.",
        "outcomes": "$50M synergies captured in year 1, 95% staff retention, unified EHR platform deployed, 20% reduction in administrative overhead",
        "team_members": ["Lisa Partner", "Tom Manager", "Amy Analyst", "David Consultant"],
        "frameworks_used": ["PMI Playbook", "Healthcare Synergy Model", "Cultural Integration Framework"],
        "status": "completed",
        "days_ago": 120,
    },
    {
        "client_name": "TechCorp Solutions",
        "client_industry": "Technology",
        "engagement_type": "Growth Strategy",
        "description": "Comprehensive growth strategy for B2B SaaS company seeking to expand from $50M to $200M ARR. Analyzed market opportunities, pricing optimization, go-to-market strategy, and M&A targets for inorganic growth.",
        "outcomes": "Identified 3 adjacent market opportunities worth $500M TAM, new pricing model projected to increase ARPU by 35%, M&A roadmap with 5 priority targets",
        "team_members": ["Robert Partner", "Jennifer Manager", "Kevin Analyst"],
        "frameworks_used": ["Growth Diagnostic", "Pricing Excellence Framework", "M&A Target Screening"],
        "status": "completed",
        "days_ago": 90,
    },
    {
        "client_name": "RetailMax Corporation",
        "client_industry": "Retail",
        "engagement_type": "Customer Experience Transformation",
        "description": "Omnichannel customer experience redesign for national retailer with 500+ stores. Implemented unified commerce platform, personalization engine, mobile app enhancement, and store associate enablement tools.",
        "outcomes": "25% increase in customer satisfaction (NPS), 18% improvement in conversion rates, 40% growth in mobile app engagement, $80M incremental revenue in year 1",
        "team_members": ["Michelle Partner", "Brian Manager", "Susan Analyst", "Chris Consultant"],
        "frameworks_used": ["Customer Journey Mapping", "Omnichannel Maturity Model", "Personalization at Scale"],
        "status": "completed",
        "days_ago": 60,
    },
    {
        "client_name": "EnergyFirst Utilities",
        "client_industry": "Energy & Utilities",
        "engagement_type": "Operational Excellence",
        "description": "Lean operations transformation for regional utility serving 2M customers. Focus areas included field service optimization, grid maintenance efficiency, customer service redesign, and workforce planning.",
        "outcomes": "22% improvement in first-time fix rates, 30% reduction in truck rolls, 15% decrease in call center volume, $25M annual cost savings",
        "team_members": ["Daniel Partner", "Rachel Manager", "Jason Analyst"],
        "frameworks_used": ["Lean Operations Playbook", "Field Service Excellence", "Utility Customer Experience"],
        "status": "completed",
        "days_ago": 150,
    },
    {
        "client_name": "FinServ Global Bank",
        "client_industry": "Financial Services",
        "engagement_type": "Risk & Compliance Modernization",
        "description": "End-to-end risk management and compliance transformation including regulatory reporting automation, AML/KYC process redesign, and risk data infrastructure modernization for Tier 1 bank.",
        "outcomes": "60% reduction in false positive alerts, 40% faster regulatory reporting, $100M reduction in compliance costs over 3 years, improved regulatory ratings",
        "team_members": ["Patricia Partner", "Mark Manager", "Emily Analyst", "Andrew Consultant"],
        "frameworks_used": ["Risk Operating Model", "RegTech Implementation", "Data Quality Framework"],
        "status": "completed",
        "days_ago": 200,
    },
    {
        "client_name": "Pharma Innovations Ltd",
        "client_industry": "Life Sciences",
        "engagement_type": "R&D Productivity",
        "description": "R&D operating model redesign for mid-size pharmaceutical company. Scope included portfolio optimization, clinical trial efficiency, AI-enabled drug discovery integration, and strategic partnerships strategy.",
        "outcomes": "20% reduction in clinical trial cycle times, 3 AI-enabled discovery programs launched, partnership framework with 2 academic institutions, improved pipeline probability of success",
        "team_members": ["William Partner", "Karen Manager", "Steven Analyst"],
        "frameworks_used": ["R&D Excellence Model", "Clinical Trial Optimization", "AI in Drug Discovery"],
        "status": "completed",
        "days_ago": 240,
    },
    {
        "client_name": "LogiTrans International",
        "client_industry": "Transportation & Logistics",
        "engagement_type": "Technology Modernization",
        "description": "Legacy systems modernization for global logistics provider. Migrated core TMS and WMS to cloud, implemented real-time tracking capabilities, and deployed customer self-service portal.",
        "outcomes": "99.9% system uptime (from 97%), 50% reduction in IT maintenance costs, real-time visibility for 100% of shipments, customer satisfaction up 30%",
        "team_members": ["George Partner", "Nancy Manager", "Paul Analyst", "Linda Consultant"],
        "frameworks_used": ["Cloud Migration Playbook", "API-First Architecture", "Customer Portal Design"],
        "status": "completed",
        "days_ago": 100,
    },
]


# ============ Sample Frameworks ============

SAMPLE_FRAMEWORKS = [
    {
        "title": "Digital Maturity Assessment",
        "category": "framework",
        "industry": None,
        "content": """A structured approach to evaluating an organization's digital capabilities across 6 dimensions:

1. **Strategy & Vision**: Digital strategy alignment, leadership commitment, innovation culture
2. **Customer Experience**: Digital channels, personalization, omnichannel integration
3. **Operations**: Process automation, data-driven decisions, agile ways of working
4. **Technology**: Cloud adoption, modern architecture, cybersecurity posture
5. **Data & Analytics**: Data governance, analytics capabilities, AI/ML readiness
6. **Organization & Culture**: Digital skills, change readiness, talent strategy

Assessment produces a maturity score (1-5) per dimension with prioritized roadmap.""",
        "tags": ["digital", "transformation", "assessment", "maturity"],
    },
    {
        "title": "Supply Chain 4.0 Framework",
        "category": "framework",
        "industry": "Manufacturing",
        "content": """Framework for next-generation supply chain transformation leveraging Industry 4.0 technologies:

**Core Components:**
- IoT-enabled visibility across end-to-end supply chain
- Predictive analytics for demand sensing and inventory optimization
- Digital twins for supply chain simulation and scenario planning
- Autonomous logistics and warehouse automation
- Blockchain for traceability and supplier collaboration

**Implementation Phases:**
1. Visibility Foundation (sensors, data integration)
2. Predictive Capabilities (ML models, analytics)
3. Automation & Optimization (robotics, autonomous systems)
4. Ecosystem Integration (supplier networks, customer integration)""",
        "tags": ["supply chain", "manufacturing", "iot", "automation"],
    },
    {
        "title": "PMI Playbook",
        "category": "framework",
        "industry": None,
        "content": """Post-Merger Integration playbook for successful deal value capture:

**Day 1 Readiness:**
- Legal entity integration requirements
- IT systems continuity
- Employee communications
- Customer/supplier notifications

**First 100 Days:**
- Synergy capture tracking and governance
- Integration Management Office setup
- Culture integration initiatives
- Quick wins identification and execution

**Value Capture Workstreams:**
- Revenue synergies (cross-sell, pricing, market expansion)
- Cost synergies (procurement, shared services, footprint)
- Capital synergies (working capital, capex optimization)

**Critical Success Factors:**
- Clear leadership and decision rights
- Dedicated integration resources
- Transparent communication
- Retention of key talent""",
        "tags": ["m&a", "integration", "synergies", "transformation"],
    },
    {
        "title": "Customer Journey Mapping",
        "category": "framework",
        "industry": "Retail",
        "content": """Methodology for understanding and optimizing end-to-end customer experiences:

**Journey Stages:**
1. Awareness & Discovery
2. Research & Consideration
3. Purchase & Transaction
4. Onboarding & Activation
5. Usage & Engagement
6. Support & Service
7. Loyalty & Advocacy

**For Each Stage, Map:**
- Customer goals and expectations
- Touchpoints and channels
- Pain points and friction
- Moments of truth
- Emotional journey
- Opportunities for improvement

**Outputs:**
- Visual journey maps
- Pain point prioritization matrix
- Quick wins and strategic initiatives
- Success metrics and KPIs""",
        "tags": ["customer experience", "journey", "retail", "cx"],
    },
    {
        "title": "Change Management Playbook",
        "category": "framework",
        "industry": None,
        "content": """Comprehensive approach to driving organizational change adoption:

**ADKAR Model Integration:**
- Awareness of need for change
- Desire to participate and support
- Knowledge of how to change
- Ability to implement new skills
- Reinforcement to sustain change

**Key Workstreams:**
1. Stakeholder Analysis & Engagement
2. Communications Strategy & Execution
3. Training & Capability Building
4. Change Champion Network
5. Resistance Management
6. Adoption Measurement

**Success Metrics:**
- Awareness levels (survey)
- Training completion rates
- Adoption metrics (system usage, process compliance)
- Performance outcomes""",
        "tags": ["change management", "adoption", "transformation", "culture"],
    },
    {
        "title": "Lean Operations Playbook",
        "category": "framework",
        "industry": None,
        "content": """Framework for operational excellence through lean principles:

**Core Principles:**
- Eliminate waste (muda) in all forms
- Continuous improvement (kaizen)
- Respect for people
- Just-in-time delivery
- Built-in quality (jidoka)

**Diagnostic Tools:**
- Value stream mapping
- Process capability analysis
- Root cause analysis (5 Whys, fishbone)
- Standard work documentation

**Implementation Approach:**
1. Current state assessment
2. Future state design
3. Pilot and iterate
4. Scale and sustain
5. Continuous improvement cycles

**Typical Results:**
- 20-40% productivity improvement
- 30-50% lead time reduction
- 50%+ quality defect reduction""",
        "tags": ["operations", "lean", "efficiency", "continuous improvement"],
    },
    {
        "title": "Growth Diagnostic",
        "category": "framework",
        "industry": None,
        "content": """Comprehensive growth strategy assessment framework:

**Growth Lever Analysis:**
1. Core Growth: Organic growth in existing markets
2. Adjacent Growth: New products, segments, or geographies
3. Transformational Growth: New business models, M&A

**Market Assessment:**
- Market sizing (TAM, SAM, SOM)
- Growth rate analysis
- Competitive dynamics
- Customer segmentation

**Capability Gaps:**
- Go-to-market capabilities
- Product/service development
- Operational scalability
- Talent and organization

**Output:**
- Growth opportunity matrix
- Prioritized initiatives
- Investment requirements
- Implementation roadmap""",
        "tags": ["growth", "strategy", "market analysis", "expansion"],
    },
    {
        "title": "Pricing Excellence Framework",
        "category": "framework",
        "industry": None,
        "content": """End-to-end pricing optimization methodology:

**Pricing Strategy:**
- Value-based pricing principles
- Competitive positioning
- Price architecture design
- Discount governance

**Analytics & Insights:**
- Price elasticity analysis
- Customer willingness-to-pay research
- Competitive intelligence
- Margin analytics

**Execution Capabilities:**
- Pricing tools and CPQ
- Sales enablement
- Performance management
- Deal desk processes

**Governance:**
- Pricing committee structure
- Approval workflows
- Exception management
- Continuous monitoring

**Typical Impact:**
- 2-5% margin improvement
- Reduced discounting
- Improved win rates""",
        "tags": ["pricing", "revenue", "margin", "commercial excellence"],
    },
    {
        "title": "Cloud Migration Playbook",
        "category": "framework",
        "industry": "Technology",
        "content": """Enterprise cloud migration methodology:

**Migration Strategies (6 Rs):**
1. Rehost (lift and shift)
2. Replatform (lift and reshape)
3. Repurchase (move to SaaS)
4. Refactor (re-architect)
5. Retain (keep on-premises)
6. Retire (decommission)

**Migration Phases:**
1. Assess: Application portfolio analysis, cloud readiness
2. Plan: Migration waves, dependency mapping, risk assessment
3. Migrate: Execute migration, testing, validation
4. Optimize: Cost optimization, performance tuning
5. Operate: Cloud operations, FinOps, continuous improvement

**Key Success Factors:**
- Executive sponsorship
- Cloud Center of Excellence
- Security and compliance integration
- Skills development
- Vendor management""",
        "tags": ["cloud", "migration", "technology", "modernization"],
    },
    {
        "title": "AI/ML Implementation Framework",
        "category": "framework",
        "industry": None,
        "content": """Framework for successful AI/ML deployment in enterprise:

**Use Case Identification:**
- Business value assessment
- Data availability check
- Technical feasibility
- Implementation complexity

**Development Lifecycle:**
1. Problem framing and data exploration
2. Feature engineering and model development
3. Model validation and testing
4. Deployment and integration
5. Monitoring and maintenance

**MLOps Capabilities:**
- Model versioning and registry
- Automated training pipelines
- Model monitoring and drift detection
- A/B testing framework

**Governance:**
- AI ethics and responsible AI
- Model explainability
- Bias detection and mitigation
- Regulatory compliance

**Success Metrics:**
- Model performance (accuracy, precision, recall)
- Business impact (revenue, cost savings)
- Adoption rates""",
        "tags": ["ai", "ml", "analytics", "data science", "automation"],
    },
]


# ============ Sample Expertise Areas ============

SAMPLE_EXPERTISE = [
    {
        "title": "Digital Transformation Leadership",
        "category": "expertise",
        "industry": None,
        "content": """Deep expertise in leading large-scale digital transformation programs across industries. Key capabilities include digital strategy development, technology architecture, change management, and agile delivery. Track record of 50+ successful transformations with average ROI of 300%.""",
        "tags": ["digital", "leadership", "transformation"],
    },
    {
        "title": "Healthcare Industry Expertise",
        "category": "expertise",
        "industry": "Healthcare",
        "content": """Specialized knowledge of healthcare industry including provider operations, payer dynamics, life sciences R&D, regulatory environment (HIPAA, FDA), and emerging trends in digital health, telehealth, and value-based care. 15+ years of healthcare consulting experience.""",
        "tags": ["healthcare", "provider", "payer", "life sciences"],
    },
    {
        "title": "Financial Services Expertise",
        "category": "expertise",
        "industry": "Financial Services",
        "content": """Deep expertise in banking, insurance, and capital markets including retail/commercial banking operations, risk management, regulatory compliance (Basel, Dodd-Frank), and fintech disruption. Experience with 20+ Tier 1 financial institutions.""",
        "tags": ["banking", "insurance", "fintech", "risk", "compliance"],
    },
    {
        "title": "Supply Chain & Operations",
        "category": "expertise",
        "industry": "Manufacturing",
        "content": """End-to-end supply chain expertise including procurement, manufacturing operations, logistics, and inventory management. Deep knowledge of Industry 4.0 technologies, lean principles, and supply chain planning systems (SAP, Oracle, Kinaxis).""",
        "tags": ["supply chain", "operations", "manufacturing", "logistics"],
    },
    {
        "title": "M&A and Post-Merger Integration",
        "category": "expertise",
        "industry": None,
        "content": """Extensive experience in M&A strategy, due diligence, and post-merger integration. Track record of 100+ deals across industries with expertise in synergy identification, Day 1 readiness, and integration program management. Average synergy capture rate of 110% of target.""",
        "tags": ["m&a", "integration", "due diligence", "synergies"],
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


async def seed_database():
    """Seed the database with sample data and embeddings."""
    print("🌱 Starting database seeding...")
    
    # Initialize database
    await init_db()
    print("✓ Database initialized")
    
    # Get LLM service for embeddings
    llm_service = get_llm_service()
    
    async with AsyncSessionLocal() as db:
        # Seed engagements
        print("\n📁 Seeding engagements...")
        for eng_data in SAMPLE_ENGAGEMENTS:
            # Generate embedding from description
            embed_text = f"{eng_data['client_name']} {eng_data['engagement_type']} {eng_data['description']}"
            embedding = await generate_embedding(llm_service, embed_text)
            
            days = eng_data.pop("days_ago")
            
            engagement = Engagement(
                id=str(uuid.uuid4()),
                client_name=eng_data["client_name"],
                client_industry=eng_data["client_industry"],
                engagement_type=eng_data["engagement_type"],
                description=eng_data["description"],
                outcomes=eng_data["outcomes"],
                team_members=eng_data["team_members"],
                frameworks_used=eng_data["frameworks_used"],
                status=eng_data["status"],
                start_date=datetime.utcnow() - timedelta(days=days + 90),
                end_date=datetime.utcnow() - timedelta(days=days),
                embedding=embedding,
            )
            db.add(engagement)
            print(f"  ✓ {eng_data['client_name']} - {eng_data['engagement_type']}")
        
        # Seed frameworks
        print("\n📚 Seeding frameworks...")
        for fw_data in SAMPLE_FRAMEWORKS:
            embed_text = f"{fw_data['title']} {fw_data['content']}"
            embedding = await generate_embedding(llm_service, embed_text)
            
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=fw_data["title"],
                content=fw_data["content"],
                category=fw_data["category"],
                industry=fw_data["industry"],
                tags=fw_data["tags"],
                embedding=embedding,
            )
            db.add(item)
            print(f"  ✓ {fw_data['title']}")
        
        # Seed expertise
        print("\n🎓 Seeding expertise areas...")
        for exp_data in SAMPLE_EXPERTISE:
            embed_text = f"{exp_data['title']} {exp_data['content']}"
            embedding = await generate_embedding(llm_service, embed_text)
            
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=exp_data["title"],
                content=exp_data["content"],
                category=exp_data["category"],
                industry=exp_data["industry"],
                tags=exp_data["tags"],
                embedding=embedding,
            )
            db.add(item)
            print(f"  ✓ {exp_data['title']}")
        
        await db.commit()
        print("\n✅ Database seeding complete!")
        print(f"   - {len(SAMPLE_ENGAGEMENTS)} engagements")
        print(f"   - {len(SAMPLE_FRAMEWORKS)} frameworks")
        print(f"   - {len(SAMPLE_EXPERTISE)} expertise areas")


if __name__ == "__main__":
    asyncio.run(seed_database())
