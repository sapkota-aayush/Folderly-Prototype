import os
import json
import openai
import asyncio
from dotenv import load_dotenv
from src.ai.function_schemas import get_function_schemas
from src.ai.prompts import (
    load_system_prompt, load_force_prompt, load_welcome_message, 
    load_goodbye_message, load_empty_input_message, load_error_message
)
from src.core.core import list_directory_items, filter_and_sort_by_modified, create_directory, create_multiple_directories, create_numbered_files, move_items_to_directory, delete_single_item, delete_multiple_items, delete_items_by_pattern, list_nested_folders_tree, count_files_by_extension, get_file_type_statistics, copy_multiple_items, rename_multiple_items, discover_user_paths
from pathlib import Path

# Load environment variables
load_dotenv()

# Get API key from environment or use the one passed from CLI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(load_error_message("api_key"))
    exit(1)

print(f"API Key loaded: {'Yes' if api_key else 'No'}")

# Configure OpenAI client - use async client
client = openai.AsyncOpenAI(api_key=api_key)

def main_sync():
    """Synchronous wrapper for async main function - entry point for Poetry script"""
    asyncio.run(chat_with_ai())

async def chat_with_ai():
    print(load_welcome_message())
    
    # Initialize conversation history with fresh system prompt
    conversation_history = [
        {"role": "system", "content": load_system_prompt()}
    ]
    
    while True:
        try:
            user_input = input("\n💭 You: ").strip()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit']:
                print(load_goodbye_message())
                break
                
            if not user_input:
                print(load_empty_input_message())
                continue
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})

            # Inner loop to handle multiple function calls per user input
            while True:
                # Enable streaming for better UX
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation_history,
                    functions=get_function_schemas(),
                    function_call="auto",
                    temperature=0.1,
                    max_tokens=2000,
                    presence_penalty=0.1,
                    frequency_penalty=0.1,
                    stream=True  # Enable streaming for real-time responses
                )
                
                # Variables to track streaming response
                full_content = ""
                function_call_data = {"name": "", "arguments": ""}
                in_function_call = False
                
                # Stream the response in real-time
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        print(content, end="", flush=True)
                    
                    # Handle function calls during streaming
                    if chunk.choices[0].delta.function_call:
                        if not in_function_call:
                            in_function_call = True
                        
                        delta = chunk.choices[0].delta.function_call
                        if delta.name:
                            function_call_data["name"] += delta.name
                        if delta.arguments:
                            function_call_data["arguments"] += delta.arguments
                
                print()  # New line after streaming
                
                # Check if we have a function call
                if function_call_data["name"]:
                    function_name = function_call_data["name"]
                    try:
                        function_args = json.loads(function_call_data["arguments"])
                    except json.JSONDecodeError:
                        # Handle incomplete JSON
                        continue
                    
                    # Helper function to get arguments with defaults
                    def get_arg(key, default=None):
                        return function_args.get(key, default)
                    
                    # Execute appropriate function
                    if function_name == "list_directory_items":
                        result = await list_directory_items(
                            custom_path=get_arg("custom_path"),
                            folder_name=get_arg("folder_name"),
                            extension=get_arg("extension"),
                            file_type=get_arg("file_type"),
                            pattern=get_arg("pattern"),
                            date_range=get_arg("date_range"),
                            size_range=get_arg("size_range"),
                            sort_by=get_arg("sort_by", "name"),
                            sort_order=get_arg("sort_order", "asc"),
                            include_folders=get_arg("include_folders", True),
                            include_files=get_arg("include_files", True),
                            max_results=get_arg("max_results"),
                            summary_only=get_arg("summary_only", True),
                            sample_size=get_arg("sample_size", 5)
                        )
                    elif function_name == "filter_and_sort_by_modified":
                        # Get items first, then filter by date
                        items_result = await list_directory_items(
                            folder_name=get_arg("folder_name", "Desktop"),
                            custom_path=get_arg("custom_path"),
                            summary_only=True,
                            sample_size=5
                        )
                        if items_result["success"]:
                            # Convert string paths back to Path objects for the filter function
                            items = [Path(path) for path in items_result["full_results"]]
                            days = get_arg("days", 7)
                            result = filter_and_sort_by_modified(items, days)  # No await needed
                        else:
                            result = items_result
                    elif function_name == "create_directory":
                        # Create directory with base path support
                        target_dir = Path(get_arg("target_dir", ""))
                        base_path = get_arg("base_path", "Desktop")
                        result = await create_directory(target_dir, base_path)
                    elif function_name == "create_multiple_directories":
                        # Create multiple directories with base path support
                        directories = get_arg("directories", [])
                        base_path = get_arg("base_path", "Desktop")
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await create_multiple_directories(directories, base_path, execution_mode)
                    elif function_name == "create_numbered_files":
                        # Create numbered files with execution mode support
                        base_name = get_arg("base_name", "")
                        count = get_arg("count", 1)
                        extension = get_arg("extension", "txt")
                        start_number = get_arg("start_number", 1)
                        target_dir = get_arg("target_dir", None)
                        custom_path = get_arg("custom_path", None)
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await create_numbered_files(base_name, count, extension, start_number, target_dir, custom_path, execution_mode)
                    elif function_name == "move_items_to_directory":
                        # Move items to destination directory
                        items = [Path(item) for item in get_arg("items", [])]
                        destination_dir = Path(get_arg("destination_dir", ""))
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await move_items_to_directory(items, destination_dir, execution_mode)
                    elif function_name == "delete_single_item":
                        # Delete a single item
                        item_path = get_arg("item_path", "")
                        result = await delete_single_item(item_path)
                    elif function_name == "delete_multiple_items":
                        # Delete multiple items
                        item_paths = get_arg("item_paths", [])
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await delete_multiple_items(item_paths, execution_mode)
                    elif function_name == "delete_items_by_pattern":
                        # Delete items by pattern
                        pattern = get_arg("pattern", "")
                        target_dir = get_arg("target_dir", None)
                        custom_path = get_arg("custom_path", None)
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await delete_items_by_pattern(pattern, target_dir, custom_path, execution_mode)
                    elif function_name == "list_nested_folders_tree":
                        # List nested folders in tree structure
                        target_dir = get_arg("target_dir", None)
                        max_depth = get_arg("max_depth", 3)
                        custom_path = get_arg("custom_path", None)
                        result = list_nested_folders_tree(target_dir, max_depth, custom_path)  # No await needed
                    elif function_name == "count_files_by_extension":
                        # Count files by extension
                        custom_path = get_arg("custom_path", None)
                        folder_name = get_arg("folder_name", None)
                        result = await count_files_by_extension(folder_name, custom_path)
                    elif function_name == "get_file_type_statistics":
                        # Get file type statistics
                        custom_path = get_arg("custom_path", None)
                        folder_name = get_arg("folder_name", None)
                        result = await count_files_by_extension(folder_name, custom_path)
                    elif function_name == "copy_multiple_items":
                        # Copy multiple items to destination directory
                        items = [Path(item) for item in get_arg("items", [])]
                        destination_dir = Path(get_arg("destination_dir", ""))
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await copy_multiple_items(items, destination_dir, execution_mode)
                    elif function_name == "rename_multiple_items":
                        # Rename multiple items with new names
                        items_data = get_arg("items", [])
                        items = [(Path(item["old_path"]), item["new_name"]) for item in items_data]
                        execution_mode = get_arg("execution_mode", "parallel")
                        result = await rename_multiple_items(items, execution_mode)
                    elif function_name == "discover_user_paths":
                        # Discover all user folder paths for path selection
                        result = await discover_user_paths()
                    else:
                        result = {"success": False, "error": f"Unknown function: {function_name}"}
                    
                    # Ensure we have a valid result before proceeding
                    if not result or "success" not in result:
                        result = {"success": False, "error": "Function returned invalid result"}
                    
                    # Add function result to conversation
                    conversation_history.append({
                        "role": "function", 
                        "name": function_name, 
                        "content": json.dumps(result, indent=2)
                    })
                    
                    # Continue the inner loop to see if AI wants to call another function
                    continue
                
                else:
                    # No function call, final model response ready
                    conversation_history.append({
                        "role": "assistant",
                        "content": full_content
                    })
                    break  # Exit the inner loop and wait for next user input
                
        except KeyboardInterrupt:
            print("\n👋 See you later! 👋")
            break
        except Exception as e:
            print(load_error_message("generic", str(e)))

if __name__ == "__main__":
    main_sync()