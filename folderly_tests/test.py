import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core import (
    list_directory_items,
    filter_and_sort_by_modified,
    filter_exclude,
    select_items_by_indices,
    find_duplicates_by_name,
    # If you have find_similar_name_duplicates, import it too
)

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