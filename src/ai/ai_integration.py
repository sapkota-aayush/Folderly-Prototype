import os
import json
import openai
import threading
import time
import asyncio
from dotenv import load_dotenv
from src.ai.function_schemas import get_function_schemas
from src.ai.prompts import (
    load_system_prompt, load_force_prompt, load_welcome_message, 
    load_goodbye_message, load_empty_input_message, load_error_message
)
from src.core.core import list_directory_items, filter_and_sort_by_modified, create_directory, create_multiple_directories, move_items_to_directory, delete_single_item, delete_multiple_items, delete_items_by_pattern, list_nested_folders_tree, count_files_by_extension, get_file_type_statistics
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
    print(load_error_message("api_key"))
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
        global background_tracker
        if background_tracker is None:
            # If no background tracker, create one
            background_tracker = FolderlyActivityTracker()
        result = show_ai_enhanced_activity(background_tracker)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Could not analyze activity: {str(e)}"
        }

async def chat_with_ai():
    print(load_welcome_message())
    
    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": load_system_prompt()}
    ]
    
    # Start background monitoring
    start_background_monitoring()
    
    while True:
        try:
            user_input = input("\n💭 You: ").strip()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit']:
                print(load_goodbye_message())
                stop_background_monitoring()
                break
                
            if not user_input:
                print(load_empty_input_message())
                continue
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})
            
            # Debug: Print what we're checking
            print(f"🔍 DEBUG: Checking user input: '{user_input.lower()}'")
            print(f"🔍 DEBUG: Contains 'folder'? {'folder' in user_input.lower()}")
            print(f"🔍 DEBUG: Contains 'create'? {'create' in user_input.lower()}")
            print(f"🔍 DEBUG: Folder condition result: {'folder' in user_input.lower() and 'create' in user_input.lower()}")
            
            # Force function calling for activity analysis
            if "analyze my activity" in user_input.lower() or "what did I do" in user_input.lower() or "activity" in user_input.lower():
                print("🔍 DEBUG: Triggered activity analysis condition")
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("activity")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "show_activity_with_ai"}
                )
            # Force function calling for undo operations
            elif "undo" in user_input.lower():
                print("🔍 DEBUG: Triggered undo condition")
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("undo")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "undo_last_operation"}
                )
            # Force function calling for folder creation operations
            elif (('folder' in user_input.lower() or any(keyword in user_input.lower() for keyword in ['structure', 'course', 'project', 'organization', 'setup'])) and 
                  any(keyword in user_input.lower() for keyword in ['create', 'creat', 'make', 'new'])):
                print("🔍 DEBUG: Detected folder creation request")
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("directory_creation")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto"
                )

            # Force function calling for smart folder structure generation
            elif any(keyword in user_input.lower() for keyword in ['structure', 'course', 'project', 'organization', 'setup']) and any(keyword in user_input.lower() for keyword in ['create', 'make', 'generate']):
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("smart_folder_structure")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto"
                )
            # Force function calling for tree structure requests (specific keywords)
            elif any(keyword in user_input.lower() for keyword in ['tree', 'structure', 'folder structure', 'nested', 'hierarchy']) and not any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash', 'move']):
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("tree_structure")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "list_nested_folders_tree"}
                )
            # Force function calling for listing files (default surface level)
            elif any(keyword in user_input.lower() for keyword in ['list', 'show', 'files', 'desktop']) and not any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash', 'move', 'tree', 'structure', 'nested', 'hierarchy', 'can you do', 'what can you', 'help']):
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("list_files")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "list_directory_items"}
                )
            # Force function calling for move operations
            elif "move" in user_input.lower():
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("move")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call={"name": "perform_move_with_undo"}
                )
            # Force function calling for delete operations
            elif any(keyword in user_input.lower() for keyword in ['delete', 'remove', 'trash', 'bin']):
                conversation_history.append({
                    "role": "system",
                    "content": load_force_prompt("delete")
                })
                response = await client.chat.completions.acreate(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto"
                )
            else:
                print("🔍 DEBUG: No specific condition matched, using normal response")
                # Normal response
                response = await client.chat.completions.acreate(
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
                    folder_name = function_args.get("folder_name", None)
                    extension = function_args.get("extension", None)
                    file_type = function_args.get("file_type", None)
                    pattern = function_args.get("pattern", None)
                    date_range = function_args.get("date_range", None)
                    size_range = function_args.get("size_range", None)
                    sort_by = function_args.get("sort_by", "name")
                    sort_order = function_args.get("sort_order", "asc")
                    include_folders = function_args.get("include_folders", True)
                    include_files = function_args.get("include_files", True)
                    max_results = function_args.get("max_results", None)
                    
                    result = await list_directory_items(
                        folder_name=folder_name,
                        extension=extension,
                        file_type=file_type,
                        pattern=pattern,
                        date_range=date_range,
                        size_range=size_range,
                        sort_by=sort_by,
                        sort_order=sort_order,
                        include_folders=include_folders,
                        include_files=include_files,
                        max_results=max_results,
                        execution_mode="parallel"
                    )
                elif function_name == "filter_and_sort_by_modified":
                    # Get items first, then filter by date
                    items_result = await list_directory_items()
                    if items_result["success"]:
                        # Convert string paths back to Path objects for the filter function
                        items = [Path(path) for path in items_result["results"]]
                        days = function_args.get("days", 7)
                        result = await filter_and_sort_by_modified(items, days)
                    else:
                        result = items_result
                elif function_name == "create_directory":
                    # Create directory with base path support
                    target_dir = Path(function_args.get("target_dir", ""))
                    base_path = function_args.get("base_path", "Desktop")
                    result = await create_directory(target_dir, base_path)
                elif function_name == "create_multiple_directories":
                    # Create multiple directories with base path support
                    directories = function_args.get("directories", [])
                    base_path = function_args.get("base_path", "Desktop")
                    result = await create_multiple_directories(directories, base_path)
                
                        
                
                elif function_name == "perform_move_with_undo":
                    # Use the safe move function with undo
                    items = function_args.get("items", [])
                    destination_dir = function_args.get("destination_dir", "")
                    move_message = await perform_move_with_undo(items, destination_dir)
                    result = {
                        "success": True,
                        "message": move_message,
                        "undo_available": True,
                        "expires_in": 30
                    }
                elif function_name == "show_activity_with_ai":
                    # Show user's recent activity with AI analysis
                    result = await show_activity_with_ai()
                elif function_name == "undo_last_operation":
                    # Handle undo operation
                    undo_result = await undo_last_operation()
                    result = undo_result
                elif function_name == "delete_single_item":
                    # Delete a single item
                    item_path = function_args.get("item_path", "")
                    result = await delete_single_item(item_path)
                elif function_name == "delete_multiple_items":
                    # Delete multiple items
                    item_paths = function_args.get("item_paths", [])
                    result = await delete_multiple_items(item_paths)
                elif function_name == "delete_items_by_pattern":
                    # Delete items by pattern
                    pattern = function_args.get("pattern", "")
                    target_dir = function_args.get("target_dir", None)
                    result = await delete_items_by_pattern(pattern, target_dir)
                elif function_name == "list_nested_folders_tree":
                    # List nested folders in tree structure
                    target_dir = function_args.get("target_dir", None)
                    max_depth = function_args.get("max_depth", 3)
                    result = await list_nested_folders_tree(target_dir, max_depth)
                elif function_name == "count_files_by_extension":
                    # Count files by extension
                    folder_name = function_args.get("folder_name", None)
                    result = await count_files_by_extension(folder_name)
                elif function_name == "get_file_type_statistics":
                    # Get file type statistics
                    folder_name = function_args.get("folder_name", None)
                    result = await get_file_type_statistics(folder_name)
                else:
                    result = {"success": False, "error": f"Unknown function: {function_name}"}
                
                # Add function result to conversation
                conversation_history.append({
                    "role": "function", 
                    "name": function_name, 
                    "content": json.dumps(result, indent=2)
                })
                
                # Get final response with the data
                final_response = await client.chat.completions.acreate(
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
            print(load_error_message("generic", str(e)))

if __name__ == "__main__":
    main()