from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import subprocess
from pathlib import Path

class ReposModule:
    def __init__(self, org, pat):
        self.org = org
        self.pat = pat
        
    def backup(self):
        print("📦 Backing up repositories...")
        connection = Connection(
            base_url=f"https://dev.azure.com/{self.org}",
            creds=BasicAuthentication('', self.pat))
        
        git_client = connection.clients.get_git_client()
        repos = git_client.get_repositories()
        
        backup_dir = Path("backups/repos")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for repo in repos:
            repo_dir = backup_dir / f"{repo.name}.git"
            try:
                subprocess.run([
                    "git", "clone", "--mirror",
                    repo.remote_url,
                    str(repo_dir)
                ], check=True, capture_output=True)
                results.append({
                    "name": repo.name,
                    "status": "success",
                    "path": str(repo_dir)
                })
            except subprocess.CalledProcessError as e:
                results.append({
                    "name": repo.name,
                    "status": "failed",
                    "error": e.stderr.decode()
                })
        
        return results