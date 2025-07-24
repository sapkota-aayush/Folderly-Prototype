import threading
from datetime import datetime

def auto_expiry_cleanup(expires_at, operation_items, delete_metadata_func, delete_backup_func):
    """
    Waits until expiry, then deletes backups and metadata.
    - expires_at: datetime object for expiry
    - operation_items: list of items with 'backup_path'
    - delete_metadata_func: function to delete operation metadata
    - delete_backup_func: function to delete a backup file/folder
    """
    now = datetime.now()
    wait_seconds = (expires_at - now).total_seconds()
    if wait_seconds > 0:
        threading.Event().wait(wait_seconds)
    for item in operation_items:
        delete_backup_func(item['backup_path'])
    delete_metadata_func()
    print("Undo window expired. Backups and metadata cleaned up.") 