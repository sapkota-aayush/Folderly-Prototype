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