# AI Foundry Infrastructure

This folder hosts the Azure Verified Module (AVM) based deployment that provisions:

- An Azure AI Foundry account and default project aligned to Track 2 requirements
- Optional companion resources (Storage, Key Vault, Cosmos DB, AI Search)
- Dedicated blob containers and file shares for brand guidelines and MCP draft artifacts
- Azure Container Registry + Azure Container Apps hosting resources for frontend and backend containers
- Azure SQL logical server + single database for backend persistence
- Key Vault-backed secret flow for backend `DATABASE_URL` (Container App reads secret reference via managed identity)

## Recent Deployment Updates

The infrastructure template now includes several reliability fixes for Azure Container Apps deployments:

- Frontend runtime endpoint wiring now uses the **actual backend Container App FQDN output** from the deployment, not a deterministic hostname guess.
- Frontend endpoint vars are injected as runtime server vars (`RUNTIME_API_URL`, `RUNTIME_WS_URL`) so Next.js can resolve backend URLs at runtime.
- Backend CORS is configured for strict Azure Container Apps frontend origins using `ALLOWED_ORIGIN_REGEX`.
- `ALLOWED_ORIGINS` is set to `[]` in Azure deployments (valid list payload for settings parsing).
- Backend and frontend Container Apps are tagged with `azd-service-name` in IaC so `azd deploy --service <name>` can reliably discover targets.
- `azure.yaml` services now set Docker `registry` explicitly from `AZURE_CONTAINER_REGISTRY_ENDPOINT` to avoid publish-time registry resolution failures.

## Layout

| File | Purpose |
| --- | --- |
| `main.bicep` | Entry point that instantiates `br/public:avm/ptn/ai-ml/ai-foundry:0.6.0`, configures storage containers for knowledge assets, provisions container hosting resources, and deploys Azure SQL via `br/public:avm/res/sql/server:0.21.1` |
| `params/main.bicepparam` | Default parameter set with shared environment tags and dual model deployments |
| `params/dev.bicepparam` | Lightweight dev environment sample |
| `params/prod.bicepparam` | Production-leaning configuration with higher SKU and throughput |

## Deploying with Bicep

```bash
# subscription scope deployment
az deployment sub create \
  --name smc-shared \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters @infra/params/main.bicepparam

# or target a specific resource group
az deployment group create \
  --resource-group <rg-name> \
  --template-file infra/main.bicep \
  --parameters @infra/params/dev.bicepparam
```

## Key Parameters

- `baseName`: Friendly slug applied to AI Foundry account, project, and associated resources
- `aiModelDeployments`: List of Azure OpenAI deployments to create alongside the project
- `includeAssociatedResources`: Leave enabled to let the AVM module create Storage, Key Vault, Cosmos DB, and AI Search instances
- `createKnowledgeContainers`: Toggles the extra blob containers and file share for brand guidelines / MCP drafts
- `cognitiveServicesRoleAssignments`: Optional list of principals granted access to the Cognitive Services account during deployment
- `sqlAdministratorLoginPassword`: SQL admin secret. Set `AZURE_SQL_ADMIN_PASSWORD` in your azd environment before provisioning.
- Backend container app secrets are provisioned into Key Vault and bound with Key Vault reference (`secretRef`) instead of inline values.

## Runtime App Settings Provisioned

Backend container app:

- `ALLOWED_ORIGINS=[]`
- `ALLOWED_ORIGIN_REGEX=^https://<frontend-app>(--revision)?\..*\.azurecontainerapps\.io$`

Frontend container app:

- `RUNTIME_API_URL=https://<backend-fqdn>`
- `RUNTIME_WS_URL=wss://<backend-fqdn>`

These runtime vars are consumed by the frontend layout/runtime config injection path.

## Outputs

The template surfaces AI Foundry account/project identifiers, storage IDs, container hosting metadata (Container Apps Environment ID, Container App names, and ACR login server), and Azure SQL details (server name/FQDN and database name). When used via `azd`, these are exported to environment variables and consumed by service deployment.

## Next Steps

1. Create or select an Azure resource group and run the deployment commands above (or `azd provision` from the repo root).
2. Deploy containerized applications with `azd deploy` (or `azd up`).
3. If needed, run data/bootstrap scripts separately; they are intentionally not part of the current azd deployment flow.

## Troubleshooting

- `ERR_NAME_NOT_RESOLVED` to backend host
  - Re-run `azd provision` so frontend runtime vars are refreshed from backend FQDN output.
- `could not determine container registry endpoint`
  - Ensure `AZURE_CONTAINER_REGISTRY_ENDPOINT` is set in azd env and `azure.yaml` includes docker registry mapping.
- `unable to find a resource tagged with 'azd-service-name: ...'`
  - Re-run `azd provision` after pulling latest IaC so service tags are applied by template.
