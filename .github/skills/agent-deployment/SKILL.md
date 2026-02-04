---
name: agent-deployment
description: Deploy Microsoft Agent Framework agents to production environments including Azure Functions, containers, and Azure AI Foundry. Use this skill when deploying agents to cloud platforms, containerizing agents, or integrating with Azure services.
---

# Deploying Microsoft Agent Framework Agents

This skill helps you deploy AI agents built with Microsoft Agent Framework to production environments.

## When to Use This Skill

- Deploying agents to Azure Functions
- Containerizing agents with Docker
- Deploying to Azure AI Foundry
- Setting up production configurations
- Scaling agent workloads

## Deployment Options

| Platform | Best For | Scaling |
|----------|----------|---------|
| Azure Functions | Event-driven, serverless | Automatic |
| Azure Container Apps | Containerized workloads | Automatic |
| Azure Kubernetes Service | Enterprise, multi-agent | Manual/Auto |
| Azure AI Foundry | Full lifecycle management | Managed |

## Azure Functions Deployment (Python)

### Project Structure

```
my-agent-function/
├── function_app.py
├── requirements.txt
├── host.json
└── local.settings.json
```

### function_app.py

```python
import azure.functions as func
import asyncio
import json
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

# Initialize agent once (reuse across invocations)
def get_agent():
    return AzureOpenAIResponsesClient(
        credential=DefaultAzureCredential()
    ).as_agent(
        name="ProductionAgent",
        instructions="You are a helpful assistant."
    )

agent = get_agent()

@app.route(route="chat", methods=["POST"])
async def chat(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        message = body.get("message", "")
        
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "Message is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        response = await agent.run(message)
        
        return func.HttpResponse(
            json.dumps({"response": response}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
```

### requirements.txt

```
azure-functions
agent-framework
azure-identity
```

### host.json

```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  },
  "logging": {
    "logLevel": {
      "default": "Information"
    }
  }
}
```

### local.settings.json

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
    "AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME": "gpt-4o-mini"
  }
}
```

### Deploy to Azure

```bash
# Create Function App
az functionapp create \
    --resource-group myResourceGroup \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --name my-agent-function \
    --storage-account mystorageaccount

# Enable managed identity
az functionapp identity assign \
    --resource-group myResourceGroup \
    --name my-agent-function

# Grant access to Azure OpenAI
az role assignment create \
    --role "Cognitive Services OpenAI User" \
    --assignee <managed-identity-principal-id> \
    --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<aoai-resource>

# Deploy
func azure functionapp publish my-agent-function
```

## Azure Functions Deployment (.NET)

### Project Structure

```
MyAgentFunction/
├── Program.cs
├── ChatFunction.cs
├── MyAgentFunction.csproj
├── host.json
└── local.settings.json
```

### ChatFunction.cs

```csharp
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Http;
using Microsoft.Extensions.Logging;
using System.Net;
using System.Text.Json;

public class ChatFunction
{
    private readonly ILogger<ChatFunction> _logger;
    private readonly IAIAgent _agent;

    public ChatFunction(ILogger<ChatFunction> logger, IAIAgent agent)
    {
        _logger = logger;
        _agent = agent;
    }

    [Function("chat")]
    public async Task<HttpResponseData> Run(
        [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req)
    {
        var body = await JsonSerializer.DeserializeAsync<ChatRequest>(req.Body);
        
        var response = await _agent.RunAsync(body.Message);
        
        var httpResponse = req.CreateResponse(HttpStatusCode.OK);
        await httpResponse.WriteAsJsonAsync(new { response });
        return httpResponse;
    }
}

public record ChatRequest(string Message);
```

### Program.cs

```csharp
using Azure.Identity;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using OpenAI;

var host = new HostBuilder()
    .ConfigureFunctionsWebApplication()
    .ConfigureServices(services =>
    {
        services.AddApplicationInsightsTelemetryWorkerService();
        services.ConfigureFunctionsApplicationInsights();
        
        // Register agent as singleton
        services.AddSingleton<IAIAgent>(sp =>
        {
            var client = new OpenAIClient(
                new BearerTokenPolicy(new DefaultAzureCredential(), "https://ai.azure.com/.default"),
                new OpenAIClientOptions() 
                { 
                    Endpoint = new Uri(Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!) 
                });
            
            return client.GetOpenAIResponseClient(
                Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT")!)
                .AsAIAgent(name: "ProductionAgent", instructions: "You are helpful.");
        });
    })
    .Build();

host.Run();
```

## Docker Deployment

### Dockerfile (Python)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### main.py (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

app = FastAPI()

agent = AzureOpenAIResponsesClient(
    credential=DefaultAzureCredential()
).as_agent(
    name="ProductionAgent",
    instructions="You are a helpful assistant."
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await agent.run(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Build and Deploy to Azure Container Apps

```bash
# Build image
docker build -t my-agent:latest .

# Push to Azure Container Registry
az acr login --name myregistry
docker tag my-agent:latest myregistry.azurecr.io/my-agent:latest
docker push myregistry.azurecr.io/my-agent:latest

# Deploy to Container Apps
az containerapp create \
    --name my-agent-app \
    --resource-group myResourceGroup \
    --environment myEnvironment \
    --image myregistry.azurecr.io/my-agent:latest \
    --target-port 8000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --user-assigned <managed-identity-id> \
    --env-vars \
        AZURE_OPENAI_ENDPOINT=https://... \
        AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4o-mini
```

## Azure AI Foundry Integration

Microsoft Agent Framework integrates with Azure AI Foundry for full lifecycle management.

```python
from agent_framework.azure import AzureAIFoundryClient

# Connect to Azure AI Foundry project
client = AzureAIFoundryClient(
    project_name="my-ai-project",
    resource_group="myResourceGroup"
)

# Deploy agent to Foundry
deployment = await client.deploy_agent(
    agent=agent,
    deployment_name="production-agent",
    instance_type="Standard_DS3_v2",
    instance_count=2
)

print(f"Deployed to: {deployment.endpoint}")
```

## Production Configuration

### Environment Variables

```bash
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4o-mini

# Optional
AZURE_OPENAI_API_VERSION=2024-02-15-preview
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# For non-managed-identity auth
AZURE_OPENAI_API_KEY=your-key
```

### Health Checks

Always implement health endpoints:

```python
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    # Check agent connectivity
    try:
        await agent.run("health check")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}
```

## Security Best Practices

1. **Use Managed Identity** - Never embed API keys in code
2. **Enable HTTPS only** - No unencrypted traffic
3. **Implement rate limiting** - Prevent abuse
4. **Add authentication** - Use Azure AD or API keys
5. **Log requests** - For audit and debugging
6. **Set timeouts** - Prevent runaway requests

### Example: Rate Limiting Middleware

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if now - t < 60
        ]
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                {"error": "Rate limit exceeded"},
                status_code=429
            )
        
        self.requests[client_ip].append(now)
        return await call_next(request)

app.middleware("http")(RateLimiter(requests_per_minute=60))
```

## Scaling Considerations

| Metric | Recommendation |
|--------|----------------|
| Requests/sec | Start with 2-3 instances, scale based on load |
| Memory | 512MB-1GB per instance minimum |
| Timeout | 30-60 seconds for agent responses |
| Cold start | Use premium/dedicated plans to minimize |
| Concurrency | 10-20 concurrent requests per instance |

## References

- [Azure Functions Python](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-foundry/)
- [Agent Framework Deployment Guide](https://learn.microsoft.com/agent-framework/deployment)
