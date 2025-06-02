class BackupError(Exception):
    """Base exception for backup operations"""
    pass

class StorageError(BackupError):
    """Storage-related errors"""
    pass

class DevOpsError(BackupError):
    """Azure DevOps API errors"""
    pass