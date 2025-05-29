import logging
from typing import List, Dict, Optional
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work_item_tracking.models import Wiql, WorkItem
from azure.devops.connection import Connection
from azure.core.exceptions import AzureError

class BoardsModule:
    """Handles Azure DevOps Boards operations including work items and queries"""
    
    def __init__(self, connection: Connection):
        """
        Initialize Boards module with Azure DevOps connection
        
        Args:
            connection: Authenticated Connection object
        """
        self.logger = logging.getLogger(__name__)
        self.client = connection.clients.get_work_item_tracking_client()
        self.logger.info("Boards client initialized")

    def get_all_boards(self, project_name: str) -> List[dict]:
        """Get all boards in a project"""
        try:
            return self.client.get_boards(project_name).value
        except AzureError as e:
            self.logger.error(f"Failed to get boards: {e}")
            raise

    def get_work_item(self, id: int, project_name: str) -> WorkItem:
        """Get single work item by ID"""
        try:
            return self.client.get_work_item(id, project=project_name)
        except AzureError as e:
            self.logger.error(f"Failed to get work item {id}: {e}")
            raise

    def query_work_items(self, wiql_query: str, project_name: str) -> List[WorkItem]:
        """Execute WIQL query and return work items"""
        try:
            query = Wiql(query=wiql_query)
            result = self.client.query_by_wiql(query, project=project_name)
            if result.work_items:
                return self.client.get_work_items(
                    [wi.id for wi in result.work_items],
                    project=project_name
                )
            return []
        except AzureError as e:
            self.logger.error(f"Query failed: {e}")
            raise

    def create_work_item(
        self, 
        project_name: str, 
        work_item_type: str, 
        fields: Dict[str, str]
    ) -> WorkItem:
        """Create new work item with specified fields"""
        try:
            return self.client.create_work_item(
                document=fields,
                project=project_name,
                type=work_item_type
            )
        except AzureError as e:
            self.logger.error(f"Creation failed: {e}")
            raise

    def update_work_item(
        self,
        id: int,
        project_name: str,
        updates: List[dict]
    ) -> WorkItem:
        """Update existing work item"""
        try:
            return self.client.update_work_item(
                document=updates,
                project=project_name,
                id=id
            )
        except AzureError as e:
            self.logger.error(f"Update failed: {e}")
            raise