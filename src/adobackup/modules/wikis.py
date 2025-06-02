import requests
import subprocess
import base64
from azure.devops.connection import Connection

class WikisModule:
    def __init__(self, connection: Connection, pat: str):
        self.connection = connection
        self.pat = pat
        self.base_url = connection.base_url
        self.headers = {
            "Authorization": f"Basic {self._encode_pat()}",
            "Content-Type": "application/json"
        }

    def _encode_pat(self):
        return base64.b64encode(f":{self.pat}".encode()).decode()

    def backup(self, backup_path):
        wikis_path = backup_path / "wikis"
        wikis_path.mkdir(exist_ok=True)

        core_client = self.connection.clients.get_core_client()
        projects = core_client.get_projects()
        results = []

        for project in projects:
            try:
                url = f"{self.base_url}/{project.name}/_apis/wiki/wikis?api-version=7.1-preview.1"
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                wikis = response.json().get("value", [])

                for wiki in wikis:
                    try:
                        subprocess.run([
                            "git", "clone", "--mirror",
                            wiki["remoteUrl"],
                            str(wikis_path / f"{wiki['name']}.git")
                        ], check=True)
                        results.append({
                            "project": project.name,
                            "name": wiki["name"],
                            "status": "success"
                        })
                    except subprocess.CalledProcessError as e:
                        results.append({
                            "project": project.name,
                            "name": wiki["name"],
                            "status": "failed",
                            "error": str(e)
                        })

            except Exception as e:
                results.append({
                    "project": project.name,
                    "status": "error",
                    "error": str(e)
                })

        return results
