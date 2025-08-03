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
try:
    from config import TARGET_FOLDER
except ImportError:
    # Default fallback
    TARGET_FOLDER = "Desktop"

#Getting root directory and target folder 
def get_directory(folder_name: str = None, root_dir: Path = Path.home()) -> Path:
    """
    Get directory path for any root folder (Desktop, Downloads, Documents, etc.)
    
    Args:
        folder_name: Name of the folder (Desktop, Downloads, Documents, etc.)
        root_dir: Root directory (default: user home)
    
    Returns:
        Path to the specified folder
    """
    if folder_name is None:
        folder_name = TARGET_FOLDER
    
    # Handle common folder name variations
    folder_mappings = {
        "documents": ["Documents", "My Documents", "Documenti"],
        "downloads": ["Downloads", "Download"],
        "desktop": ["Desktop"],
        "pictures": ["Pictures", "My Pictures", "Immagini"],
        "music": ["Music", "My Music", "Musica"],
        "videos": ["Videos", "My Videos", "Video"]
    }
    
    # Debug: Print what we're looking for
    print(f"🔍 Looking for folder: '{folder_name}' in {root_dir}")
    
    # Normalize folder name
    folder_lower = folder_name.lower() if folder_name else TARGET_FOLDER.lower()
    
    # Try the exact name first
    exact_path = root_dir / folder_name
    if exact_path.exists():
        return exact_path
    
    # Try common variations
    if folder_lower in folder_mappings:
        for variation in folder_mappings[folder_lower]:
            variation_path = root_dir / variation
            if variation_path.exists():
                return variation_path
    
    # Handle OneDrive paths for Documents, Pictures, etc.
    if folder_lower in ["documents", "pictures", "music", "videos"]:
        # Try OneDrive paths - check multiple possible locations
        onedrive_variations = [
            "OneDrive",
            "OneDrive - Personal", 
            "OneDrive - Personal",
            "OneDrive"
        ]
        
        for onedrive_folder in onedrive_variations:
            onedrive_paths = [
                root_dir / onedrive_folder / folder_name,
                root_dir / onedrive_folder / folder_mappings[folder_lower][0] if folder_lower in folder_mappings else folder_name
            ]
            
            for onedrive_path in onedrive_paths:
                if onedrive_path.exists():
                    return onedrive_path
    
    # If nothing found, return the original path (will be created if needed)
    return root_dir / folder_name

#Getting the list of all the files and folders
def list_directory_items(
    folder_name: str = None,
    extension: str = None,
    file_type: str = None,
    pattern: str = None,
    date_range: tuple = None,
    size_range: tuple = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    include_folders: bool = True,
    include_files: bool = True,
    max_results: int = None
) -> Dict[str, Any]:
    """
    Lists files and folders in the specified root folder with advanced filtering
    
    Args:
        folder_name: Name of the folder (Desktop, Downloads, Documents, etc.)
        extension: Filter by file extension (e.g., "txt", "pdf", "docx")
        file_type: Filter by file type ("documents", "images", "videos", "audio", "archives")
        pattern: Filter by name pattern (case-insensitive substring match)
        date_range: Filter by date range (days_ago, or (start_date, end_date))
        size_range: Filter by file size in bytes (min_size, max_size)
        sort_by: Sort by "name", "modified", "size" (default: "name")
        sort_order: "asc" or "desc" (default: "asc")
        include_folders: Include folders in results (default: True)
        include_files: Include files in results (default: True)
        max_results: Maximum number of results to return
    
    Returns:
        Dict with success status, filtered file list, and filter metadata
    """
    try:
        target_dir = get_directory(folder_name)
        
        # Check if directory exists
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Folder '{folder_name or TARGET_FOLDER}' does not exist at {target_dir}",
                "folder_name": folder_name or TARGET_FOLDER,
                "suggestions": [
                    "Try checking the folder name spelling",
                    "The folder might be in a different location",
                    "Common folder names: Desktop, Downloads, Documents, Pictures, Music, Videos"
                ]
            }
        
        # Check if directory is accessible
        if not target_dir.is_dir():
            return {
                "success": False,
                "error": f"'{target_dir}' is not a directory",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        # Get all items
        all_items = list(target_dir.iterdir())
        results = []
        
        # Apply file/folder filters
        for item in all_items:
            is_file = item.is_file()
            is_folder = item.is_dir()
            
            # Skip if not including files/folders
            if not include_files and is_file:
                continue
            if not include_folders and is_folder:
                continue
            
            # Apply extension filter
            if extension and is_file:
                ext = extension.lower().lstrip('.')
                if item.suffix.lower() != f'.{ext}':
                    continue
            
            # Apply file type filter
            if file_type and is_file:
                file_extensions = {
                    "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
                    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
                    "videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"],
                    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
                    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]
                }
                
                if file_type.lower() in file_extensions:
                    if item.suffix.lower() not in file_extensions[file_type.lower()]:
                        continue
            
            # Apply pattern filter
            if pattern:
                if pattern.lower() not in item.name.lower():
                    continue
            
            # Apply date filter
            if date_range and is_file:
                try:
                    file_time = datetime.fromtimestamp(item.stat().st_mtime)
                    current_time = datetime.now()
                    
                    if isinstance(date_range, (int, float)):
                        # Days ago filter
                        cutoff_date = current_time - timedelta(days=date_range)
                        if file_time < cutoff_date:
                            continue
                    elif isinstance(date_range, tuple) and len(date_range) == 2:
                        # Date range filter
                        start_date, end_date = date_range
                        if isinstance(start_date, str):
                            start_date = datetime.strptime(start_date, "%Y-%m-%d")
                        if isinstance(end_date, str):
                            end_date = datetime.strptime(end_date, "%Y-%m-%d")
                        
                        if file_time < start_date or file_time > end_date:
                            continue
                except Exception:
                    # Skip date filtering if there's an error
                    pass
            
            # Apply size filter
            if size_range and is_file:
                try:
                    file_size = item.stat().st_size
                    min_size, max_size = size_range
                    
                    if min_size and file_size < min_size:
                        continue
                    if max_size and file_size > max_size:
                        continue
                except Exception:
                    # Skip size filtering if there's an error
                    pass
            
            results.append(item)
        
        # Apply sorting
        if sort_by == "name":
            results.sort(key=lambda x: x.name.lower(), reverse=(sort_order == "desc"))
        elif sort_by == "modified":
            results.sort(key=lambda x: x.stat().st_mtime, reverse=(sort_order == "desc"))
        elif sort_by == "size":
            results.sort(key=lambda x: x.stat().st_size if x.is_file() else 0, reverse=(sort_order == "desc"))
        
        # Apply max results limit
        if max_results and len(results) > max_results:
            results = results[:max_results]
        
        # Build filters applied metadata
        filters_applied = {}
        if extension:
            filters_applied["extension"] = extension
        if file_type:
            filters_applied["file_type"] = file_type
        if pattern:
            filters_applied["pattern"] = pattern
        if date_range:
            filters_applied["date_range"] = date_range
        if size_range:
            filters_applied["size_range"] = size_range
        if sort_by:
            filters_applied["sort_by"] = sort_by
        if sort_order:
            filters_applied["sort_order"] = sort_order
        if max_results:
            filters_applied["max_results"] = max_results
        
        return {
            "success": True,
            "results": [str(path) for path in results],
            "total_found": len(results),
            "filters_applied": filters_applied,
            "directory": str(target_dir),
            "folder_name": folder_name or TARGET_FOLDER
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot access folder '{folder_name or TARGET_FOLDER}'",
            "folder_name": folder_name or TARGET_FOLDER,
            "suggestions": ["Try running as administrator or check folder permissions"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name or TARGET_FOLDER
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

def count_files_by_extension(folder_name: str = None) -> Dict[str, Any]:
    """
    Counts files by extension in the specified folder
    
    Args:
        folder_name: Name of the folder (Desktop, Downloads, Documents, etc.)
    
    Returns:
        Dict with extension counts and statistics
    """
    try:
        target_dir = get_directory(folder_name)
        
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Folder '{folder_name or TARGET_FOLDER}' does not exist",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        # Get all files
        all_files = [f for f in target_dir.iterdir() if f.is_file()]
        
        # Count by extension
        extension_counts = {}
        total_files = len(all_files)
        
        for file_path in all_files:
            ext = file_path.suffix.lower()
            if ext:
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
            else:
                # Files without extension
                extension_counts["no_extension"] = extension_counts.get("no_extension", 0) + 1
        
        # Sort by count (descending)
        sorted_extensions = sorted(extension_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "total_files": total_files,
            "extension_counts": dict(sorted_extensions),
            "top_extensions": sorted_extensions[:10],  # Top 10 extensions
            "directory": str(target_dir),
            "folder_name": folder_name or TARGET_FOLDER
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name or TARGET_FOLDER
        }

def get_file_type_statistics(folder_name: str = None) -> Dict[str, Any]:
    """
    Gets file type statistics (documents, images, videos, etc.) for the specified folder
    
    Args:
        folder_name: Name of the folder (Desktop, Downloads, Documents, etc.)
    
    Returns:
        Dict with file type statistics
    """
    try:
        target_dir = get_directory(folder_name)
        
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Folder '{folder_name or TARGET_FOLDER}' does not exist",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        # File type definitions
        file_types = {
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".ppt", ".pptx", ".xls", ".xlsx"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
            "videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm", ".m4v"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
            "executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
            "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".rb", ".go"]
        }
        
        # Get all files
        all_files = [f for f in target_dir.iterdir() if f.is_file()]
        
        # Count by file type
        type_counts = {file_type: 0 for file_type in file_types.keys()}
        type_counts["other"] = 0
        total_files = len(all_files)
        
        for file_path in all_files:
            ext = file_path.suffix.lower()
            categorized = False
            
            for file_type, extensions in file_types.items():
                if ext in extensions:
                    type_counts[file_type] += 1
                    categorized = True
                    break
            
            if not categorized:
                type_counts["other"] += 1
        
        # Remove zero counts and sort
        non_zero_counts = {k: v for k, v in type_counts.items() if v > 0}
        sorted_types = sorted(non_zero_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "total_files": total_files,
            "file_type_counts": dict(sorted_types),
            "top_file_types": sorted_types[:5],  # Top 5 file types
            "directory": str(target_dir),
            "folder_name": folder_name or TARGET_FOLDER
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name or TARGET_FOLDER
        }