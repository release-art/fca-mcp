"""Top-level Azure API interface for Flow Shelf."""

import contextlib
import logging

import azure.data.tables.aio as azure_tables_aio
import azure.storage.blob.aio as azure_blob_aio
import azure.storage.queue.aio as azure_queue_aio
from azure.identity.aio import DefaultAzureCredential

import fca_mcp

from .. import settings as app_settings_module

logger = logging.getLogger(__name__)


class AzureAPI:
    """Azure API interface for Flow Shelf."""

    settings: app_settings_module.AzureSettings
    queue_service_client: azure_queue_aio.QueueServiceClient
    blob_service_client: azure_blob_aio.BlobServiceClient
    table_service_client: azure_tables_aio.TableServiceClient

    def __init__(self, settings: app_settings_module.AzureSettings) -> None:
        self.settings = settings
        # When using connection string with AccountKey (Azurite), don't pass credential
        # When using DefaultAzureCredential (production), pass it explicitly
        if self.settings.credential == fca_mcp.settings.AzureCredentialType.NONE:
            self.queue_service_client = azure_queue_aio.QueueServiceClient.from_connection_string(
                conn_str=self.settings.storage_connection_string,
            )
            self.blob_service_client = azure_blob_aio.BlobServiceClient.from_connection_string(
                conn_str=self.settings.storage_connection_string,
            )
            self.table_service_client = azure_tables_aio.TableServiceClient.from_connection_string(
                conn_str=self.settings.storage_connection_string,
            )
        elif self.settings.credential == fca_mcp.settings.AzureCredentialType.DEFAULT:
            credential = DefaultAzureCredential()
            self.queue_service_client = azure_queue_aio.QueueServiceClient.from_connection_string(
                conn_str=self.settings.storage_connection_string,
                credential=credential,
            )
            self.blob_service_client = azure_blob_aio.BlobServiceClient.from_connection_string(
                conn_str=self.settings.storage_connection_string,
                credential=credential,
            )
            self.table_service_client = azure_tables_aio.TableServiceClient.from_connection_string(
                conn_str=self.settings.storage_connection_string,
                credential=credential,
            )
        else:
            raise ValueError(f"Unsupported Azure credential type: {self.settings.credential}")

    @contextlib.asynccontextmanager
    async def lifespan(self):
        """Lifespan context manager for Azure API."""
        logger.info("Starting Azure API lifespan...")
        try:
            async with self.queue_service_client, self.blob_service_client, self.table_service_client:
                logger.info("Connected to Azure Services.")
                yield
                logger.debug("Azure API operations completed successfully.")
        finally:
            logger.info("Azure API lifespan ended.")

    async def get_queue(self, queue_name: str) -> azure_queue_aio.QueueClient:
        """Get a QueueClient for the specified queue."""
        return self.queue_service_client.get_queue_client(queue=queue_name)

    async def get_blob_container(self, container_name: str) -> azure_blob_aio.ContainerClient:
        """Get a ContainerClient for the specified blob container."""
        return self.blob_service_client.get_container_client(container=container_name)
