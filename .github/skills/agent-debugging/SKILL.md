---
name: agent-debugging
description: Debug and observe AI agents using Microsoft Agent Framework DevUI and OpenTelemetry. Use this skill when troubleshooting agents, setting up distributed tracing, monitoring agent performance, analyzing agent conversations, or using the interactive DevUI.
---

# Debugging and Observability with Microsoft Agent Framework

This skill helps you debug AI agents and set up observability using DevUI and OpenTelemetry integration.

## When to Use This Skill

- Debugging agent behavior issues
- Setting up distributed tracing with OpenTelemetry
- Monitoring agent performance and latency
- Analyzing agent conversation flows
- Using DevUI for interactive testing

## DevUI - Interactive Developer Interface

DevUI is an interactive web-based interface for agent development, testing, and debugging.

### Installation

```bash
pip install agent-framework[devui] --pre
```

### Starting DevUI

```python
from agent_framework.devui import DevUI
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

# Create your agent
agent = AzureOpenAIResponsesClient(
    credential=AzureCliCredential()
).as_agent(
    name="DebugAgent",
    instructions="You are a helpful assistant."
)

# Launch DevUI
devui = DevUI()
devui.register_agent(agent)
devui.start(port=8080)
# Open http://localhost:8080 in your browser
```

### DevUI Features

- **Interactive chat**: Test agents in real-time
- **Conversation history**: View and replay past conversations
- **Tool execution viewer**: See tool calls and responses
- **Token usage tracking**: Monitor API consumption
- **Workflow visualization**: Visualize multi-agent workflows
- **Time-travel debugging**: Step through workflow execution

## OpenTelemetry Integration

Microsoft Agent Framework has built-in OpenTelemetry support for distributed tracing and monitoring.

### Python - Basic Setup

```python
import asyncio
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.observability import configure_telemetry
from azure.identity import AzureCliCredential

# Configure OpenTelemetry
provider = TracerProvider()
processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Instrument HTTP client
HTTPXClientInstrumentor().instrument()

# Enable Agent Framework telemetry
configure_telemetry(enable_tracing=True)

async def main():
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="TracedAgent",
        instructions="You are a helpful assistant."
    )
    
    # All agent calls will now be traced
    response = await agent.run("Hello!")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Python - Export to Azure Monitor

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure Azure Monitor exporter
exporter = AzureMonitorTraceExporter(
    connection_string="InstrumentationKey=your-key;..."
)

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# Continue with agent setup...
```

### Python - Export to Jaeger

```python
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# Continue with agent setup...
```

### .NET - Basic Setup

```csharp
using OpenTelemetry;
using OpenTelemetry.Trace;
using Microsoft.Agents.AI.Telemetry;

// Configure OpenTelemetry
using var tracerProvider = Sdk.CreateTracerProviderBuilder()
    .AddAgentFrameworkInstrumentation()
    .AddConsoleExporter()
    .Build();

// All agent calls will be traced
var agent = client.GetOpenAIResponseClient("gpt-4o-mini")
    .AsAIAgent(name: "TracedAgent", instructions: "You are helpful.");

var response = await agent.RunAsync("Hello!");
Console.WriteLine(response);
```

### .NET - Export to Azure Monitor

```csharp
using Azure.Monitor.OpenTelemetry.Exporter;

using var tracerProvider = Sdk.CreateTracerProviderBuilder()
    .AddAgentFrameworkInstrumentation()
    .AddAzureMonitorTraceExporter(options =>
    {
        options.ConnectionString = "InstrumentationKey=...";
    })
    .Build();
```

## Debugging Techniques

### 1. Enable Verbose Logging

```python
import logging

# Set logging level for agent framework
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("agent_framework").setLevel(logging.DEBUG)
```

### 2. Capture Diagnostic Information

```python
async def debug_agent_call(agent, prompt):
    try:
        response = await agent.run(prompt)
        return response
    except Exception as e:
        # Log diagnostic information
        print(f"Error: {e}")
        print(f"Diagnostics: {agent.get_diagnostics()}")
        raise
```

### 3. Inspect Tool Calls

```python
from agent_framework.middleware import LoggingMiddleware

# Add middleware to log all tool calls
agent = client.as_agent(
    name="DebugAgent",
    instructions="...",
    middleware=[LoggingMiddleware(log_tool_calls=True)]
)
```

### 4. Track Token Usage

```python
async def main():
    agent = client.as_agent(name="Agent", instructions="...")
    
    response = await agent.run("Complex prompt...")
    
    # Access usage statistics
    usage = agent.last_usage
    print(f"Prompt tokens: {usage.prompt_tokens}")
    print(f"Completion tokens: {usage.completion_tokens}")
    print(f"Total tokens: {usage.total_tokens}")
```

### 5. Time-Travel Debugging for Workflows

```python
from agent_framework.workflows import Workflow
from agent_framework.devui import DevUI

workflow = Workflow("my-workflow")
# ... configure workflow ...

# Enable time-travel debugging
devui = DevUI()
devui.register_workflow(workflow)
devui.enable_time_travel()
devui.start()

# Run workflow - you can step through execution in DevUI
await workflow.run(input_data)
```

## Common Issues and Solutions

### Issue: Agent produces inconsistent results

**Solution**: Add temperature control and seed for reproducibility:

```python
agent = client.as_agent(
    name="ConsistentAgent",
    instructions="...",
    temperature=0.0,  # Deterministic
    seed=42           # Reproducible
)
```

### Issue: Tool calls failing silently

**Solution**: Add error handling middleware:

```python
from agent_framework.middleware import ErrorHandlingMiddleware

agent = client.as_agent(
    name="RobustAgent",
    middleware=[ErrorHandlingMiddleware(
        on_error="retry",
        max_retries=3,
        log_errors=True
    )]
)
```

### Issue: High latency

**Solution**: Use streaming and check trace spans:

```python
# Enable streaming for faster first-token response
async for chunk in agent.stream("Long prompt..."):
    print(chunk, end="", flush=True)

# Check OpenTelemetry spans for latency breakdown
```

### Issue: Rate limiting (429 errors)

**Solution**: Implement retry with exponential backoff:

```python
from agent_framework.middleware import RetryMiddleware

agent = client.as_agent(
    name="RetryAgent",
    middleware=[RetryMiddleware(
        max_retries=5,
        initial_delay=1.0,
        exponential_backoff=True
    )]
)
```

## Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `agent.request.duration` | Time per request | > 10s |
| `agent.token.usage` | Tokens per request | > 4000 |
| `agent.tool.calls` | Tool invocations | > 10 per request |
| `agent.error.rate` | Percentage of failures | > 5% |
| `workflow.step.duration` | Time per workflow step | > 30s |

## Best Practices

1. **Always enable tracing in production** - Essential for debugging
2. **Use structured logging** - Include correlation IDs
3. **Set up alerts** - Monitor error rates and latency
4. **Use DevUI in development** - Faster iteration
5. **Export traces to centralized system** - Azure Monitor, Jaeger, etc.
6. **Add custom spans** - For business-specific metrics

## References

- [Python Observability Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/observability)
- [.NET Telemetry Samples](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/GettingStarted/AgentOpenTelemetry)
- [DevUI Package](https://github.com/microsoft/agent-framework/tree/main/python/packages/devui)
