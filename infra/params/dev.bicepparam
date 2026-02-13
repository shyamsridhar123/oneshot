using '../main.bicep'

param baseName = 'oneshot-dev'
param location = 'eastus2'
param tags = {
  environment: 'dev'
  workload: 'social-media-command-center'
  owner: 'hackathon-team'
}
param aiModelDeployments = [
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
param brandDataContainerName = 'dev-brand-data'
param draftsContainerName = 'dev-agent-drafts'
param draftsShareName = 'dev-drafts'
param sqlAdministratorLogin = 'oneshotdevsqladmin'
param sqlAdministratorLoginPassword = readEnvironmentVariable('AZURE_SQL_ADMIN_PASSWORD', '')
param sqlDatabaseName = 'oneshotdevdb'
param sqlDatabaseSkuName = 'S0'
param sqlDatabaseSkuTier = 'Standard'
param sqlAllowAzureServices = true
