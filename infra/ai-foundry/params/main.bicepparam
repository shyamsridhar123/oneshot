using '../main.bicep'

param baseName = 'oneshot-smc'
param location = 'eastus'
param tags = {
  environment: 'shared'
  workload: 'social-media-command-center'
}
param aiModelDeployments = [
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
  {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-mini'
      version: '2024-12-17'
    }
    name: 'gpt-4o-mini'
    sku: {
      name: 'Standard'
      capacity: 1
    }
  }
]
param projectDescription = 'Multi-agent reasoning workspace powering TechVista social media command center.'
param brandDataContainerName = 'brand-data'
param draftsContainerName = 'drafts'
param draftsShareName = 'drafts'
param cognitiveServicesRoleAssignments = []
