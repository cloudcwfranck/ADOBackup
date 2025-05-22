class TestPlansModule:
    def __init__(self, org, pat):
        self.client = Connection(...).clients.get_test_plan_client()
    
    def backup(self):
        plans = self.client.get_test_plans()
        return [{
            "id": p.id,
            "suites": self._backup_suites(p.id)
        } for p in plans]