import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import platform
import subprocess

from core import (
    list_directory_items,
    filter_and_sort_by_modified,
    filter_exclude,
    select_items_by_indices,
    find_duplicates_by_name,
    # If you have find_similar_name_duplicates, import it too
    filter_by_name,
)

def normalize(s):
    return ''.join(s.lower().split())

if __name__ == "__main__":
    all_items = list_directory_items()
    days = int(input("Consider files/folders modified in the last how many days as 'most used'? "))
    top_n = int(input("How many top items do you want to keep as 'most used'? "))

    most_used = filter_and_sort_by_modified(all_items, days=days)[:top_n]
    least_used = filter_exclude(all_items, most_used)

    print(f"\nMost used items (top {top_n} from last {days} days):")
    for item in most_used:
        print(item)

    print(f"\nLeast used items (not in top {top_n} most used from last {days} days):")
    for idx, item in enumerate(least_used, 1):
        print(f"{idx}. {item}")

    # Prompt user for numbers to keep
    to_keep_input = input("\nEnter the numbers of items you want to keep on your Desktop (comma-separated), or press Enter to skip: ")
    if to_keep_input.strip():
        keep_indices = [int(num.strip()) for num in to_keep_input.split(',') if num.strip().isdigit()]
        user_keep = select_items_by_indices(least_used, keep_indices)
    else:
        user_keep = []

    # Exclude user_keep from further cleanup
    final_candidates = filter_exclude(least_used, user_keep)

    print("\nFinal candidates for cleanup (after user exclusions):")
    for item in final_candidates:
        print(item)

    # Show duplicates by name for all items
    print("\nDuplicates by name (across all Desktop items):")
    duplicates = find_duplicates_by_name(all_items)
    for name, paths in duplicates.items():
        print(f"Duplicate name: {name}")
        for p in paths:
            print(f"  {p}")

    # If you have similar name duplicates, you can add:
    # from core import find_similar_name_duplicates
    # similar_duplicates = find_similar_name_duplicates(all_items)
    # if similar_duplicates:
    #     print("\nSimilar name duplicates (ignoring trailing numbers):")
    #     for name, paths in similar_duplicates.items():
    #         print(f"Duplicate group: {name}")
    #         for p in paths:
    #             print(f"  {p}")
    # else:
    #     print("\nNo similar name duplicates found.")

    # --- Test: Open file/folder in system file explorer ---
    search_name = input("\nEnter the name of a file or folder to search on your Desktop (or press Enter to skip): ").strip()
    if search_name:
        norm_search = normalize(search_name)
        matches = [item for item in all_items if norm_search in normalize(item.name)]
        if matches:
            print("Found:")
            for idx, match in enumerate(matches, 1):
                print(f"{idx}. {match}")
            open_choice = input("Enter the number to open in File Explorer, or press Enter to skip: ").strip()
            if open_choice.isdigit():
                idx = int(open_choice)
                if 1 <= idx <= len(matches):
                    path = matches[idx - 1]
                    if platform.system() == 'Windows':
                        os.startfile(str(path))
                    elif platform.system() == 'Darwin':
                        subprocess.run(['open', str(path)])
                    else:
                        subprocess.run(['xdg-open', str(path)])
                    print("Opened in file explorer.")
                else:
                    print("Invalid number.")
            else:
                print("Skipped opening.")
        else:
            print("No file or folder found with that name on your Desktop.")

    # Quick test for filter_by_name
    search_term = input("\nEnter a file or folder name (or part of it) to search for: ").strip()
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