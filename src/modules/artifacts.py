import subprocess
import json
from pathlib import Path

class ArtifactsModule:
    def __init__(self, connection):
        self.connection = connection
    
    def backup(self, backup_path):
        artifacts_path = backup_path / "artifacts"
        artifacts_path.mkdir(exist_ok=True)
        
        # Requires Azure CLI installed
        try:
            result = subprocess.run([
                "az", "artifacts", "universal", "list",
                "--org", self.connection.base_url
            ], capture_output=True, text=True)
            
            artifacts = json.loads(result.stdout)
            with open(artifacts_path / "packages.json", "w") as f:
                json.dump(artifacts, f)
            
            return artifacts
        except Exception as e:
            return {"error": str(e)}