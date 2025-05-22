class RestoreEngine:
    def __init__(self, target_org, target_pat):
        self.target_org = target_org
        self.target_pat = target_pat

    def restore_all(self, backup_source):
        if backup_source == "Local Storage":
            data = self._load_local_backup()
        else:
            data = self._download_from_blob()
        
        self._restore_repos(data["repos"])
        self._restore_boards(data["boards"])
        # Add other components

    def _restore_repos(self, repos):
        for repo in repos:
            subprocess.run([
                "git", "push", "--mirror",
                f"https://{self.target_pat}@dev.azure.com/{self.target_org}/_git/{repo['name']}"
            ], cwd=repo["local_path"])