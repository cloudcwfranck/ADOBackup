import json
import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, Callable

from azure.devops.connection import Connection
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_1.build import BuildClient
from azure.devops.v7_1.release import ReleaseClient
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from azure.devops.v7_1.work import WorkClient
from azure.devops.v7_1.core.models import TeamProjectReference
from azure.devops.v7_1.work.models import TeamContext
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient
from msrest.authentication import BasicAuthentication
from adobackup.core.storage_manager import StorageManager


class RestoreEngine:
    """Handles complete restoration of Azure DevOps components from backups"""

    def __init__(self, target_org: str, target_pat: str):
        self.target_org = target_org
        self.target_pat = target_pat
        self.connection = Connection(
            base_url=f"https://dev.azure.com/{target_org}",
            creds=BasicAuthentication("", target_pat)
        )
        self.logger = logging.getLogger(__name__)
        self._progress_callback = None
        self.logger.info(f"Initialized restore engine for {target_org}")

    def set_progress_callback(self, callback: Callable[[int, str], None]):
        self._progress_callback = callback

    def _update_progress(self, percent: int, message: str):
        if self._progress_callback:
            self._progress_callback(percent, message)

    def restore_all(self, backup_source: str) -> bool:
        try:
            self._update_progress(0, "Starting restore process...")
            data = self._load_backup_data(backup_source)
            self._update_progress(10, "Backup data loaded")

            self._restore_projects(data.get("projects", []))
            self._update_progress(20, "Projects restored")

            self._restore_repos(data.get("repos", []))
            self._update_progress(40, "Repositories restored")

            self._restore_boards(data.get("boards", {}))
            self._update_progress(60, "Boards and work items restored")

            self._restore_pipelines(data.get("pipelines", {}))
            self._update_progress(80, "Pipelines restored")

            self._restore_artifacts(data.get("artifacts", []))
            self._update_progress(90, "Artifacts restored")

            self._update_progress(100, "Restore completed successfully")
            self.logger.info("Restore completed successfully")
            return True

        except AzureError as e:
            self.logger.error(f"Azure operation failed: {str(e)}")
            self._update_progress(-1, f"Azure error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            self._update_progress(-1, f"Restore failed: {str(e)}")
            raise

    def _load_backup_data(self, source: str) -> dict:
        try:
            if source == "Local Storage":
                backup_path = Path("backups/latest_backup.json")
                if not backup_path.exists():
                    raise FileNotFoundError(f"Backup file not found at {backup_path}")

                self.logger.info("Loading backup from local storage...")
                with open(backup_path, 'r') as f:
                    return json.load(f)

            elif source == "Azure Blob Storage":
                self.logger.info("Downloading backup from Azure Blob Storage...")
                download_path = StorageManager().download_to_file()
                with open(download_path, 'r') as f:
                    return json.load(f)

            else:
                raise ValueError(f"Unknown backup source: {source}")

        except Exception as e:
            self.logger.error(f"Failed to load backup data: {str(e)}")
            raise

    def _restore_projects(self, projects: list[dict]):
        core_client = self.connection.clients.get_core_client()
        existing_projects = {p.name: p for p in core_client.get_projects()}

        for project in projects:
            if project["name"] not in existing_projects:
                try:
                    self.logger.info(f"Creating project {project['name']}")
                    core_client.queue_create_project(
                        TeamProjectReference(
                            name=project["name"],
                            description=project.get("description", ""),
                            capabilities=project.get("capabilities", {})
                        )
                    )
                except AzureError as e:
                    if "already exists" not in str(e):
                        raise

    def _restore_repos(self, repos: list[dict]):
        git_client = self.connection.clients.get_git_client()

        for repo in repos:
            try:
                existing_repos = git_client.get_repositories(repo["project"])
                if not any(r.name == repo["name"] for r in existing_repos):
                    git_client.create_repository(
                        {"name": repo["name"], "project": repo["project"]},
                        repo["project"]
                    )
                    self.logger.info(f"Created repository {repo['name']}")

                self.logger.info(f"Mirroring repository {repo['name']}...")
                subprocess.run([
                    "git", "push", "--mirror",
                    f"https://{self.target_pat}@dev.azure.com/{self.target_org}/{repo['project']}/_git/{repo['name']}"
                ], cwd=repo["local_path"], check=True)

                self.logger.info(f"Successfully restored repo {repo['name']}")

            except subprocess.CalledProcessError as e:
                self.logger.error(f"Git push failed for {repo['name']}: {str(e)}")
                raise
            except AzureError as e:
                self.logger.error(f"Azure operation failed for {repo['name']}: {str(e)}")
                raise

    def _restore_boards(self, boards_data: dict):
        wit_client = self.connection.clients.get_work_item_tracking_client()
        work_client = self.connection.clients.get_work_client()

        for project_name, iterations in boards_data.get("iterations", {}).items():
            try:
                team_context = TeamContext(project=project_name)
                existing_iterations = {i.name: i for i in work_client.get_team_iterations(team_context)}

                for iteration in iterations:
                    if iteration["name"] not in existing_iterations:
                        work_client.post_team_iteration(iteration, team_context)
                        self.logger.info(f"Created iteration {iteration['name']}")
            except AzureError as e:
                self.logger.error(f"Failed to restore iterations for {project_name}: {str(e)}")
                raise

        for wi in boards_data.get("work_items", []):
            try:
                wit_client.create_work_item(
                    document=wi["fields"],
                    project=wi["project"],
                    type=wi["type"]
                )
                self.logger.info(f"Created work item {wi['id']} ({wi['type']})")
            except AzureError as e:
                self.logger.error(f"Failed to process work item {wi['id']}: {str(e)}")
                raise

    def _restore_pipelines(self, pipelines_data: dict):
        build_client = self.connection.clients.get_build_client()
        release_client = self.connection.clients.get_release_client()

        for build_def in pipelines_data.get("builds", []):
            try:
                existing_defs = build_client.get_definitions(build_def["project"])
                if not any(d.name == build_def["name"] for d in existing_defs):
                    build_client.create_definition(build_def, project=build_def["project"])
                    self.logger.info(f"Created build pipeline {build_def['name']}")
            except AzureError as e:
                self.logger.error(f"Failed to restore build pipeline {build_def['name']}: {str(e)}")
                raise

        for release_def in pipelines_data.get("releases", []):
            try:
                existing_defs = release_client.get_release_definitions(release_def["project"])
                if not any(d.name == release_def["name"] for d in existing_defs):
                    release_client.create_definition(release_def, project=release_def["project"])
                    self.logger.info(f"Created release pipeline {release_def['name']}")
            except AzureError as e:
                self.logger.error(f"Failed to restore release pipeline {release_def['name']}: {str(e)}")
                raise

    def _restore_artifacts(self, artifacts: list[dict]):
        self.logger.warning("Artifact restoration not yet implemented")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    def progress_callback(percent: int, message: str):
        print(f"[{percent}%] {message}")

    engine = RestoreEngine("your-org", "your-pat")
    engine.set_progress_callback(progress_callback)

    try:
        engine.restore_all("Local Storage")
    except Exception as e:
        print(f"Restore failed: {str(e)}")
