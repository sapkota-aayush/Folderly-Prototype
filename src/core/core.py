import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import shutil
from send2trash import send2trash
from ..utils.utils import write_operation_metadata, read_operation_metadata, delete_operation_metadata
from ..utils.backup import backup_file_or_folder, delete_backup_file_or_folder
import threading
from ..utils.undo_expiry import auto_expiry_cleanup

# ============================================================================
# CONFIGURABLE TARGET DIRECTORY
# ============================================================================
# Change this to any folder you want to manage
# Examples: "Desktop", "Documents", "Downloads", "Pictures", "Work", "Projects"
TARGET_FOLDER = "Desktop"  # Easy to change!

#Getting root directory and target folder 
def get_directory(root_dir:Path=Path.home())->Path:
    return root_dir/TARGET_FOLDER

#Getting the list of all the files and folders
def list_directory_items()->Dict[str, Any]:
    try:
        desktop_dir = get_directory()
        results = list(desktop_dir.iterdir())
        
        return {
            "success": True,
            "results": [str(path) for path in results],  # Convert to strings
            "total_found": len(results),
            "directory": str(desktop_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

#Listing recently modified files and folders
def filter_and_sort_by_modified(items: List[Path], days: int) -> Dict[str, Any]:
    try:
        cutoff = datetime.now() - timedelta(days=days)
        filtered = [p for p in items if datetime.fromtimestamp(p.stat().st_mtime) >= cutoff]
        sorted_items = sorted(filtered, key=lambda p: p.stat().st_mtime, reverse=True)
        
        return {
            "success": True,
            "results": [str(path) for path in sorted_items],  # Convert to strings
            "total_found": len(sorted_items),
            "days_threshold": days
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

#Creating a directory 
def create_directory(target_dir: Path) -> Dict[str, Any]:
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "results": str(target_dir),
            "directory_created": str(target_dir),
            "already_existed": target_dir.exists()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def move_items_to_directory(items: list[Path], destination_dir: Path) -> Dict[str, Any]:
    try:
        moved_items = []
        skipped_items = []
        
        for item in items:
            # Skip hidden files/folders
            if item.name.startswith('.'):
                skipped_items.append({"item": str(item), "reason": "hidden file"})
                continue
                
            # Skip if file is in use (try to check)
            try:
                dest = destination_dir / item.name
                shutil.move(str(item), str(dest))
                moved_items.append(str(dest))
            except PermissionError:
                skipped_items.append({"item": str(item), "reason": "file in use"})
            except Exception as e:
                skipped_items.append({"item": str(item), "reason": str(e)})
        
        return {
            "success": True,
            "results": moved_items,
            "total_moved": len(moved_items),
            "skipped_items": skipped_items,
            "destination": str(destination_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def create_numbered_files(base_name: str, count: int, extension: str, start_number: int = 1, target_dir: Path = None) -> Dict[str, Any]:
    """
    Creates multiple numbered files with specified extension.
    
    Args:
        base_name: Base name for files (e.g., "file", "test")
        count: Number of files to create
        extension: File extension (e.g., "txt", "py", "js")
        start_number: Starting number (default: 1)
        target_dir: Directory to create files in (default: Desktop)
    
    Returns:
        Dict with success status and created files info
    """
    try:
        if target_dir is None:
            target_dir = get_directory()
        
        created_files = []
        failed_files = []
        
        for i in range(start_number, start_number + count):
            try:
                # Create filename
                filename = f"{base_name}_{i}.{extension}"
                file_path = target_dir / filename
                
                # Create file with basic content
                content = f"This is {base_name} number {i}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                created_files.append({
                    "filename": filename,
                    "path": str(file_path),
                    "content_length": len(content)
                })
                
            except Exception as e:
                failed_files.append({
                    "filename": f"{base_name}_{i}.{extension}",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "created_files": created_files,
            "failed_files": failed_files,
            "total_created": len(created_files),
            "total_failed": len(failed_files),
            "target_directory": str(target_dir)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def delete_single_item(item_path: str, enable_undo: bool = True) -> Dict[str, Any]:
    """
    Soft deletes a single file or directory using send2trash with optional undo support.
    
    Args:
        item_path: Path to the file or directory to delete
        enable_undo: Whether to enable undo support (default: True)
        
    Returns:
        Dict with success status and deletion info
    """
    try:
        path = Path(item_path)
        
        # Check if item exists
        if not path.exists():
            return {
                "success": False,
                "error": f"Item does not exist: {item_path}",
                "item_path": item_path
            }
        
        # Check if item is accessible
        if not path.is_file() and not path.is_dir():
            return {
                "success": False,
                "error": f"Item is not a file or directory: {item_path}",
                "item_path": item_path
            }
        
        # If undo is enabled, create backup and metadata
        if enable_undo:
            # Clear any existing undo operation
            metadata = read_operation_metadata()
            if metadata:
                for item in metadata['current_operation'].get('items', []):
                    delete_backup_file_or_folder(item['backup_path'])
                delete_operation_metadata()
            
            # Create backup
            backup_path = backup_file_or_folder(str(path))
            
            # Prepare operation metadata
            expires_at = datetime.now() + timedelta(seconds=30)
            operation_data = {
                'session_id': 'folderly_delete_session',
                'current_operation': {
                    'id': f'delete_op_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'type': 'delete',
                    'timestamp': datetime.now().isoformat(),
                    'expires_at': expires_at.isoformat(),
                    'status': 'active',
                    'items': [{
                        'original_path': str(path),
                        'backup_path': backup_path,
                        'item_type': 'file' if path.is_file() else 'directory'
                    }]
                }
            }
            write_operation_metadata(operation_data)
            
            # Start expiry timer
            threading.Thread(
                target=auto_expiry_cleanup,
                args=(expires_at, operation_data['current_operation']['items'], delete_operation_metadata, delete_backup_file_or_folder),
                daemon=True
            ).start()
        
        # Soft delete using send2trash
        send2trash(str(path))
        
        return {
            "success": True,
            "deleted_item": item_path,
            "item_type": "file" if path.is_file() else "directory",
            "deletion_method": "soft_delete",
            "trash_location": "system_recycle_bin",
            "undo_available": enable_undo,
            "undo_expires_in": 30 if enable_undo else 0
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot delete {item_path}",
            "item_path": item_path,
            "reason": "file_in_use_or_protected"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "item_path": item_path
        }

def delete_multiple_items(item_paths: List[str], enable_undo: bool = True) -> Dict[str, Any]:
    """
    Soft deletes multiple files and directories using send2trash with undo support.
    
    Args:
        item_paths: List of paths to files or directories to delete
        enable_undo: Whether to enable undo support (default: True)
        
    Returns:
        Dict with success status and deletion info for all items
    """
    try:
        # If undo is enabled, create backup and metadata for all items
        if enable_undo:
            # Clear any existing undo operation
            metadata = read_operation_metadata()
            if metadata:
                for item in metadata['current_operation'].get('items', []):
                    delete_backup_file_or_folder(item['backup_path'])
                delete_operation_metadata()
            
            # Create backups for all items
            operation_items = []
            for item_path in item_paths:
                path = Path(item_path)
                if path.exists():
                    backup_path = backup_file_or_folder(str(path))
                    operation_items.append({
                        'original_path': str(path),
                        'backup_path': backup_path,
                        'item_type': 'file' if path.is_file() else 'directory'
                    })
            
            # Prepare operation metadata
            expires_at = datetime.now() + timedelta(seconds=30)
            operation_data = {
                'session_id': 'folderly_delete_session',
                'current_operation': {
                    'id': f'delete_op_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'type': 'delete',
                    'timestamp': datetime.now().isoformat(),
                    'expires_at': expires_at.isoformat(),
                    'status': 'active',
                    'items': operation_items
                }
            }
            write_operation_metadata(operation_data)
            
            # Start expiry timer
            threading.Thread(
                target=auto_expiry_cleanup,
                args=(expires_at, operation_items, delete_operation_metadata, delete_backup_file_or_folder),
                daemon=True
            ).start()
        
        deleted_items = []
        failed_items = []
        
        for item_path in item_paths:
            result = delete_single_item(item_path, enable_undo=False)  # Don't create individual undo for each item
            
            if result["success"]:
                deleted_items.append({
                    "path": item_path,
                    "type": result.get("item_type", "unknown"),
                    "deletion_method": "soft_delete"
                })
            else:
                failed_items.append({
                    "path": item_path,
                    "error": result.get("error", "Unknown error"),
                    "reason": result.get("reason", "unknown")
                })
        
        return {
            "success": True,
            "deleted_items": deleted_items,
            "failed_items": failed_items,
            "total_deleted": len(deleted_items),
            "total_failed": len(failed_items),
            "deletion_method": "soft_delete",
            "trash_location": "system_recycle_bin",
            "undo_available": enable_undo,
            "undo_expires_in": 30 if enable_undo else 0
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_items": len(item_paths)
        }

def delete_items_by_pattern(pattern: str, target_dir: str = None, enable_undo: bool = True) -> Dict[str, Any]:
    """
    Deletes files and directories matching a pattern using soft delete with undo support.
    
    Args:
        pattern: Glob pattern to match (e.g., "*.txt", "test*", "*temp*")
        target_dir: Directory to search in (default: Desktop)
        enable_undo: Whether to enable undo support (default: True)
        
    Returns:
        Dict with success status and deletion info
    """
    try:
        if target_dir is None:
            target_dir = str(get_directory())
        
        search_dir = Path(target_dir)
        
        if not search_dir.exists():
            return {
                "success": False,
                "error": f"Target directory does not exist: {target_dir}",
                "target_dir": target_dir
            }
        
        # Find all items matching the pattern
        matching_items = list(search_dir.glob(pattern))
        
        if not matching_items:
            return {
                "success": True,
                "message": f"No items found matching pattern: {pattern}",
                "pattern": pattern,
                "target_dir": target_dir,
                "total_found": 0
            }
        
        # Convert to string paths for deletion
        item_paths = [str(item) for item in matching_items]
        
        # Use the multiple delete function
        result = delete_multiple_items(item_paths, enable_undo)
        result["pattern"] = pattern
        result["target_dir"] = target_dir
        result["total_found"] = len(matching_items)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "pattern": pattern,
            "target_dir": target_dir
        }

def list_nested_folders_tree(target_dir: str = None, max_depth: int = 3) -> Dict[str, Any]:
    """
    Lists all nested folders in a tree structure format.
    
    Args:
        target_dir: Directory to search in (default: Desktop)
        max_depth: Maximum depth to traverse (default: 3)
        
    Returns:
        Dict with success status and tree structure
    """
    try:
        if target_dir is None:
            target_dir = str(get_directory())
        
        search_dir = Path(target_dir)
        
        if not search_dir.exists():
            return {
                "success": False,
                "error": f"Target directory does not exist: {target_dir}",
                "target_dir": target_dir
            }
        
        def build_tree(path: Path, depth: int = 0, is_last: bool = False, prefix: str = "") -> str:
            """Recursively build tree structure string"""
            if depth > max_depth:
                return ""
            
            # Get all items in current directory
            try:
                items = sorted([item for item in path.iterdir() if item.is_dir()], key=lambda x: x.name.lower())
            except PermissionError:
                return f"{prefix}└── [Access Denied]\n"
            
            if not items:
                return ""
            
            tree_lines = []
            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                connector = "└──" if is_last_item else "├──"
                line_prefix = "    " if is_last else "│   "
                
                # Current item line
                tree_lines.append(f"{prefix}{connector} {item.name}/")
                
                # Recursively add children
                child_prefix = prefix + line_prefix
                child_tree = build_tree(item, depth + 1, is_last_item, child_prefix)
                if child_tree:
                    tree_lines.append(child_tree)
            
            return "\n".join(tree_lines)
        
        # Build the tree structure
        tree_structure = build_tree(search_dir)
        
        if not tree_structure:
            return {
                "success": True,
                "message": f"No folders found in {target_dir}",
                "target_dir": target_dir,
                "tree_structure": f"{search_dir.name}/\n",
                "total_folders": 0
            }
        
        # Add root directory name
        full_tree = f"{search_dir.name}/\n{tree_structure}"
        
        # Count total folders
        folder_count = len([line for line in full_tree.split('\n') if line.strip().endswith('/')])
        
        return {
            "success": True,
            "target_dir": target_dir,
            "tree_structure": full_tree,
            "total_folders": folder_count,
            "max_depth": max_depth
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "target_dir": target_dir
        }