---
name: workflow-orchestration
description: Build multi-agent workflows and graph-based orchestration using Microsoft Agent Framework. Use this skill when creating agent pipelines, connecting multiple agents, implementing human-in-the-loop patterns, streaming, checkpointing, or time-travel debugging.
---

# Workflow Orchestration with Microsoft Agent Framework

This skill helps you build complex multi-agent workflows using graph-based orchestration in Microsoft Agent Framework.

## When to Use This Skill

- Building multi-agent pipelines
- Creating data flows between agents
- Implementing human-in-the-loop patterns
- Setting up streaming and checkpointing
- Orchestrating deterministic functions with AI agents

## Key Concepts

### Graph-Based Workflows

Microsoft Agent Framework uses a graph-based model where:
- **Nodes** represent agents or deterministic functions
- **Edges** define data flow between nodes
- **Workflows** are compositions of nodes connected by edges

### Features

- **Streaming**: Real-time data flow between agents
- **Checkpointing**: Save and restore workflow state
- **Human-in-the-loop**: Pause execution for human input
- **Time-travel**: Debug by replaying workflow steps

## Python Workflow Examples

### Basic Sequential Workflow

```python
import asyncio
from agent_framework.workflows import Workflow, step
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

# Define workflow steps
@step
async def research_topic(topic: str) -> str:
    """Research agent gathers information on a topic."""
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="Researcher",
        instructions="You are a research assistant. Provide comprehensive information on topics."
    )
    return await agent.run(f"Research the following topic: {topic}")

@step
async def summarize_research(research: str) -> str:
    """Summarizer agent condenses research into key points."""
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="Summarizer",
        instructions="You summarize complex information into clear, concise bullet points."
    )
    return await agent.run(f"Summarize this research:\n{research}")

@step
async def create_report(summary: str) -> str:
    """Writer agent creates a formatted report."""
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="Writer",
        instructions="You are a technical writer. Create well-structured reports."
    )
    return await agent.run(f"Create a report from this summary:\n{summary}")

# Build the workflow
async def main():
    workflow = Workflow("research-report")
    
    # Connect steps in sequence
    workflow.add_edge(research_topic, summarize_research)
    workflow.add_edge(summarize_research, create_report)
    
    # Execute workflow
    result = await workflow.run(topic="Quantum Computing")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Parallel Agent Workflow

```python
import asyncio
from agent_framework.workflows import Workflow, step, parallel

@step
async def analyze_code(code: str) -> dict:
    """Analyze code for issues."""
    # Analysis agent implementation
    return {"issues": [...]}

@step
async def suggest_improvements(code: str) -> dict:
    """Suggest code improvements."""
    # Improvement agent implementation
    return {"suggestions": [...]}

@step
async def check_security(code: str) -> dict:
    """Check code for security vulnerabilities."""
    # Security agent implementation
    return {"vulnerabilities": [...]}

@step
async def generate_report(analysis: dict, improvements: dict, security: dict) -> str:
    """Combine all analysis into a report."""
    # Report generation
    return "Comprehensive code review report..."

async def main():
    workflow = Workflow("code-review")
    
    # Run analysis, improvements, and security checks in parallel
    parallel_results = parallel(analyze_code, suggest_improvements, check_security)
    
    # Feed parallel results to report generator
    workflow.add_edge(parallel_results, generate_report)
    
    result = await workflow.run(code="def example(): pass")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Human-in-the-Loop Workflow

```python
import asyncio
from agent_framework.workflows import Workflow, step, human_input

@step
async def generate_draft(topic: str) -> str:
    """Generate initial draft."""
    # Agent generates draft
    return "Initial draft content..."

@step
@human_input(prompt="Review the draft and provide feedback:")
async def review_draft(draft: str, feedback: str) -> dict:
    """Human reviews and provides feedback."""
    return {"draft": draft, "feedback": feedback}

@step
async def revise_draft(review: dict) -> str:
    """Revise draft based on human feedback."""
    # Agent revises based on feedback
    return "Revised content..."

async def main():
    workflow = Workflow("content-review")
    
    workflow.add_edge(generate_draft, review_draft)
    workflow.add_edge(review_draft, revise_draft)
    
    # Workflow will pause at review_draft for human input
    result = await workflow.run(topic="AI Ethics")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Workflow with Checkpointing

```python
import asyncio
from agent_framework.workflows import Workflow, step, Checkpoint

@step
async def long_running_analysis(data: str) -> dict:
    """Long-running analysis step."""
    # Expensive computation
    return {"analysis": "..."}

async def main():
    workflow = Workflow("checkpointed-workflow")
    
    # Enable checkpointing
    checkpoint = Checkpoint(storage_path="./checkpoints")
    workflow.enable_checkpointing(checkpoint)
    
    # If interrupted, workflow resumes from last checkpoint
    result = await workflow.run(data="Large dataset...")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## .NET Workflow Examples

### Basic Workflow

```csharp
using Microsoft.Agents.AI.Workflows;

// Define workflow steps
async Task<string> ResearchTopic(string topic)
{
    var agent = client.GetOpenAIResponseClient("gpt-4o-mini")
        .AsAIAgent(name: "Researcher", instructions: "Research topics thoroughly.");
    return await agent.RunAsync($"Research: {topic}");
}

async Task<string> SummarizeResearch(string research)
{
    var agent = client.GetOpenAIResponseClient("gpt-4o-mini")
        .AsAIAgent(name: "Summarizer", instructions: "Summarize information concisely.");
    return await agent.RunAsync($"Summarize: {research}");
}

// Build and run workflow
var workflow = new Workflow("research-workflow")
    .AddStep(ResearchTopic)
    .AddStep(SummarizeResearch);

var result = await workflow.RunAsync("Machine Learning");
Console.WriteLine(result);
```

## Workflow Patterns

### Pattern 1: Fan-Out/Fan-In

Multiple agents process data in parallel, then results are aggregated.

```python
@step
async def distribute_work(data: list) -> list:
    """Split work across multiple agents."""
    return [chunk for chunk in split_data(data)]

@step  
async def process_chunk(chunk: any) -> any:
    """Process individual chunk."""
    return await agent.run(str(chunk))

@step
async def aggregate_results(results: list) -> str:
    """Combine all results."""
    return await aggregator_agent.run(str(results))
```

### Pattern 2: Conditional Routing

Route to different agents based on conditions.

```python
@step
async def classify_request(request: str) -> str:
    """Classify the type of request."""
    return await classifier.run(request)

@step
async def route_request(classification: str, request: str) -> str:
    """Route to appropriate agent."""
    if classification == "technical":
        return await tech_agent.run(request)
    elif classification == "billing":
        return await billing_agent.run(request)
    else:
        return await general_agent.run(request)
```

### Pattern 3: Retry with Escalation

```python
@step(retries=3)
async def attempt_resolution(issue: str) -> dict:
    """Try to resolve issue, escalate on failure."""
    result = await first_line_agent.run(issue)
    if not result.resolved:
        result = await senior_agent.run(issue)
    return result
```

## Best Practices

1. **Keep steps focused** - Each step should have a single responsibility
2. **Use parallel execution** - Run independent steps concurrently
3. **Enable checkpointing** - For long-running or critical workflows
4. **Handle failures gracefully** - Implement retry logic and fallbacks
5. **Use streaming** - For real-time user feedback
6. **Log workflow state** - For debugging and monitoring

## References

- [Python Workflow Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/workflows)
- [.NET Workflow Samples](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/GettingStarted/Workflows)
- [MS Learn - User Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)
