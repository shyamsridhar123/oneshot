---
name: agent-creation
description: Create AI agents using Microsoft Agent Framework (MAF) in Python or .NET. Use this skill when building new agents, configuring agent providers (Azure OpenAI, OpenAI, etc.), setting up chat agents, or implementing tool-calling agents.
---

# Agent Creation with Microsoft Agent Framework

This skill helps you create AI agents using Microsoft Agent Framework, supporting both Python and .NET implementations.

## When to Use This Skill

- Creating a new AI agent or chatbot
- Setting up agent providers (Azure OpenAI, OpenAI, etc.)
- Implementing agents with custom tools/functions
- Building agents with specific instructions or personas

## Installation

### Python

```bash
pip install agent-framework --pre
```

### .NET

```bash
dotnet add package Microsoft.Agents.AI --prerelease
```

## Quick Start Examples

### Python - Azure OpenAI Agent

```python
import os
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

async def main():
    agent = AzureOpenAIResponsesClient(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        credential=AzureCliCredential(),
    ).as_agent(
        name="MyAgent",
        instructions="You are a helpful assistant.",
    )
    
    response = await agent.run("Hello, how can you help me?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Python - OpenAI Agent

```python
import asyncio
from agent_framework.openai import OpenAIResponsesClient

async def main():
    agent = OpenAIResponsesClient(
        api_key="your-api-key",  # Or use OPENAI_API_KEY env var
    ).as_agent(
        name="MyAgent",
        instructions="You are a helpful coding assistant.",
    )
    
    response = await agent.run("Explain async/await in Python")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### .NET - Azure OpenAI Agent

```csharp
// dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
// dotnet add package Azure.Identity
using System;
using OpenAI;

var agent = new OpenAIClient(
    new BearerTokenPolicy(new AzureCliCredential(), "https://ai.azure.com/.default"),
    new OpenAIClientOptions() { Endpoint = new Uri("https://<resource>.openai.azure.com/openai/v1") })
    .GetOpenAIResponseClient("gpt-4o-mini")
    .AsAIAgent(name: "MyAgent", instructions: "You are a helpful assistant.");

Console.WriteLine(await agent.RunAsync("Hello, how can you help me?"));
```

### .NET - OpenAI Agent

```csharp
// dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
using System;
using OpenAI;

var agent = new OpenAIClient("<your-api-key>")
    .GetOpenAIResponseClient("gpt-4o-mini")
    .AsAIAgent(name: "MyAgent", instructions: "You are a helpful assistant.");

Console.WriteLine(await agent.RunAsync("Write a haiku about coding."));
```

## Adding Tools to Agents

### Python - Agent with Tools

```python
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.tools import tool
from azure.identity import AzureCliCredential

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny and 72°F"

@tool
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression."""
    return eval(expression)

async def main():
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential(),
    ).as_agent(
        name="ToolAgent",
        instructions="You are a helpful assistant with access to weather and calculation tools.",
        tools=[get_weather, calculate],
    )
    
    response = await agent.run("What's the weather in Seattle and what is 15 * 7?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### .NET - Agent with Tools

```csharp
using Microsoft.Agents.AI;

public class WeatherTools
{
    [AIFunction("Get the current weather for a location")]
    public string GetWeather(string location)
    {
        return $"The weather in {location} is sunny and 72°F";
    }
    
    [AIFunction("Evaluate a mathematical expression")]
    public double Calculate(string expression)
    {
        // Use a proper expression evaluator in production
        return 0.0;
    }
}

var tools = new WeatherTools();
var agent = client.GetOpenAIResponseClient("gpt-4o-mini")
    .AsAIAgent(
        name: "ToolAgent", 
        instructions: "You are a helpful assistant.",
        tools: [tools.GetWeather, tools.Calculate]);
```

## Best Practices

1. **Use environment variables** for API keys and endpoints
2. **Reuse client instances** - Don't create new clients for each request
3. **Use async APIs** for better throughput
4. **Handle rate limiting** - Implement retry logic for 429 errors
5. **Set clear instructions** - Be specific about agent behavior and constraints
6. **Use Azure CLI authentication** (`AzureCliCredential`) for local development

## Environment Variables

### Python/Azure OpenAI
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME` - Deployment name
- `AZURE_OPENAI_API_VERSION` - API version (e.g., "2024-02-15-preview")
- `AZURE_OPENAI_API_KEY` - API key (optional if using credential)

### Python/OpenAI
- `OPENAI_API_KEY` - Your OpenAI API key

## References

- [Getting Started with Agents (Python)](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/agents)
- [Getting Started with Agents (.NET)](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/GettingStarted/Agents)
- [MS Learn Documentation](https://learn.microsoft.com/en-us/agent-framework/)
