import questionary
from adobackup.core.storage_manager import StorageManager
from adobackup.core.backup_engine import BackupEngine
from adobackup.core.restore_engine import RestoreEngine
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication


def main():
    print("\U0001F6E1️ Azure DevOps Backup & Restore Tool")

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
    org = questionary.text("Enter source organization name:").ask()
    pat = questionary.password("Enter PAT (Personal Access Token):").ask()

    # Validate auth
    try:
        connection = Connection(
            base_url=f"https://dev.azure.com/{org}",
            creds=BasicAuthentication('', pat)
        )
        core_client = connection.clients.get_core_client()
        projects = list(core_client.get_projects())
        if not projects:
            print("⚠️ Auth succeeded, but no projects found in the org.")
        else:
            print(f"✅ Authenticated successfully. Found {len(projects)} project(s).")
    except Exception as e:
        print(f"❌ Authentication to Azure DevOps failed: {str(e)}")
        return

    # Component selection
    component_options = {
        "1": "Repos",
        "2": "Boards",
        "3": "Pipelines",
        "4": "Test Plans",
        "5": "Artifacts",
        "6": "Wikis"
    }

    print("\nSelect components to back up by typing numbers (e.g., 1,2,4):")
    for num, name in component_options.items():
        print(f"  {num}. {name}")

    selection_raw = questionary.text("Your selection:").ask()
    selected_numbers = [s.strip() for s in selection_raw.split(",") if s.strip() in component_options]
    components = [component_options[n] for n in selected_numbers]

    print(f"\n🧪 Selected component numbers: {selected_numbers}")
    print(f"📦 Components selected: {components}")

    if not components:
        print("❌ No valid components selected. Backup aborted.")
        return

    # Perform backup
    engine = BackupEngine(org, pat)
    results, manifest_path = engine.backup_all(components)

    latest_path = "backups/latest_backup.json"
    engine.save_to_local(results, latest_path)

    if "Azure" in storage_type:
        print("☁️ Uploading to Azure Blob Storage...")
        StorageManager().upload_file_to_blob(latest_path)
        print("✅ Backup uploaded to Azure Blob.")
    else:
        print(f"✅ Backup saved locally at: {manifest_path}")


def run_restore():
    source = questionary.select(
        "Select backup source:",
        choices=["Local Storage", "Azure Blob Storage"]
    ).ask()

    org = questionary.text("Enter target organization name:").ask()
    pat = questionary.password("Enter target PAT:").ask()

    engine = RestoreEngine(org, pat)
    engine.restore_all(source)


if __name__ == "__main__":
    main()
