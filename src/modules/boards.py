class BoardsModule:
    def __init__(self, connection):
        self.wit_client = connection.clients.get_work_item_tracking_client()
        
    def backup(self):
        print("📋 Backing up Boards...")
        return {
            "work_items": self._backup_work_items(),
            "queries": self._backup_queries(),
            "board_states": self._backup_board_states()
        }
        
    def _backup_work_items(self):
        return [wi.as_dict() for wi in 
                self.wit_client.query_by_wiql("SELECT * FROM workitems").work_items]
                
    def _backup_queries(self):
        return self.wit_client.get_queries().as_dict()
        
    def _backup_board_states(self):
        # Implementation for board columns/configurations
        pass