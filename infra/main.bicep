targetScope = 'resourceGroup'

@description('Friendly base name for the AI Foundry resources. Used by the AVM module when generating resource names.')
@minLength(3)
param baseName string

@description('Azure region for the deployment. Defaults to the current resource group location.')
param location string = resourceGroup().location

@description('Azure region for container hosting resources (ACR + Container Apps).')
param appHostingLocation string = location

@description('Optional override for the auto-generated unique suffix that gets appended to global resources.')
param baseUniqueName string = substring(uniqueString(subscription().id, resourceGroup().name, baseName), 0, 5)

@description('SKU for the AI Foundry (Cognitive Services) account.')
@allowed([
  'C2'
  'C3'
  'C4'
  'DC0'
  'F0'
  'F1'
  'S'
  'S0'
  'S1'
  'S10'
  'S2'
  'S3'
  'S4'
  'S5'
  'S6'
  'S7'
  'S8'
  'S9'
])
param aiFoundrySku string = 'S0'

@description('Model deployments to create inside the AI Foundry account.')
param aiModelDeployments array = [
  {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
    name: 'gpt-4o'
    sku: {
      name: 'Standard'
      capacity: 1
    }
  }
]

@description('Optional custom name for the default AI project. Empty string uses a generated value.')
param projectName string = ''

@description('Optional display name for the default AI project. Empty string uses a generated value.')
param projectDisplayName string = ''

@description('Optional description for the AI project.')
param projectDescription string = 'Multi-agent social media workspace for TechVista'

@description('Set to true to deploy the companion resources (Key Vault, Storage, Cosmos DB, AI Search) that the AVM module can manage.')
param includeAssociatedResources bool = true

@description('Optional tags applied to all resources created by this template.')
param tags object = {}

@description('Opt-in for AVM usage telemetry. See https://aka.ms/avm/telemetry for details.')
param enableTelemetry bool = true

@description('Set to true to create blob containers and file shares that store brand guidelines, historical assets, and MCP drafts.')
param createKnowledgeContainers bool = true

@description('Blob container for curated brand knowledge artifacts.')
param brandDataContainerName string = 'brand-data'

@description('Blob container for generated drafts / MCP outputs.')
param draftsContainerName string = 'mcp-drafts'

@description('Azure Files share that stores downloadable drafts for MCP tooling.')
param draftsShareName string = 'drafts'

@description('Optional array of role assignment objects applied to the AI Foundry account. Each item must include principalId and roleDefinitionIdOrName.')
param cognitiveServicesRoleAssignments array = []

@description('Set to true to provision Azure Container Apps resources for frontend and backend deployment via azd.')
param deployApplicationHosting bool = true

@description('Azure Container Registry SKU used to store frontend/backend container images.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param containerRegistrySku string = 'Basic'

@description('Bootstrap image used during initial backend container app provisioning before azd deploys application images.')
param backendContainerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('Bootstrap image used during initial frontend container app provisioning before azd deploys application images.')
param frontendContainerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('CPU cores allocated to the backend container app revision.')
param backendCpu int = 1

@description('Memory allocated to the backend container app revision.')
param backendMemory string = '2Gi'

@description('CPU cores allocated to the frontend container app revision.')
param frontendCpu int = 1

@description('Memory allocated to the frontend container app revision.')
param frontendMemory string = '2Gi'

@description('Primary chat deployment name used by the backend API in Azure OpenAI.')
param backendChatDeploymentName string = 'gpt-4o'

@description('Secondary deployment name used by the backend API for fallback/specialized tasks.')
param backendSecondaryDeploymentName string = 'gpt-4o-mini'

@description('Code-focused deployment name used by the backend API for coding tasks.')
param backendCodexDeploymentName string = 'gpt-4o-mini'

@description('Embedding deployment name used by the backend API for semantic search/RAG.')
param backendEmbeddingDeploymentName string = 'text-embedding-3-small'

@description('API version used by the backend API for Azure OpenAI.')
param backendOpenAiApiVersion string = '2025-03-01-preview'

@description('Set to true to provision Azure SQL Database resources for the backend data store.')
param deployAzureSql bool = true

@description('SQL logical server administrator login name.')
param sqlAdministratorLogin string = 'oneshotsqladmin'

@description('SQL logical server administrator password.')
@secure()
param sqlAdministratorLoginPassword string = ''

@description('Optional override for the Azure SQL logical server name. Empty string uses a generated name.')
param sqlServerName string = ''

@description('Name of the Azure SQL database used by the backend API.')
param sqlDatabaseName string = 'oneshotdb'

@description('Azure SQL database SKU name.')
@allowed([
  'Basic'
  'S0'
  'S1'
  'S2'
  'S3'
  'P1'
  'P2'
  'P4'
  'GP_S_Gen5_1'
  'GP_S_Gen5_2'
  'GP_Gen5_2'
])
param sqlDatabaseSkuName string = 'S0'

@description('Azure SQL database SKU tier.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
  'GeneralPurpose'
])
param sqlDatabaseSkuTier string = 'Standard'

@description('Set to true to create the Azure SQL firewall rule that allows Azure services access (0.0.0.0).')
param sqlAllowAzureServices bool = true

var resolvedProjectName = projectName == '' ? '${baseName}-project' : projectName
var resolvedProjectDisplayName = projectDisplayName == '' ? '${baseName} Social Media Command Center' : projectDisplayName
var shouldCreateKnowledgeArtifacts = createKnowledgeContainers && includeAssociatedResources
var acrName = toLower('acr${baseUniqueName}${uniqueString(baseName, resourceGroup().id)}')
var containerAppsEnvironmentName = take('${baseName}-cae', 60)
var backendContainerAppName = take('${baseName}-backend', 32)
var frontendContainerAppName = take('${baseName}-frontend', 32)
var backendOpenAiEndpoint = 'https://${aiFoundry.outputs.aiServicesName}.openai.azure.com/'
var backendApiUrl = 'https://${backendContainerAppName}.${containerAppsEnvironmentName}.${appHostingLocation}.azurecontainerapps.io'
var backendWsUrl = 'wss://${backendContainerAppName}.${containerAppsEnvironmentName}.${appHostingLocation}.azurecontainerapps.io'
var frontendApiUrl = 'https://${frontendContainerAppName}.${containerAppsEnvironmentName}.${appHostingLocation}.azurecontainerapps.io'
var shouldDeployAzureSql = deployAzureSql && !empty(sqlAdministratorLoginPassword)
var resolvedSqlServerName = sqlServerName == '' ? toLower(take('${baseName}-sql-${baseUniqueName}', 63)) : sqlServerName
var sqlServerFqdn = '${resolvedSqlServerName}.${environment().suffixes.sqlServerHostname}'
var sqlOdbcConnectionString = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:${sqlServerFqdn},1433;Database=${sqlDatabaseName};Uid=${sqlAdministratorLogin};Pwd=${sqlAdministratorLoginPassword};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
var backendDatabaseUrl = shouldDeployAzureSql ? 'mssql+aioodbc:///?odbc_connect=${uriComponent(sqlOdbcConnectionString)}' : 'sqlite+aiosqlite:///./data/oneshot.db'
var shouldUseKeyVaultBackedSecrets = deployApplicationHosting && includeAssociatedResources && shouldDeployAzureSql
var backendDatabaseUrlSecretName = 'backend-database-url'
var backendDatabaseUrlSecretUri = shouldUseKeyVaultBackedSecrets ? backendDatabaseUrlSecret!.outputs.secretUri : ''
var keyVaultResourceId = includeAssociatedResources ? resourceId('Microsoft.KeyVault/vaults', aiFoundry.outputs.keyVaultName) : ''

module backendDatabaseUrlSecret 'br/public:avm/res/key-vault/vault/secret:0.1.0' = if (shouldUseKeyVaultBackedSecrets) {
  name: take('avm.res.key-vault.vault.secret.${backendDatabaseUrlSecretName}', 64)
  params: {
    keyVaultName: aiFoundry.outputs.keyVaultName
    name: backendDatabaseUrlSecretName
    value: backendDatabaseUrl
    enableTelemetry: enableTelemetry
  }
}

module aiFoundry 'br/public:avm/ptn/ai-ml/ai-foundry:0.6.0' = {
  name: '${baseName}-ai-foundry'
  params: {
    baseName: baseName
    baseUniqueName: baseUniqueName
    location: location
    tags: tags
    enableTelemetry: enableTelemetry
    includeAssociatedResources: includeAssociatedResources
    aiModelDeployments: aiModelDeployments
    aiFoundryConfiguration: {
      sku: aiFoundrySku
      allowProjectManagement: true
      disableLocalAuth: true
      createCapabilityHosts: includeAssociatedResources
      project: {
        name: resolvedProjectName
        displayName: resolvedProjectDisplayName
        desc: projectDescription
      }
      roleAssignments: cognitiveServicesRoleAssignments
    }
  }
}

var storageAccountName = includeAssociatedResources ? aiFoundry.outputs.storageAccountName : ''
module knowledgeStorage './modules/knowledge-storage.bicep' = if (shouldCreateKnowledgeArtifacts) {
  name: '${baseName}-knowledge-storage'
  params: {
    storageAccountName: storageAccountName
    brandDataContainerName: brandDataContainerName
    draftsContainerName: draftsContainerName
    draftsShareName: draftsShareName
  }
}

module containerRegistry 'br/public:avm/res/container-registry/registry:0.9.3' = if (deployApplicationHosting) {
  name: take('avm.res.container-registry.registry.${acrName}', 64)
  params: {
    name: acrName
    location: appHostingLocation
    tags: tags
    acrSku: containerRegistrySku
    acrAdminUserEnabled: false
    enableTelemetry: enableTelemetry
  }
}

module containerAppsEnvironment 'br/public:avm/res/app/managed-environment:0.11.3' = if (deployApplicationHosting) {
  name: take('avm.res.app.managed-environment.${containerAppsEnvironmentName}', 64)
  params: {
    name: containerAppsEnvironmentName
    location: appHostingLocation
    tags: tags
    zoneRedundant: false
    enableTelemetry: enableTelemetry
  }
}

module backendContainerApp 'br/public:avm/res/app/container-app:0.20.0' = if (deployApplicationHosting) {
  name: take('avm.res.app.container-app.${backendContainerAppName}', 64)
  params: {
    name: backendContainerAppName
    location: appHostingLocation
    tags: tags
    environmentResourceId: containerAppsEnvironment!.outputs.resourceId
    managedIdentities: {
      systemAssigned: true
    }
    activeRevisionsMode: 'Single'
    ingressExternal: true
    ingressTargetPort: 8000
    ingressTransport: 'auto'
    ingressAllowInsecure: false
    secrets: shouldUseKeyVaultBackedSecrets
      ? [
          {
            name: backendDatabaseUrlSecretName
            keyVaultUrl: backendDatabaseUrlSecretUri
            identity: 'system'
          }
        ]
      : []
    registries: [
      {
        server: containerRegistry!.outputs.loginServer
        identity: 'system'
      }
    ]
    containers: [
      {
        name: 'backend'
        image: backendContainerImage
        resources: {
          cpu: backendCpu
          memory: backendMemory
        }
        env: concat(
          [
            {
              name: 'APP_HOST'
              value: '0.0.0.0'
            }
            {
              name: 'APP_PORT'
              value: '8000'
            }
            {
              name: 'ASPNETCORE_HTTP_PORTS'
              value: '8000'
            }
            {
              name: 'ASPNETCORE_URLS'
              value: 'http://+:8000'
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: backendOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: backendOpenAiApiVersion
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: backendChatDeploymentName
            }
            {
              name: 'AZURE_OPENAI_GPT5_DEPLOYMENT_NAME'
              value: backendSecondaryDeploymentName
            }
            {
              name: 'AZURE_OPENAI_CODEX_DEPLOYMENT_NAME'
              value: backendCodexDeploymentName
            }
            {
              name: 'AZURE_OPENAI_TEXTEMBEDDING_DEPLOYMENT_NAME'
              value: backendEmbeddingDeploymentName
            }
            {
              name: 'ALLOWED_ORIGINS'
              value: '["${frontendApiUrl}"]'
            }
          ],
          shouldUseKeyVaultBackedSecrets
            ? [
                {
                  name: 'DATABASE_URL'
                  secretRef: backendDatabaseUrlSecretName
                }
              ]
            : [
                {
                  name: 'DATABASE_URL'
                  value: backendDatabaseUrl
                }
              ]
        )
      }
    ]
    scaleSettings: {
      minReplicas: 1
      maxReplicas: 2
    }
    enableTelemetry: enableTelemetry
  }
}

module frontendContainerApp 'br/public:avm/res/app/container-app:0.20.0' = if (deployApplicationHosting) {
  name: take('avm.res.app.container-app.${frontendContainerAppName}', 64)
  params: {
    name: frontendContainerAppName
    location: appHostingLocation
    tags: tags
    environmentResourceId: containerAppsEnvironment!.outputs.resourceId
    managedIdentities: {
      systemAssigned: true
    }
    activeRevisionsMode: 'Single'
    ingressExternal: true
    ingressTargetPort: 3000
    ingressTransport: 'auto'
    ingressAllowInsecure: false
    registries: [
      {
        server: containerRegistry!.outputs.loginServer
        identity: 'system'
      }
    ]
    containers: [
      {
        name: 'frontend'
        image: frontendContainerImage
        resources: {
          cpu: frontendCpu
          memory: frontendMemory
        }
        env: [
          {
            name: 'ASPNETCORE_HTTP_PORTS'
            value: '3000'
          }
          {
            name: 'ASPNETCORE_URLS'
            value: 'http://+:3000'
          }
          {
            name: 'NEXT_PUBLIC_API_URL'
            value: backendApiUrl
          }
          {
            name: 'NEXT_PUBLIC_WS_URL'
            value: backendWsUrl
          }
        ]
      }
    ]
    scaleSettings: {
      minReplicas: 1
      maxReplicas: 2
    }
    enableTelemetry: enableTelemetry
  }
}

module backendAcrPullAssignment 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = if (deployApplicationHosting) {
  name: take('avm.ptn.authorization.resource-role-assignment.backend.${backendContainerAppName}', 64)
  params: {
    principalId: backendContainerApp!.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
    resourceId: containerRegistry!.outputs.resourceId
    roleDefinitionId: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    roleName: 'AcrPull'
  }
}

module frontendAcrPullAssignment 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = if (deployApplicationHosting) {
  name: take('avm.ptn.authorization.resource-role-assignment.frontend.${frontendContainerAppName}', 64)
  params: {
    principalId: frontendContainerApp!.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
    resourceId: containerRegistry!.outputs.resourceId
    roleDefinitionId: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    roleName: 'AcrPull'
  }
}

module backendContainerAppKeyVaultSecretsUserRoleAssignment 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.2' = if (shouldUseKeyVaultBackedSecrets) {
  name: take('avm.ptn.authorization.resource-role-assignment.kv.${backendContainerAppName}', 64)
  params: {
    principalId: backendContainerApp!.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
    resourceId: keyVaultResourceId
    roleDefinitionId: '4633458b-17de-408a-b874-0445c86b69e6'
    roleName: 'Key Vault Secrets User'
  }
}

module sqlServer 'br/public:avm/res/sql/server:0.21.1' = if (shouldDeployAzureSql) {
  name: take('avm.res.sql.server.${resolvedSqlServerName}', 64)
  params: {
    name: resolvedSqlServerName
    location: location
    tags: tags
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorLoginPassword
    connectionPolicy: 'Redirect'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    firewallRules: sqlAllowAzureServices
      ? [
          {
            name: 'AllowAzureServices'
            startIpAddress: '0.0.0.0'
            endIpAddress: '0.0.0.0'
          }
        ]
      : []
    databases: [
      {
        availabilityZone: -1
        name: sqlDatabaseName
        sku: {
          name: sqlDatabaseSkuName
          tier: sqlDatabaseSkuTier
        }
        zoneRedundant: false
      }
    ]
    enableTelemetry: enableTelemetry
  }
}

output aiFoundryAccountName string = aiFoundry.outputs.aiServicesName
output aiProjectName string = aiFoundry.outputs.aiProjectName
output aiSearchName string = includeAssociatedResources ? aiFoundry.outputs.aiSearchName : ''
output cosmosAccountName string = includeAssociatedResources ? aiFoundry.outputs.cosmosAccountName : ''
output keyVaultName string = includeAssociatedResources ? aiFoundry.outputs.keyVaultName : ''
output storageAccountOutputName string = storageAccountName
output brandDataContainerResourceId string = shouldCreateKnowledgeArtifacts ? knowledgeStorage!.outputs.brandDataContainerResourceId : ''
output draftsContainerResourceId string = shouldCreateKnowledgeArtifacts ? knowledgeStorage!.outputs.draftsContainerResourceId : ''
output draftsShareResourceId string = shouldCreateKnowledgeArtifacts ? knowledgeStorage!.outputs.draftsShareResourceId : ''
output containerRegistryName string = deployApplicationHosting ? containerRegistry!.outputs.name : ''
output containerRegistryLoginServer string = deployApplicationHosting ? containerRegistry!.outputs.loginServer : ''
output containerAppsEnvironmentId string = deployApplicationHosting ? containerAppsEnvironment!.outputs.resourceId : ''
output backendContainerAppResourceId string = deployApplicationHosting ? backendContainerApp!.outputs.resourceId : ''
output frontendContainerAppResourceId string = deployApplicationHosting ? frontendContainerApp!.outputs.resourceId : ''
output backendContainerAppName string = deployApplicationHosting ? backendContainerApp!.outputs.name : ''
output frontendContainerAppName string = deployApplicationHosting ? frontendContainerApp!.outputs.name : ''
output backendEndpoint string = deployApplicationHosting ? 'https://${backendContainerApp!.outputs.fqdn}' : ''
output frontendEndpoint string = deployApplicationHosting ? 'https://${frontendContainerApp!.outputs.fqdn}' : ''
output sqlServerNameOutput string = shouldDeployAzureSql ? sqlServer!.outputs.name : ''
output sqlServerResourceId string = shouldDeployAzureSql ? sqlServer!.outputs.resourceId : ''
output sqlServerFullyQualifiedDomainName string = shouldDeployAzureSql ? sqlServer!.outputs.fullyQualifiedDomainName : ''
output sqlDatabaseNameOutput string = shouldDeployAzureSql ? sqlDatabaseName : ''
