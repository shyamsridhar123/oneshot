targetScope = 'resourceGroup'

@description('Name of the existing storage account where knowledge artifacts should be created.')
param storageAccountName string

@description('Blob container for curated brand knowledge artifacts.')
param brandDataContainerName string

@description('Blob container for generated drafts / MCP outputs.')
param draftsContainerName string

@description('Azure Files share that stores downloadable drafts for MCP tooling.')
param draftsShareName string

module brandContainer 'br/public:avm/res/storage/storage-account/blob-service/container:0.3.2' = {
  name: take('avm.res.storage.storage-account.blob-service.container.${brandDataContainerName}', 64)
  params: {
    storageAccountName: storageAccountName
    blobServiceName: 'default'
    name: brandDataContainerName
    publicAccess: 'None'
  }
}

module draftsContainer 'br/public:avm/res/storage/storage-account/blob-service/container:0.3.2' = if (toLower(brandDataContainerName) != toLower(draftsContainerName)) {
  name: take('avm.res.storage.storage-account.blob-service.container.${draftsContainerName}', 64)
  params: {
    storageAccountName: storageAccountName
    blobServiceName: 'default'
    name: draftsContainerName
    publicAccess: 'None'
  }
}

module draftsShare 'br/public:avm/res/storage/storage-account/file-service/share:0.1.2' = {
  name: take('avm.res.storage.storage-account.file-service.share.${draftsShareName}', 64)
  params: {
    storageAccountName: storageAccountName
    fileServicesName: 'default'
    name: draftsShareName
    accessTier: 'Hot'
  }
}

output brandDataContainerResourceId string = brandContainer.outputs.resourceId
output draftsContainerResourceId string = toLower(brandDataContainerName) == toLower(draftsContainerName)
  ? brandContainer.outputs.resourceId
  : draftsContainer!.outputs.resourceId
output draftsShareResourceId string = draftsShare.outputs.resourceId
