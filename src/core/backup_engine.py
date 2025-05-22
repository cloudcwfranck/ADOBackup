from datetime import datetime
from pathlib import Path
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import json

class BackupEngine:
    def __init__(self, org_url, pat):
        self.connection = Connection(
            base_url=f"https://dev.azure.com/{org_url}",
            creds=BasicAuthentication('', pat))
    
    def backup_all(self, components):
        results = {}
        
        if "Repos" in components:
            from modules.repos import ReposModule
            results["repos"] = ReposModule(self.connection).backup()
        
        if "Boards" in components:
            from modules.boards import BoardsModule
            results["boards"] = BoardsModule(self.connection).backup()
            
        return {
            "metadata": {
                "date": datetime.now().isoformat(),
                "components": components
            },
            "data": results
        }
