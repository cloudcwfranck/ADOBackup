from azure.devops.v6_0.wiki import WikiClient
import subprocess
import json

class WikisModule:
    def __init__(self, connection):
        self.client = connection.clients.get_wiki_client()
    
    def backup(self, backup_path):
        wikis_path = backup_path / "wikis"
        wikis_path.mkdir(exist_ok=True)
        
        wikis = self.client.list_wikis()
        results = []
        
        for wiki in wikis:
            try:
                subprocess.run([
                    "git", "clone", "--mirror",
                    wiki.remote_url,
                    str(wikis_path / f"{wiki.name}.git")
                ], check=True)
                results.append({
                    "name": wiki.name,
                    "status": "success"
                })
            except subprocess.CalledProcessError as e:
                results.append({
                    "name": wiki.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results