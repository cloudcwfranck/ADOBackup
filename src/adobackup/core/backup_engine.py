from datetime import datetime
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from ..modules.boards import BoardsModule
from ..modules.repos import ReposModule
from adobackup.modules.pipelines import PipelinesModule
from adobackup.modules.testplans import TestPlansModule
from adobackup.modules.artifacts import ArtifactsModule
from adobackup.modules.wikis import WikisModule
import os
from pathlib import Path
import json
import zipfile

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
        if not components:
            raise ValueError("No components selected for backup.")

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

        module_map = {
            "Boards": BoardsModule,
            "Repos": ReposModule,
            "Pipelines": PipelinesModule,
            "Test Plans": TestPlansModule,
            "Artifacts": ArtifactsModule,
            "Wikis": WikisModule
        }

        for name, module in module_map.items():
            if name in components:
                print(f"🔍 Backing up: {name}")
                try:
                    module_instance = module(self.connection)
                    backup_data = module_instance.backup(backup_path)
                    print(f"📁 {name} data size: {len(str(backup_data)) if backup_data else 0}")
                    results["data"][name.lower().replace(" ", "")] = backup_data
                except Exception as e:
                    print(f"❌ Failed to backup {name}: {str(e)}")

        # Save metadata
        with open(backup_path / "backup_manifest.json", "w") as f:
            json.dump(results, f, indent=2)

        return results, str(backup_path / "backup_manifest.json")

    def save_to_local(self, results: dict, path: str = "backups/latest_backup.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(results, f, indent=2)

    def zip_backup(self, source_json: str = "backups/latest_backup.json", output_zip: str = "backups/latest_backup.zip"):
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            zipf.write(source_json, arcname=os.path.basename(source_json))
