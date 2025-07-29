import os
import json
import openai
from dotenv import load_dotenv
from function_schemas import get_function_schemas
from folderly.core import list_directory_items, filter_and_sort_by_modified, create_directory, move_items_to_directory
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

def create_system_prompt():
    return """You are Folderly, a smart file management assistant. You can help users explore their desktop.

You can do this:
- list_directory_items: Show all files and folders on desktop
- filter_and_sort_by_modified: Show recently modified files/folders
- create_directory: Create a new folder on desktop
- move_items_to_directory: Move files and folders to a destination

RESPONSE PATTERNS:
- For listing: "Here are your desktop items: [item names]"
- For recent files: "Here are files modified in the last [X] days: [item names]"
- For creating: "I've created a new folder called '[folder name]' on your desktop"
- For moving: "I've moved [X] items to [destination]. Here's what was moved: [item names]"
- For errors: "I couldn't do that because [error]. Try again!"

Keep responses friendly and helpful. Use emojis occasionally."""

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
    
    while True:
        try:
            user_input = input("\n💭 You: ").strip()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit']:
                print("👋 Thanks for using Folderly! ✨")
                break
                
            if not user_input:
                print("🤔 What would you like to do?")
                continue
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response with function calling
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
                elif function_name == "move_items_to_directory":
                    # Convert string paths to Path objects for the move function
                    items = [Path(item) for item in function_args.get("items", [])]
                    destination_dir = Path(function_args.get("destination_dir", ""))
                    result = move_items_to_directory(items, destination_dir)
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
                
                print(f"🤖 Folderly: {final_response.choices[0].message.content}")
                conversation_history.append(final_response.choices[0].message)
                
            else:
                print(f"🤖 Folderly: {message.content}")
                conversation_history.append(message)
                
        except KeyboardInterrupt:
            print("\n👋 See you later! 👋")
            break
        except Exception as e:
            print(f"😅 Oops! Something went wrong: {e}")

if __name__ == "__main__":
    chat_with_ai()