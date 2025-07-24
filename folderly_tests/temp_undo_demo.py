"""
This script demonstrates and tests temp-folder undo logic for Folderly.
It is safe to experiment here without affecting core or search modules.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from move_manager import perform_move_with_undo
from undo_manager import undo_last_operation

def main():
    print("--- Folderly Move with Undo Demo ---")
    source_folder = input("Enter the full path of the folder to move: ").strip()
    if not os.path.isdir(source_folder):
        print("Invalid source folder.")
        return
    dest_dir = input("Enter the full path to the destination directory: ").strip()
    if not os.path.isdir(dest_dir):
        print("Invalid destination directory.")
        return
    print(f"Moving folder {source_folder} to {dest_dir}...")
    perform_move_with_undo([source_folder], dest_dir)
    print("Done. Undo is available for 30 seconds.")
    undo_prompt = input("Would you like to undo the last move operation? (y/n): ").strip().lower()
    if undo_prompt == 'y':
        undo_last_operation(expected_type='move')

if __name__ == "__main__":
    main()
