targetScope = 'resourceGroup'

@description('Friendly base name for the AI Foundry resources. Used by the AVM module when generating resource names.')
@minLength(3)
param baseName string

@description('Azure region for the deployment. Defaults to the current resource group location.')
param location string = resourceGroup().location

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

@description('Container image placeholder used during initial backend container app provisioning before azd deploys application images.')
param backendContainerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Container image placeholder used during initial frontend container app provisioning before azd deploys application images.')
param frontendContainerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('CPU cores allocated to the backend container app revision.')
param backendCpu int = 1

@description('Memory allocated to the backend container app revision.')
param backendMemory string = '2Gi'

@description('CPU cores allocated to the frontend container app revision.')
param frontendCpu int = 1

@description('Memory allocated to the frontend container app revision.')
param frontendMemory string = '2Gi'

var resolvedProjectName = projectName == '' ? '${baseName}-project' : projectName
var resolvedProjectDisplayName = projectDisplayName == '' ? '${baseName} Social Media Command Center' : projectDisplayName
var shouldCreateKnowledgeArtifacts = createKnowledgeContainers && includeAssociatedResources
var acrName = toLower('acr${baseUniqueName}${uniqueString(baseName, resourceGroup().id)}')
var containerAppsEnvironmentName = take('${baseName}-cae', 60)
var backendContainerAppName = take('${baseName}-backend', 32)
var frontendContainerAppName = take('${baseName}-frontend', 32)

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
    location: location
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
    location: location
    tags: tags
    zoneRedundant: false
    enableTelemetry: enableTelemetry
  }
}

module backendContainerApp 'br/public:avm/res/app/container-app:0.19.0' = if (deployApplicationHosting) {
  name: take('avm.res.app.container-app.${backendContainerAppName}', 64)
  params: {
    name: backendContainerAppName
    location: location
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
        env: [
          {
            name: 'APP_HOST'
            value: '0.0.0.0'
          }
          {
            name: 'APP_PORT'
            value: '8000'
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

module frontendContainerApp 'br/public:avm/res/app/container-app:0.19.0' = if (deployApplicationHosting) {
  name: take('avm.res.app.container-app.${frontendContainerAppName}', 64)
  params: {
    name: frontendContainerAppName
    location: location
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
