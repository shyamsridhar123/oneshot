"""MAF Agent Factory - Creates agents using Microsoft Agent Framework patterns."""

from typing import Callable, Any
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework import ai_function as tool  # tool decorator renamed to ai_function

from app.config import settings


def get_azure_client() -> AzureOpenAIResponsesClient:
    """Get configured Azure OpenAI client for MAF."""
    return AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
        api_key=settings.azure_openai_api_key,
    )


def create_agent(
    name: str,
    instructions: str,
    tools: list[Callable] = None,
    deployment: str = None,
):
    """
    Create an agent using MAF pattern.
    
    Args:
        name: Agent name
        instructions: System prompt for the agent
        tools: Optional list of tool functions decorated with @tool
        deployment: Optional specific deployment to use
    
    Returns:
        MAF agent instance
    """
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        deployment_name=deployment or settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
        api_key=settings.azure_openai_api_key,
    )
    
    return client.as_agent(
        name=name,
        instructions=instructions,
        tools=tools or [],
    )


# Pre-defined tools for agents

@tool
def search_web(query: str) -> str:
    """Search the web for information on a topic."""
    # Mock implementation for demo
    return f"""Web search results for: "{query}"

1. **Industry Report 2026** - Comprehensive analysis of market trends and forecasts.
   Source: IndustryAnalytics.com
   
2. **Company Overview** - Recent developments and strategic initiatives.
   Source: BusinessWire
   
3. **Market Analysis** - Competitive landscape and growth opportunities.
   Source: MarketWatch

Note: These are simulated results for demonstration purposes."""


@tool
def search_news(query: str, days: int = 7) -> str:
    """Search recent news articles on a topic."""
    # Mock implementation for demo
    return f"""Recent news for: "{query}" (last {days} days)

📰 **Strategic Partnership Announced** (2 days ago)
   Major collaboration to expand market reach.
   
📰 **Q4 Earnings Report** (5 days ago)
   Company exceeds analyst expectations with strong growth.
   
📰 **New Product Launch** (6 days ago)
   Innovative solution targeting enterprise customers.

Note: These are simulated results for demonstration purposes."""


@tool
def get_company_info(company_name: str) -> str:
    """Get detailed information about a company."""
    # Mock implementation for demo
    return f"""Company Profile: {company_name}

**Overview:**
- Industry: Technology / Professional Services
- Founded: 2010
- Headquarters: San Francisco, CA
- Employees: 5,000+
- Annual Revenue: $2.5B (estimated)

**Recent Highlights:**
- Expanded into 3 new markets this year
- Launched AI-powered product suite
- Strong focus on digital transformation

**Key Challenges:**
- Competitive pressure from new entrants
- Need for operational efficiency
- Talent retention in key areas

Note: This is simulated data for demonstration purposes."""


@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for relevant information."""
    # Mock implementation - would connect to actual knowledge service
    return f"""Knowledge Base Results for: "{query}"

**Relevant Frameworks:**
1. Digital Transformation Playbook
   - 6-phase methodology for enterprise digitization
   - Proven across 50+ engagements
   
2. Change Management Framework
   - Stakeholder engagement model
   - Communication strategy templates

**Similar Past Engagements:**
1. TechCorp Digital Transformation (2024)
   - Scope: End-to-end process digitization
   - Outcome: 40% efficiency improvement
   
2. GlobalRetail Modernization (2025)
   - Scope: Customer experience platform
   - Outcome: 25% increase in customer satisfaction

Note: This is simulated data for demonstration purposes."""


@tool
def calculate_metrics(data: str, metric_type: str) -> str:
    """Calculate business metrics from data."""
    return f"""Metric Calculation: {metric_type}

Based on provided data:
- Baseline: 100 units
- Projected: 135 units
- Improvement: +35%
- Confidence: High (based on historical patterns)

Key Assumptions:
1. Market conditions remain stable
2. Implementation follows best practices
3. Team capacity is maintained

Note: This is a simulated calculation for demonstration."""


# Export all tools
AGENT_TOOLS = {
    "researcher": [search_web, search_news, get_company_info],
    "memory": [search_knowledge_base],
    "analyst": [calculate_metrics],
}
