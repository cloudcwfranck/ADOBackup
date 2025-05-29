from datetime import datetime
from azure.devops.v6_0.connection import Connection
from msrest.authentication import BasicAuthentication
from adobackup.modules.boards import BoardsModule
from adobackup.modules.repos import ReposModule
from adobackup.modules.pipelines import PipelinesModule
from adobackup.modules.testplans import TestPlansModule
from adobackup.modules.artifacts import ArtifactsModule
from adobackup.modules.wikis import WikisModule
import os
from pathlib import Path
import json

class BackupEngine:
    def __init__(self, org_url, pat):
        self.connection = Connection(
            base_url=f"https://dev.azure.com/{org_url}",
            creds=BasicAuthentication('', pat)
        )
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    def backup_all(self, components):
        """Backup all selected components"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir()

        results = {
            "metadata": {
                "date": timestamp,
                "organization": self.connection.base_url,
                "components": components
            },
            "data": {}
        }

        # Backup each requested component
        if "Boards" in components:
            results["data"]["boards"] = BoardsModule(self.connection).backup(backup_path)

        if "Repos" in components:
            results["data"]["repos"] = ReposModule(self.connection).backup(backup_path)

        if "Pipelines" in components:
            results["data"]["pipelines"] = PipelinesModule(self.connection).backup(backup_path)

        if "Test Plans" in components:
            results["data"]["testplans"] = TestPlansModule(self.connection).backup(backup_path)

        if "Artifacts" in components:
            results["data"]["artifacts"] = ArtifactsModule(self.connection).backup(backup_path)

        if "Wikis" in components:
            results["data"]["wikis"] = WikisModule(self.connection).backup(backup_path)

        # Save metadata
        with open(backup_path / "backup_manifest.json", "w") as f:
            json.dump(results, f, indent=2)

        return results