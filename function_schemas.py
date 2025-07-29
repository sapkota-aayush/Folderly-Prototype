"""
Folderly AI Function Calling Schemas
JSON schemas for AI function calling in the Folderly codebase.
"""

from typing import Dict, List, Any

# ============================================================================
# AI FUNCTION CALLING SCHEMAS (OLD FORMAT)
# ============================================================================

FOLDERLY_FUNCTIONS = [
    {
        "name": "list_directory_items",
        "description": "Lists all files and folders on the Desktop",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "filter_and_sort_by_modified",
        "description": "Finds recently modified items within specified days and sorts them by modification time",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file/folder paths to filter"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back for modified items"
                }
            },
            "required": ["items", "days"]
        }
    },
    {
        "name": "create_directory",
        "description": "Creates a new directory at the specified path",
        "parameters": {
            "type": "object",
            "properties": {
                "target_dir": {
                    "type": "string",
                    "description": "Path where the directory should be created"
                }
            },
            "required": ["target_dir"]
        }
    },
    {
        "name": "move_items_to_directory",
        "description": "Moves specified files and folders to a destination directory",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file/folder paths to move"
                },
                "destination_dir": {
                    "type": "string",
                    "description": "Destination directory path where items will be moved"
                }
            },
            "required": ["items", "destination_dir"]
        }
    }
]

def get_function_schemas() -> List[Dict[str, Any]]:
    """
    Returns the list of function schemas for AI function calling.
    
    Returns:
        List[Dict[str, Any]]: List of function schemas in OpenAI function calling format
    """
    return FOLDERLY_FUNCTIONS 