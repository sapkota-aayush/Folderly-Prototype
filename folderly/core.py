import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import shutil

#Getting root directory and desktop 
def get_directory(root_dir:Path=Path.home())->Path:
    return root_dir/"Desktop"

#Getting the list of all the files and folders
def list_directory_items()->list[Path]:
    desktop_dir=get_directory()
    return list(desktop_dir.iterdir())

#Listing frequently used files and folders
def filter_and_sort_by_modified(items: List[Path], days: int) -> List[Path]:
    cutoff = datetime.now() - timedelta(days=days)
    filtered = [p for p in items if datetime.fromtimestamp(p.stat().st_mtime) >= cutoff]
    sorted_items = sorted(filtered, key=lambda p: p.stat().st_mtime, reverse=True)
    return sorted_items

def filter_by_extension(items:list[Path],extensions:list[str],exclude:set[Path]=None)->list[Path]:
    exclude=exclude or set()
    return[p for p in items if p.suffix.lower() in extensions and p not in exclude]

def filter_exclude(items: list[Path], exclude: list[Path]) -> list[Path]:
    """
    Returns items from the input list that are not in the exclude list.
    Args:
        items (list[Path]): List of Path objects to filter.
        exclude (list[Path]): List of Path objects to exclude from the result.
    Returns:
        list[Path]: Filtered list of Path objects.
    """
    exclude_set = set(exclude)
    return [p for p in items if p not in exclude_set]


def find_duplicates_by_name(items: list[Path]) -> dict[str, list[Path]]:
    """
    Returns a dictionary where keys are duplicate file/folder names and values are lists of Path objects with that name.
    Args:
        items (list[Path]): List of Path objects to check for duplicates.
    Returns:
        dict[str, list[Path]]: Dictionary of duplicate names to lists of Path objects.
    """
    from collections import defaultdict 
    name_map = defaultdict(list)
    for p in items:
        name_map[p.name.lower()].append(p)
    return {name: paths for name, paths in name_map.items() if len(paths) > 1}

def strip_trailing_number(name: str) -> str:
    # Removes trailing digits and spaces, e.g., "gcp bootcamp1" -> "gcp bootcamp"
    return re.sub(r'\d+$', '', name).strip().lower()

def find_similar_name_duplicates(items: List[Path]) -> Dict[str, List[Path]]:
    name_map = defaultdict(list)
    for p in items:
        base_name = strip_trailing_number(p.stem)  # Use .stem to ignore extension
        name_map[base_name].append(p)
    return {name: paths for name, paths in name_map.items() if len(paths) > 1}

def select_items_by_indices(items: list[Path], indices: list[int]) -> list[Path]:
    """
    Returns the items at the given 1-based indices from the items list.
    Args:
        items (list[Path]): List of Path objects.
        indices (list[int]): List of 1-based indices selected by the user.
    Returns:
        list[Path]: The selected Path objects.
    """
    return [item for idx, item in enumerate(items, 1) if idx in indices]

def prompt_and_filter_user_keep(items: list[Path]) -> list[Path]:
    """
    Prompts the user to select items to keep (by number) and returns the filtered list excluding those items.
    Args:
        items (list[Path]): List of Path objects to present to the user.
    Returns:
        list[Path]: Filtered list of Path objects not selected by the user.
    """
    for idx, item in enumerate(items, 1):
        print(f"{idx}. {item}")
    to_keep_input = input("\nEnter the numbers of items you want to keep on your Desktop (comma-separated), or press Enter to skip: ")
    if to_keep_input.strip():
        keep_indices = [int(num.strip()) for num in to_keep_input.split(',') if num.strip().isdigit()]
        user_keep = select_items_by_indices(items, keep_indices)
    else:
        user_keep = []
    return filter_exclude(items, user_keep)



#Creating a directory 
def create_directory(target_dir:Path)->Path:
    target_dir.mkdir(parents=True,exist_ok=True)
    return target_dir

def move_items_to_directory(items:list[Path],destination_dir:Path):
    for item in items:
        dest=destination_dir/item.name
        shutil.move(str(item),str(dest))