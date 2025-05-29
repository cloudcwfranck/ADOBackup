from azure.devops.v6_0.pipelines import PipelinesClient
import json

class PipelinesModule:
    def __init__(self, connection):
        self.client = connection.clients.get_pipelines_client()
    
    def backup(self, backup_path):
        pipelines_path = backup_path / "pipelines"
        pipelines_path.mkdir(exist_ok=True)
        
        pipelines = self.client.list_pipelines()
        results = []
        
        for pipeline in pipelines:
            try:
                config = self.client.get_pipeline(pipeline.id)
                with open(pipelines_path / f"{pipeline.id}.json", "w") as f:
                    json.dump(config.__dict__, f)
                results.append({
                    "id": pipeline.id,
                    "name": pipeline.name,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "id": pipeline.id,
                    "name": pipeline.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        with open(pipelines_path / "summary.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results