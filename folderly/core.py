import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import shutil

#Getting root directory and desktop 
def get_directory(root_dir:Path=Path.home())->Path:
    return root_dir/"Desktop"

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