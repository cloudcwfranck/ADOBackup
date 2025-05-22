from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

class PipelinesModule:
    def __init__(self, org, pat):
        self.client = Connection(
            base_url=f"https://dev.azure.com/{org}",
            creds=BasicAuthentication('', pat)
            ).clients.get_pipelines_client()
    
    def backup(self):
        pipelines = self.client.list_pipelines()
        return [{
            "id": p.id,
            "name": p.name,
            "yaml": self.client.get_pipeline(p.id).configuration
        } for p in pipelines]