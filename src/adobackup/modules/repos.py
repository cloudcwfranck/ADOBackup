import subprocess
from pathlib import Path
from azure.devops.v7_1.git import GitClient
import json

class ReposModule:
    def __init__(self, connection):
        self.client = connection.clients.get_git_client()
    
    def backup(self, backup_path):
        repos_backup = backup_path / "repos"
        repos_backup.mkdir(exist_ok=True)
        
        results = []
        repos = self.client.get_repositories()
        
        for repo in repos:
            repo_dir = repos_backup / f"{repo.name}.git"
            try:
                subprocess.run([
                    "git", "clone", "--mirror",
                    repo.remote_url,
                    str(repo_dir)
                ], check=True, capture_output=True)
                results.append({
                    "name": repo.name,
                    "status": "success",
                    "path": str(repo_dir.relative_to(backup_path))
                })
            except subprocess.CalledProcessError as e:
                results.append({
                    "name": repo.name,
                    "status": "failed",
                    "error": e.stderr.decode()
                })
        
        with open(repos_backup / "metadata.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results