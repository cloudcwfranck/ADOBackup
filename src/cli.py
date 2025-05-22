import questionary
from core.backup_engine import BackupEngine
from core.restore_engine import RestoreEngine

def main():
    print("🛡️ Azure DevOps Backup & Restore Tool")
    
    action = questionary.select(
        "Select operation:",
        choices=[
            "Backup to Local Storage",
            "Backup to Azure Blob Storage",
            "Restore from Backup"
        ]).ask()

    if "Backup" in action:
        run_backup(action)
    else:
        run_restore()

def run_backup(storage_type):
    from core.storage_manager import StorageManager
    
    org = questionary.text("Enter source organization name:").ask()
    pat = questionary.password("Enter PAT (Personal Access Token):").ask()
    
    components = questionary.checkbox(
        "Select components to backup:",
        choices=["Repos", "Boards", "Pipelines", "Test Plans", "Artifacts", "Wikis"]
    ).ask()

    engine = BackupEngine(org, pat)
    results = engine.backup_all(components)

    if "Azure" in storage_type:
        StorageManager().upload_to_blob(results)
    else:
        StorageManager().save_locally(results)

def run_restore():
    source = questionary.select(
        "Select backup source:",
        choices=["Local Storage", "Azure Blob Storage"]
    ).ask()
    
    org = questionary.text("Enter target organization name:").ask()
    pat = questionary.password("Enter target PAT:").ask()

    RestoreEngine(org, pat).restore_all(source)

if __name__ == "__main__":
    main()