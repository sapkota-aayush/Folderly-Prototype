#!/usr/bin/env python3
"""
Folderly CLI - Desktop Organization Tool
"""

import argparse
import sys
from pathlib import Path
from typing import List

# Import Folderly modules
from src.core.core import (
    get_directory, list_directory_items, filter_and_sort_by_modified,
    create_directory, move_items_to_directory
)
from src.core.search import filter_by_name
from src.utils.move_manager import perform_move_with_undo
from src.utils.undo_manager import undo_last_operation
from src.ai.function_schemas import get_function_schemas


def list_desktop_items():
    """List all items on Desktop"""
    items = list_directory_items()
    print(f"\n📁 Desktop Items ({len(items)} total):")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item.name}")
    return items


def show_recent_items(days: int = 7):
    """Show recently modified items"""
    items = list_directory_items()
    recent = filter_and_sort_by_modified(items, days)
    print(f"\n🕒 Recently Modified Items (last {days} days):")
    for i, item in enumerate(recent, 1):
        print(f"  {i}. {item.name}")
    return recent


def find_duplicates():
    """Find duplicate files/folders"""
    print("\n🔍 Duplicate detection not implemented yet.")
    print("This feature will be added in a future update.")
    return {}, {}


def search_items(query: str):
    """Search for items by name"""
    items = list_directory_items()
    matches = filter_by_name(items, query)
    
    if matches:
        print(f"\n🔍 Search Results for '{query}':")
        for i, item in enumerate(matches, 1):
            print(f"  {i}. {item.name}")
    else:
        print(f"\n❌ No items found matching '{query}'")
    
    return matches


def move_items_interactive():
    """Interactive move operation with undo support"""
    items = list_directory_items()
    
    print("\n📁 Select items to move:")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item.name}")
    
    try:
        selection = input("\nEnter item numbers (comma-separated): ").strip()
        if not selection:
            print("No items selected.")
            return
        
        indices = [int(x.strip()) for x in selection.split(',') if x.strip().isdigit()]
        selected_items = [items[i-1] for i in indices if 1 <= i <= len(items)]
        
        if not selected_items:
            print("No valid items selected.")
            return
        
        destination = input("Enter destination directory path: ").strip()
        if not destination:
            print("No destination specified.")
            return
        
        # Perform move with undo
        perform_move_with_undo(
            [str(item) for item in selected_items],
            destination
        )
        
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def undo_operation():
    """Undo the last operation"""
    try:
        undo_last_operation()
        print("✅ Last operation undone successfully!")
    except Exception as e:
        print(f"❌ Error undoing operation: {e}")


def show_help():
    """Show help information"""
    print("""
📁 Folderly - Desktop Organization Tool

Available Commands:
  list              - List all Desktop items
  recent [days]     - Show recently modified items (default: 7 days)
  duplicates        - Find duplicate files/folders
  search <query>    - Search for items by name
  move              - Interactive move operation with undo
  undo              - Undo last operation
  help              - Show this help message

Examples:
  python cli.py list
  python cli.py recent 14
  python cli.py search "document"
  python cli.py duplicates
  python cli.py move
  python cli.py undo
    """)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Folderly - Desktop Organization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py list
  python cli.py recent 14
  python cli.py search "document"
  python cli.py duplicates
  python cli.py move
  python cli.py undo
        """
    )
    
    parser.add_argument('command', nargs='?', default='help',
                       choices=['list', 'recent', 'duplicates', 'search', 'move', 'undo', 'help'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Additional arguments for the command')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'list':
            list_desktop_items()
        elif args.command == 'recent':
            days = int(args.args[0]) if args.args else 7
            show_recent_items(days)
        elif args.command == 'duplicates':
            find_duplicates()
        elif args.command == 'search':
            if not args.args:
                print("❌ Please provide a search query.")
                print("Example: python cli.py search 'document'")
                return
            search_items(args.args[0])
        elif args.command == 'move':
            move_items_interactive()
        elif args.command == 'undo':
            undo_operation()
        elif args.command == 'help':
            show_help()
        else:
            show_help()
            
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

