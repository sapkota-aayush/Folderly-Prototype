from utils import read_operation_metadata, delete_operation_metadata
from backup import restore_file_or_folder, delete_backup_file_or_folder
import os
from datetime import datetime

def undo_last_operation(expected_type=None):
    """
    Generic undo function for any operation type (move, delete, etc.).
    If expected_type is provided, only undoes if the operation matches.
    """
    metadata = read_operation_metadata()
    if not metadata:
        print("No operation to undo.")
        return
    operation = metadata['current_operation']
    if expected_type and operation['type'] != expected_type:
        print(f"No {expected_type} operation to undo.")
        return
    # Check expiry
    expires_at = datetime.fromisoformat(operation.get('expires_at'))
    if datetime.now() > expires_at:
        print("Undo window has expired. Cannot undo.")
        return
    # Restore each item
    for item in operation['items']:
        restore_file_or_folder(item['backup_path'], item['original_path'])
        # For move, optionally remove from destination
        if operation['type'] == 'move' and os.path.exists(item['destination_path']):
            try:
                if os.path.isdir(item['destination_path']):
                    import shutil
                    shutil.rmtree(item['destination_path'])
                else:
                    os.remove(item['destination_path'])
            except Exception as e:
                print(f"Warning: Could not remove {item['destination_path']}: {e}")
        delete_backup_file_or_folder(item['backup_path'])
    delete_operation_metadata()
    print(f"Undo complete. Files/folders restored to original locations for operation type: {operation['type']}.") 