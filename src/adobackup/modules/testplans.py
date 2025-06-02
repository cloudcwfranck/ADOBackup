from azure.devops.v7_1.test import TestClient
import json

class TestPlansModule:
    def __init__(self, connection):
        self.client = connection.clients.get_test_client()
    
    def backup(self, backup_path):
        test_path = backup_path / "test_plans"
        test_path.mkdir(exist_ok=True)
        
        plans = self.client.get_plans()
        results = []
        
        for plan in plans:
            plan_data = {
                "plan": plan.__dict__,
                "suites": self._get_test_suites(plan.id),
                "cases": self._get_test_cases(plan.id)
            }
            with open(test_path / f"plan_{plan.id}.json", "w") as f:
                json.dump(plan_data, f, default=lambda x: x.__dict__)
            results.append({
                "plan_id": plan.id,
                "name": plan.name,
                "suites": len(plan_data["suites"]),
                "cases": len(plan_data["cases"])
            })
        
        return results
    
    def _get_test_suites(self, plan_id):
        return self.client.get_test_suites_for_plan(plan_id)
    
    def _get_test_cases(self, plan_id):
        return self.client.get_test_cases(plan_id)