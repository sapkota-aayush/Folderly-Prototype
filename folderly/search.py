from pathlib import Path
from typing import List

def filter_by_name(items: List[Path], name_substring: str) -> List[Path]:
    """
    Returns items whose name contains the given substring (case-insensitive).
    Args:
        items (List[Path]): List of Path objects to filter.
        name_substring (str): Substring to search for in the item names.
    Returns:
        List[Path]: Filtered list of Path objects.
    """
    norm_sub = name_substring.lower().strip()
    return [item for item in items if norm_sub in item.name.lower()]

if __name__ == "__main__":
    from .core import list_directory_items
    all_items = list_directory_items()
    search_term = input("Enter a file or folder name (or part of it) to search for: ").strip()
    if search_term:
        matches = filter_by_name(all_items, search_term)
        if matches:
            print("\nFound the following matches:")
            for match in matches:
                print(match)
        else:
            print("No files or folders found matching your search.")
    else:
        print("No search term entered.") 