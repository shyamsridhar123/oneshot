using '../main.bicep'

param baseName = 'techvista-smc-prod'
param location = 'westus3'
param aiFoundrySku = 'S1'
param tags = {
  environment: 'prod'
  workload: 'social-media-command-center'
  data_classification: 'internal'
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
      capacity: 2
    }
  }
  {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-reasoning'
      version: '2024-11-20'
    }
    name: 'gpt-4o-reasoning'
    sku: {
      name: 'Standard'
      capacity: 1
    }
  }
]
param brandDataContainerName = 'brand-knowledge'
param draftsContainerName = 'mcp-drafts'
param draftsShareName = 'publish-ready'
