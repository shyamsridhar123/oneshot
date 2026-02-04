---
name: migration-guide
description: Migrate to Microsoft Agent Framework from Semantic Kernel, AutoGen, or LangChain. Use this skill when converting existing AI agent code to Microsoft Agent Framework, understanding equivalent concepts, or porting multi-agent systems.
---

# Migration Guide to Microsoft Agent Framework

This skill helps you migrate existing AI agent applications to Microsoft Agent Framework from other frameworks.

## When to Use This Skill

- Migrating from Semantic Kernel to Agent Framework
- Migrating from AutoGen to Agent Framework
- Migrating from LangChain to Agent Framework
- Understanding concept mappings between frameworks
- Converting existing agent code

## Migration from Semantic Kernel

### Concept Mapping

| Semantic Kernel | Agent Framework | Notes |
|-----------------|-----------------|-------|
| `Kernel` | `Client` | Core orchestration object |
| `Plugin` | `Tool` | Functions agents can call |
| `KernelFunction` | `@tool` decorator | Individual callable functions |
| `ChatCompletionService` | `Agent` | Chat handling |
| `Planner` | `Workflow` | Multi-step orchestration |
| `Memory` | Built-in context | Conversation history |

### Python: Semantic Kernel → Agent Framework

#### Before (Semantic Kernel)

```python
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function

kernel = Kernel()

# Add Azure OpenAI service
kernel.add_service(AzureChatCompletion(
    deployment_name="gpt-4o-mini",
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key"
))

# Define a plugin
class MyPlugin:
    @kernel_function(description="Get the weather for a location")
    def get_weather(self, location: str) -> str:
        return f"Weather in {location}: Sunny, 72°F"

kernel.add_plugin(MyPlugin(), "weather")

# Invoke
async def main():
    result = await kernel.invoke_prompt(
        "What's the weather in Seattle? {{weather.get_weather 'Seattle'}}"
    )
    print(result)

asyncio.run(main())
```

#### After (Agent Framework)

```python
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.tools import tool
from azure.identity import AzureCliCredential

# Define tools
@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

async def main():
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="WeatherAgent",
        instructions="You are a helpful assistant with weather capabilities.",
        tools=[get_weather]
    )
    
    result = await agent.run("What's the weather in Seattle?")
    print(result)

asyncio.run(main())
```

### .NET: Semantic Kernel → Agent Framework

#### Before (Semantic Kernel)

```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.OpenAI;

var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(
        deploymentName: "gpt-4o-mini",
        endpoint: "https://your-resource.openai.azure.com/",
        apiKey: "your-key")
    .Build();

// Add plugin
kernel.ImportPluginFromType<WeatherPlugin>();

class WeatherPlugin
{
    [KernelFunction("get_weather")]
    [Description("Get the weather for a location")]
    public string GetWeather(string location) => $"Weather in {location}: Sunny";
}

// Invoke
var result = await kernel.InvokePromptAsync("What's the weather in Seattle?");
```

#### After (Agent Framework)

```csharp
using OpenAI;
using Microsoft.Agents.AI;
using Azure.Identity;

// Define tools
[AIFunction("Get the weather for a location")]
string GetWeather(string location) => $"Weather in {location}: Sunny";

var client = new OpenAIClient(
    new BearerTokenPolicy(new AzureCliCredential(), "https://ai.azure.com/.default"),
    new OpenAIClientOptions { Endpoint = new Uri("https://your-resource.openai.azure.com/openai/v1") });

var agent = client.GetOpenAIResponseClient("gpt-4o-mini")
    .AsAIAgent(
        name: "WeatherAgent",
        instructions: "You are a helpful assistant.",
        tools: [GetWeather]);

var result = await agent.RunAsync("What's the weather in Seattle?");
Console.WriteLine(result);
```

## Migration from AutoGen

### Concept Mapping

| AutoGen | Agent Framework | Notes |
|---------|-----------------|-------|
| `AssistantAgent` | `Agent` | AI-powered agent |
| `UserProxyAgent` | Human-in-the-loop | User interaction handling |
| `GroupChat` | `Workflow` | Multi-agent orchestration |
| `GroupChatManager` | Workflow orchestrator | Manages agent interactions |
| `function_map` | `tools` | Callable functions |
| `ConversableAgent` | `Agent` with context | Maintains conversation |

### Python: AutoGen → Agent Framework

#### Before (AutoGen)

```python
import autogen

config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": "your-key",
    }
]

# Create assistant
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list},
    system_message="You are a helpful assistant."
)

# Create user proxy
user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config=False
)

# Chat
user_proxy.initiate_chat(assistant, message="Hello!")
```

#### After (Agent Framework)

```python
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

async def main():
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="assistant",
        instructions="You are a helpful assistant."
    )
    
    response = await agent.run("Hello!")
    print(response)

asyncio.run(main())
```

### AutoGen GroupChat → Agent Framework Workflow

#### Before (AutoGen GroupChat)

```python
import autogen

# Create multiple agents
researcher = autogen.AssistantAgent(
    name="researcher",
    system_message="You research topics thoroughly."
)

critic = autogen.AssistantAgent(
    name="critic",
    system_message="You critically review information."
)

writer = autogen.AssistantAgent(
    name="writer",
    system_message="You write clear summaries."
)

# Group chat
groupchat = autogen.GroupChat(
    agents=[researcher, critic, writer],
    messages=[],
    max_round=3
)

manager = autogen.GroupChatManager(groupchat=groupchat)
user_proxy.initiate_chat(manager, message="Research AI trends")
```

#### After (Agent Framework Workflow)

```python
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.workflows import Workflow, step
from azure.identity import AzureCliCredential

@step
async def research(topic: str) -> str:
    """Researcher agent."""
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="researcher",
        instructions="You research topics thoroughly."
    )
    return await agent.run(f"Research: {topic}")

@step
async def critique(research: str) -> str:
    """Critic agent."""
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="critic",
        instructions="You critically review information."
    )
    return await agent.run(f"Critique this research:\n{research}")

@step
async def write_summary(critique: str) -> str:
    """Writer agent."""
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="writer",
        instructions="You write clear summaries."
    )
    return await agent.run(f"Write a summary based on:\n{critique}")

async def main():
    workflow = Workflow("research-workflow")
    workflow.add_edge(research, critique)
    workflow.add_edge(critique, write_summary)
    
    result = await workflow.run(topic="AI trends in 2026")
    print(result)

asyncio.run(main())
```

## Migration from LangChain

### Concept Mapping

| LangChain | Agent Framework | Notes |
|-----------|-----------------|-------|
| `ChatOpenAI` | `OpenAIResponsesClient` | LLM client |
| `Tool` | `@tool` | Callable functions |
| `Agent` | `Agent` | AI agent |
| `AgentExecutor` | `Agent.run()` | Execution handler |
| `Chain` | `Workflow` | Multi-step processing |
| `Memory` | Built-in context | Conversation memory |

### Python: LangChain → Agent Framework

#### Before (LangChain)

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain import hub

llm = ChatOpenAI(model="gpt-4o-mini", api_key="your-key")

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Sunny in {location}"

prompt = hub.pull("hwchase17/openai-functions-agent")
agent = create_openai_functions_agent(llm, [get_weather], prompt)
executor = AgentExecutor(agent=agent, tools=[get_weather])

result = executor.invoke({"input": "What's the weather in NYC?"})
print(result["output"])
```

#### After (Agent Framework)

```python
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.tools import tool
from azure.identity import AzureCliCredential

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Sunny in {location}"

async def main():
    agent = AzureOpenAIResponsesClient(
        credential=AzureCliCredential()
    ).as_agent(
        name="WeatherAgent",
        instructions="You are a helpful assistant.",
        tools=[get_weather]
    )
    
    result = await agent.run("What's the weather in NYC?")
    print(result)

asyncio.run(main())
```

## Key Differences to Note

### 1. Async-First Design

Agent Framework is async by default:

```python
# Agent Framework - always async
response = await agent.run("Hello")

# For sync contexts, use asyncio.run()
import asyncio
response = asyncio.run(agent.run("Hello"))
```

### 2. Authentication

Agent Framework prefers Azure Identity:

```python
# Recommended: Managed Identity / Azure CLI
from azure.identity import DefaultAzureCredential, AzureCliCredential

credential = AzureCliCredential()  # Local dev
credential = DefaultAzureCredential()  # Production
```

### 3. Simplified Tool Definition

```python
from agent_framework.tools import tool

@tool
def my_function(param: str) -> str:
    """Description becomes the tool description."""
    return result
```

### 4. Unified Workflow API

```python
from agent_framework.workflows import Workflow, step

@step
async def my_step(input: str) -> str:
    # Step logic
    return output

workflow = Workflow("my-workflow")
workflow.add_edge(step1, step2)
result = await workflow.run(input_data)
```

## Migration Checklist

- [ ] Install agent-framework package
- [ ] Update imports to agent_framework
- [ ] Convert plugins/tools to `@tool` decorator
- [ ] Replace kernel/chain with Agent
- [ ] Update to async/await pattern
- [ ] Replace group chat with Workflow
- [ ] Update authentication to Azure Identity
- [ ] Convert memory handling to built-in context
- [ ] Update configuration to environment variables
- [ ] Test all agent interactions
- [ ] Update deployment scripts

## Common Migration Issues

### Issue: Synchronous code won't work

**Solution**: Wrap in asyncio.run():

```python
import asyncio
result = asyncio.run(agent.run("prompt"))
```

### Issue: Custom prompts not applying

**Solution**: Use the `instructions` parameter:

```python
agent = client.as_agent(
    name="MyAgent",
    instructions="Your detailed system prompt here..."
)
```

### Issue: Tools not being called

**Solution**: Ensure docstrings are descriptive:

```python
@tool
def my_tool(param: str) -> str:
    """Clear description of what this tool does and when to use it."""
    return result
```

## References

- [Migration from Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel)
- [Migration from AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen)
- [Agent Framework Quick Start](https://learn.microsoft.com/agent-framework/tutorials/quick-start)
