import os
import json
import openai
import threading
import time
from dotenv import load_dotenv
from src.ai.function_schemas import get_function_schemas
from src.core.core import list_directory_items, filter_and_sort_by_modified, create_directory, move_items_to_directory, delete_single_item, delete_multiple_items, delete_items_by_pattern, create_numbered_files, list_nested_folders_tree
from folderly.activity_tracker import start_activity_monitoring, FolderlyActivityTracker, show_activity_summary
from folderly.ai_activity_integration import show_ai_enhanced_activity
from src.utils.move_manager import perform_move_with_undo
from src.utils.undo_manager import undo_last_operation
from pathlib import Path

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in environment variables!")
    print("Please add your API key to the .env file:")
    print("OPENAI_API_KEY=your_api_key_here")
    exit(1)

print(f"API Key loaded: {'Yes' if api_key else 'No'}")

# Configure OpenAI client
client = openai.OpenAI(api_key=api_key)

# Global variables for background monitoring
background_tracker = None
background_observer = None
monitoring_thread = None

def start_background_monitoring():
    """Start background activity monitoring"""
    global background_tracker, background_observer
    
    if background_tracker is None:
        try:
            background_tracker, background_observer = start_activity_monitoring()
        except Exception as e:
            pass  # Silent fail for background monitoring

def stop_background_monitoring():
    """Stop background activity monitoring"""
    global background_observer
    
    if background_observer:
        try:
            background_observer.stop()
            background_observer.join()
        except Exception as e:
            pass  # Silent fail for background monitoring

def show_activity_with_ai():
    """Show user's recent activity with AI analysis"""
    try:
        tracker = FolderlyActivityTracker()
        result = show_ai_enhanced_activity(tracker)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Could not analyze activity: {str(e)}"
        }

def create_system_prompt():
    return """You are Folderly, a smart file management assistant. You can help users explore their desktop.

IMPORTANT: When users ask you to create files or folders, ALWAYS use the appropriate function instead of just responding conversationally.

AVAILABLE FUNCTIONS:
- list_directory_items: Show all files and folders on desktop
- list_nested_folders_tree: Show nested folders in tree structure format
- filter_and_sort_by_modified: Show recently modified files/folders
- create_directory: Create a new folder on desktop
- create_multiple_directories: Create multiple folders at once
- create_file: Create a new file with content and extension
- create_multiple_files: Create multiple files with different extensions
- perform_move_with_undo: Move files and folders to a destination with undo support
- undo_last_operation: Undo the last move or delete operation if within 30 seconds
- delete_single_item: Soft delete a single file or directory (moves to recycle bin) with undo support
- delete_multiple_items: Soft delete multiple files and directories (moves to recycle bin) with undo support
- delete_items_by_pattern: Delete files matching a pattern (moves to recycle bin) with undo support
- show_activity_with_ai: Show user's recent file activity with AI analysis and insights

WHEN TO USE FUNCTIONS:
- If user asks to create files → Use create_file or create_multiple_files
- If user asks to create folders → Use create_directory or create_multiple_directories
- If user asks to move files → Use perform_move_with_undo
- If user asks to undo → Use undo_last_operation (works for both move and delete operations)
- If user asks to list files → Use list_directory_items
- If user asks to show folder structure/tree → Use list_nested_folders_tree
- If user asks to delete files → Use delete_single_item, delete_multiple_items, or delete_items_by_pattern
- If user asks to delete files by pattern (e.g., "all txt files", "temp files") → Use delete_items_by_pattern
- If user asks to delete specific files → Use delete_single_item or delete_multiple_items

TREE STRUCTURE FORMATTING:
When displaying file/folder structures, ALWAYS use tree format with these characters:
- ├── for items that have siblings below
- └── for the last item in a level  
- │   for vertical lines showing hierarchy
- Use proper indentation (4 spaces per level)

When users ask to create multiple folders or a folder structure, ALWAYS preview the structure first like:
"📁 I'll create this folder structure for you:
Documents/
   ├── Education/
   │      ├── Program_Name/
   │      └── Certificates/
   ├── Work/
   │      ├── Project_Name/
   │      └── Reports/
   └── Personal/
          ├── Finance/
          └── ID/

Would you like me to create this structure?"

RESPONSE PATTERNS:
- For listing: Display as tree structure like:
  Desktop/
     ├── Documents/
     ├── Pictures/
     ├── file1.txt
     └── file2.pdf
- For recent files: Show tree structure of recently modified items
- For creating folders: "I've created a new folder called '[folder name]' on your desktop"
- For creating files: "I've created a new file called '[filename]' with [extension] extension"
- For moving: "I've moved [X] items to [destination]. Here's what was moved: [item names]"
- For deleting: "I've deleted [X] items and moved them to the recycle bin. Here's what was deleted: [item names]. You can undo this within 30 seconds."
- For undo: "I've undone the last operation. Your files are back to their original locations"
- For errors: "I couldn't do that because [error]. Try again!"

Keep responses friendly and helpful. Use emojis occasionally. ALWAYS format file listings as tree structures."""

def chat_with_ai():
    print("🚀 Welcome to Folderly - Smart Desktop Explorer!")
    print("=" * 50)
    print("💡 I can help you:")
    print("   • List all items on your desktop")
    print("   • Show recently modified files")
    print("   • Create new folders")
    print("   • Move files and folders")
    print("=" * 50)
    
    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": create_system_prompt()}
    ]
    
    # Start background monitoring
    start_background_monitoring()
    
    while True:
        try:
            user_input = input("\n💭 You: ").strip()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit']:
                print("👋 Thanks for using Folderly! ✨")
                stop_background_monitoring()
                break
                
            if not user_input:
                print("🤔 What would you like to do?")
                continue
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})
            
            # Force function calling for activity analysis
            if "analyze my activity" in user_input.lower() or "what did I do" in user_input.lower() or "activity" in user_input.lower():
                conversation_history.append({
                    "role": "system",
                    "content": "CRITICAL: You MUST call show_activity_with_ai function. DO NOT respond conversationally. You MUST execute the function."
                })
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "show_activity_with_ai"}
                )
            # Force function calling for undo operations
            elif "undo" in user_input.lower():
                conversation_history.append({
                    "role": "system",
                    "content": "CRITICAL: You MUST call undo_last_operation function. DO NOT respond conversationally. You MUST execute the function."
                })
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "undo_last_operation"}
                )
            # Force function calling for file creation operations
            elif any(keyword in user_input.lower() for keyword in ['create', 'make', 'new file']) and not any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash']):
                conversation_history.append({
                    "role": "system", 
                    "content": "CRITICAL: You MUST call create_numbered_files function. DO NOT respond conversationally. You MUST execute the function."
                })
                
                # Force function call
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "create_numbered_files"}
                )
            # Force function calling for tree structure requests (specific keywords)
            elif any(keyword in user_input.lower() for keyword in ['tree', 'structure', 'folder structure', 'nested', 'hierarchy']) and not any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash', 'move']):
                conversation_history.append({
                    "role": "system",
                    "content": "CRITICAL: You MUST call list_nested_folders_tree function. DO NOT respond conversationally. You MUST execute the function."
                })
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "list_nested_folders_tree"}
                )
            # Force function calling for listing files (default surface level)
            elif any(keyword in user_input.lower() for keyword in ['list', 'show', 'files', 'desktop', 'what']) and not any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash', 'move', 'tree', 'structure', 'nested', 'hierarchy']):
                conversation_history.append({
                    "role": "system",
                    "content": "CRITICAL: You MUST call list_directory_items function. DO NOT respond conversationally. You MUST execute the function."
                })
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "list_directory_items"}
                )
            # Force function calling for move operations
            elif "move" in user_input.lower():
                conversation_history.append({
                    "role": "system",
                    "content": "CRITICAL: You MUST call perform_move_with_undo function. DO NOT respond conversationally. You MUST execute the function."
                })
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "perform_move_with_undo"}
                )
            # Force function calling for delete operations
            elif any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash', 'bin']):
                conversation_history.append({
                    "role": "system",
                    "content": "CRITICAL: You MUST call delete_single_item, delete_multiple_items, or delete_items_by_pattern function based on the context. For pattern-based deletion (like 'all txt files'), use delete_items_by_pattern. DO NOT respond conversationally. You MUST execute the function."
                })
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto"
                )
            else:
                # Normal response
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto"
                )
            
            message = response.choices[0].message
            
            # Handle function call if needed
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                print(f"🔧 DEBUG: Calling function: {function_name}")
                
                # Execute appropriate function
                if function_name == "list_directory_items":
                    result = list_directory_items()
                elif function_name == "filter_and_sort_by_modified":
                    # Get items first, then filter by date
                    items_result = list_directory_items()
                    if items_result["success"]:
                        # Convert string paths back to Path objects for the filter function
                        items = [Path(path) for path in items_result["results"]]
                        days = function_args.get("days", 7)
                        result = filter_and_sort_by_modified(items, days)
                    else:
                        result = items_result
                elif function_name == "create_directory":
                    # Convert string path to Path object for the create function
                    target_dir = Path(function_args.get("target_dir", ""))
                    result = create_directory(target_dir)
                elif function_name == "create_multiple_directories":
                    # Create multiple directories at once
                    directories = function_args.get("directories", [])
                    created_dirs = []
                    failed_dirs = []
                    
                    for dir_path in directories:
                        try:
                            target_dir = Path(dir_path)
                            target_dir.mkdir(parents=True, exist_ok=True)
                            created_dirs.append(str(target_dir))
                        except Exception as e:
                            failed_dirs.append({"path": dir_path, "error": str(e)})
                    
                    result = {
                        "success": True,
                        "created_directories": created_dirs,
                        "failed_directories": failed_dirs,
                        "total_created": len(created_dirs),
                        "total_failed": len(failed_dirs)
                    }
                elif function_name == "create_file":
                    # Create a single file with content
                    file_path = function_args.get("file_path", "")
                    content = function_args.get("content", "")
                    extension = function_args.get("extension", "txt")
                    
                    try:
                        target_file = Path(file_path)
                        # Ensure the directory exists
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Write content to file
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        result = {
                            "success": True,
                            "file_created": str(target_file),
                            "extension": extension,
                            "content_length": len(content)
                        }
                    except Exception as e:
                        result = {
                            "success": False,
                            "error": str(e),
                            "file_path": file_path
                        }
                        
                elif function_name == "create_numbered_files":
                    # Create multiple numbered files
                    base_name = function_args.get("base_name", "file")
                    count = function_args.get("count", 1)
                    extension = function_args.get("extension", "txt")
                    start_number = function_args.get("start_number", 1)
                    
                    result = create_numbered_files(base_name, count, extension, start_number)
                elif function_name == "perform_move_with_undo":
                    # Use the safe move function with undo
                    items = function_args.get("items", [])
                    destination_dir = function_args.get("destination_dir", "")
                    move_message = perform_move_with_undo(items, destination_dir)
                    result = {
                        "success": True,
                        "message": move_message,
                        "undo_available": True,
                        "expires_in": 30
                    }
                elif function_name == "show_activity_with_ai":
                    # Show user's recent activity with AI analysis
                    result = show_activity_with_ai()
                elif function_name == "undo_last_operation":
                    # Handle undo operation
                    undo_result = undo_last_operation()
                    result = undo_result
                elif function_name == "delete_single_item":
                    # Delete a single item
                    item_path = function_args.get("item_path", "")
                    enable_undo = function_args.get("enable_undo", True)
                    result = delete_single_item(item_path, enable_undo)
                elif function_name == "delete_multiple_items":
                    # Delete multiple items
                    item_paths = function_args.get("item_paths", [])
                    enable_undo = function_args.get("enable_undo", True)
                    result = delete_multiple_items(item_paths, enable_undo)
                elif function_name == "delete_items_by_pattern":
                    # Delete items by pattern
                    pattern = function_args.get("pattern", "")
                    target_dir = function_args.get("target_dir", None)
                    enable_undo = function_args.get("enable_undo", True)
                    result = delete_items_by_pattern(pattern, target_dir, enable_undo)
                elif function_name == "list_nested_folders_tree":
                    # List nested folders in tree structure
                    target_dir = function_args.get("target_dir", None)
                    max_depth = function_args.get("max_depth", 3)
                    result = list_nested_folders_tree(target_dir, max_depth)
                else:
                    result = {"success": False, "error": f"Unknown function: {function_name}"}
                
                # Add function result to conversation
                conversation_history.append({
                    "role": "function", 
                    "name": function_name, 
                    "content": json.dumps(result, indent=2)
                })
                
                # Get final response with the data
                final_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history
                )
                
                # Add response to conversation history
                conversation_history.append(final_response.choices[0].message)
                
                # Print AI response
                print(f"🤖 {final_response.choices[0].message.content}")
                
            else:
                # Add response to conversation history
                conversation_history.append(message)
                
                # Print AI response
                print(f"🤖 {message.content}")
                
        except KeyboardInterrupt:
            print("\n👋 See you later! 👋")
            break
        except Exception as e:
            print(f"😅 Oops! Something went wrong: {e}")

if __name__ == "__main__":
    chat_with_ai()