import logging
from typing import List, Dict
from azure.devops.connection import Connection
from azure.core.exceptions import AzureError
from azure.devops.v7_1.work_item_tracking.models import Wiql
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work import WorkClient
from azure.devops.v7_1.core import CoreClient
from azure.devops.v7_1.work.models import TeamContext

class BoardsModule:
    """Handles Azure DevOps Boards operations and full backup."""

    def __init__(self, connection: Connection):
        self.logger = logging.getLogger(__name__)
        self.connection = connection
        self.core_client: CoreClient = connection.clients.get_core_client()
        self.wit_client: WorkItemTrackingClient = connection.clients.get_work_item_tracking_client()
        self.work_client: WorkClient = connection.clients.get_work_client()
        self.logger.info("BoardsModule initialized.")

    def backup(self, backup_path):
        data = {
            "projects": [],
            "iterations": {},
            "work_items": []
        }

        try:
            projects = self.core_client.get_projects()
        except Exception as e:
            self.logger.error(f"Failed to fetch projects: {str(e)}")
            return data

        for project in projects:
            data["projects"].append({"id": project.id, "name": project.name})

            # Fetch all iterations
            try:
                # Ensure project has teams
                teams = self.core_client.get_teams(project.id)
                if teams:
                    default_team = teams[0].name
                    team_context = TeamContext(project=project.name, team=default_team)

                    iterations = self.work_client.get_team_iterations(team_context)
                    self.logger.info(f"✅ Fetched {len(iterations)} iterations for {project.name}")
                    data["iterations"][project.name] = [
                        {
                            "id": it.id,
                            "name": it.name,
                            "path": it.path,
                            "start": str(it.attributes.start_date) if it.attributes.start_date else None,
                            "end": str(it.attributes.finish_date) if it.attributes.finish_date else None
                        }
                        for it in iterations
                    ]
                else:
                    self.logger.warning(f"⚠️ No teams found for project {project.name}")
            except Exception as e:
                self.logger.warning(f"⚠️ Iterations failed for {project.name}: {str(e)}")

            # Fetch all work items
            try:
                wiql = Wiql(query="""
                    SELECT [System.Id] 
                    FROM WorkItems 
                    WHERE [System.WorkItemType] <> '' 
                    AND [System.State] <> ''
                    ORDER BY [System.ChangedDate] DESC
                """)
                result = self.wit_client.query_by_wiql(wiql, project=project.name)

                if not result.work_items:
                    self.logger.warning(f"⚠️ No work items found in {project.name}")
                else:
                    self.logger.info(f"✅ Found {len(result.work_items)} work items in {project.name}")

                ids = [wi.id for wi in result.work_items]
                self.logger.info(f"📋 Work Item IDs: {ids}")

                if ids:
                    for i in range(0, len(ids), 200):
                        batch = ids[i:i + 200]
                        items = self.wit_client.get_work_items(
                            batch, fields=["System.Id", "System.Title", "System.State"]
                        )
                        for item in items:
                            data["work_items"].append({
                                "id": item.id,
                                "fields": item.fields,
                                "project": project.name
                            })
            except Exception as e:
                self.logger.warning(f"⚠️ Work items failed for {project.name}: {str(e)}")

        return data