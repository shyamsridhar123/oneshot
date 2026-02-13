using '../main.bicep'

param baseName = 'oneshot-platform'
param location = 'eastus'
param appHostingLocation = readEnvironmentVariable('AZURE_APP_HOSTING_LOCATION', 'eastus2')
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
  {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-small'
      version: '1'
    }
    name: 'text-embedding-3-small'
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
param sqlAdministratorLogin = 'oneshotsqladmin'
param sqlAdministratorLoginPassword = readEnvironmentVariable('AZURE_SQL_ADMIN_PASSWORD', '')
param sqlDatabaseName = 'oneshotdb'
param sqlDatabaseSkuName = 'S1'
param sqlDatabaseSkuTier = 'Standard'
param sqlAllowAzureServices = true
param cognitiveServicesRoleAssignments = []
