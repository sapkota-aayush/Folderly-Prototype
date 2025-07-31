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
        "name": "create_multiple_directories",
        "description": "Creates multiple directories at once",
        "parameters": {
            "type": "object",
            "properties": {
                "directories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of directory paths to create"
                }
            },
            "required": ["directories"]
        }
    },
    {
        "name": "create_file",
        "description": "Creates a new file with specified content and extension",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Full path where the file should be created (including filename and extension)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write in the file (optional)"
                },
                "extension": {
                    "type": "string",
                    "description": "File extension (e.g., txt, py, js, html, css, json)"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "create_numbered_files",
        "description": "Creates multiple numbered files with specified extension (e.g., file_1.txt, file_2.txt)",
        "parameters": {
            "type": "object",
            "properties": {
                "base_name": {
                    "type": "string",
                    "description": "Base name for files (e.g., 'file', 'test', 'document')"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of files to create"
                },
                "extension": {
                    "type": "string",
                    "description": "File extension (e.g., 'txt', 'py', 'js', 'html')"
                },
                "start_number": {
                    "type": "integer",
                    "description": "Starting number (default: 1)"
                }
            },
            "required": ["base_name", "count", "extension"]
        }
    },
    {
        "name": "perform_move_with_undo",
        "description": "Safely moves specified files and folders to a destination directory with undo support (30-second window)",
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
    },
    {
        "name": "undo_last_operation",
        "description": "Undoes the last move operation if within 30 seconds",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "show_activity_with_ai",
        "description": "Show user's recent file activity with AI analysis and insights",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "delete_single_item",
        "description": "Soft deletes a single file or directory using send2trash (moves to recycle bin) with undo support",
        "parameters": {
            "type": "object",
            "properties": {
                "item_path": {
                    "type": "string",
                    "description": "Path to the file or directory to delete"
                },
                "enable_undo": {
                    "type": "boolean",
                    "description": "Whether to enable undo support (default: true)"
                }
            },
            "required": ["item_path"]
        }
    },
    {
        "name": "delete_multiple_items",
        "description": "Soft deletes multiple files and directories using send2trash (moves to recycle bin) with undo support",
        "parameters": {
            "type": "object",
            "properties": {
                "item_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of paths to files or directories to delete"
                },
                "enable_undo": {
                    "type": "boolean",
                    "description": "Whether to enable undo support (default: true)"
                }
            },
            "required": ["item_paths"]
        }
    },
    {
        "name": "delete_items_by_pattern",
        "description": "Deletes files and directories matching a pattern using soft delete (moves to recycle bin) with undo support. Use this for deleting files by type (e.g., 'all txt files', 'all temp files')",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match (e.g., '*.txt', 'test*', '*temp*', 'temp*')"
                },
                "target_dir": {
                    "type": "string",
                    "description": "Directory to search in (default: Desktop)"
                },
                "enable_undo": {
                    "type": "boolean",
                    "description": "Whether to enable undo support (default: true)"
                }
            },
            "required": ["pattern"]
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