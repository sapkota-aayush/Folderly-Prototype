# Usage Guide

## Quick Start

### AI-Powered Interface (Recommended)
```bash
python -m src.ai.ai_integration
```

Start with simple commands:
- "list all my files"
- "create a folder called work"
- "show me recently modified files"

### Traditional CLI Interface
```bash
python -m src.cli.cli
```

## AI Interface Commands

### File Listing & Exploration
```
"list all my files"
"show me everything on my desktop"
"what files do I have?"
```

### File Creation
```
"create a folder called work"
"make a new folder named documents"
"create a file called notes.txt"
"make a file called todo.txt with some content"
```

### File Operations
```
"move all txt files to documents"
"move heyy.txt to the work folder"
"delete heyy.txt"
"delete all temp files"
```

### Search & Filter
```
"show me only txt files"
"find files modified today"
"list files created this week"
"show me the biggest files"
```

### Undo Operations
```
"undo my last operation"
"undo the last move"
"undo the last delete"
```

## CLI Interface Commands

### Main Menu Options
1. **List Desktop Items** - Show all files and folders
2. **Show Recent Files** - Display recently modified items
3. **Create Folder** - Create a new directory
4. **Move Items** - Move files/folders with undo support
5. **Delete Items** - Safely delete with undo support
6. **Undo Last Operation** - Reverse the last action

### Interactive Prompts
The CLI will guide you through each operation with clear prompts:
- Select items by number
- Confirm actions before execution
- See operation results immediately

## Safety Features

### Backup System
- **Automatic backups** created before any destructive operation
- **Backup location**: `data/backups/` folder
- **Backup naming**: Includes timestamp and operation type

### Undo System
- **30-second window** to undo operations
- **Works for**: Move, delete, and create operations
- **How to use**: Type "undo" or use the undo menu option

### Soft Delete
- **Files go to recycle bin** instead of permanent deletion
- **Recoverable** through normal Windows recycle bin
- **Safe by default** - no permanent data loss

## Advanced Features

### Activity Tracking
The system automatically tracks your file usage patterns:
- **File access patterns**
- **Most used files**
- **Least used files**
- **AI-powered insights**
- **2-day retention policy** - Automatic cleanup of old activity data
- **Smart cleanup** - Removes activities older than 2 days automatically

### Background Operations
- **Auto-cleanup** runs in background threads
- **Non-blocking** operations for better UX
- **Activity monitoring** without interrupting your work

## Examples

### Example 1: Organizing Work Files
```
User: "create a folder called work"
AI: "I've created a new folder called 'work' on your desktop"

User: "move all txt files to work"
AI: "I've moved 3 txt files to the work folder"

User: "undo that"
AI: "I've undone the move operation. Files are back on your desktop"
```

### Example 2: Cleaning Up Desktop
```
User: "list all my files"
AI: "Here are your desktop items: [list of files]"

User: "delete all temp files"
AI: "I've deleted 5 temp files. You can undo this within 30 seconds"

User: "undo my last operation"
AI: "I've restored the 5 temp files to your desktop"
```

### Example 3: Finding Specific Files
```
User: "show me only pdf files"
AI: "Here are the PDF files on your desktop: [list]"

User: "find files modified today"
AI: "Here are files modified today: [list]"
```

## Tips & Best Practices

### For AI Interface
1. **Use natural language** - "create a folder" instead of technical commands
2. **Be specific** - "move all txt files" is clearer than "move some files"
3. **Use undo quickly** - You have 30 seconds to undo operations
4. **Check before deleting** - List files first to see what you're working with

### For CLI Interface
1. **Read prompts carefully** - Each option is clearly explained
2. **Use numbers to select** - Type the number corresponding to your choice
3. **Confirm actions** - The system will ask for confirmation before destructive operations
4. **Check results** - Always verify the operation completed successfully

### General Tips
1. **Start small** - Try listing files before moving or deleting
2. **Use undo feature** - It's there for safety, don't hesitate to use it
3. **Keep backups** - The system creates them automatically, but you can also manually backup important files
4. **Monitor activity** - Check the activity tracking to understand your file usage patterns

## Troubleshooting

### Common Issues

#### "I can't find my files after moving them"
- Check the destination folder
- Use the undo feature if within 30 seconds
- Check the recycle bin if you deleted them

#### "The AI isn't understanding my command"
- Try rephrasing in simpler terms
- Use specific file names instead of general terms
- Check that your OpenAI API key is working

#### "Undo isn't working"
- Make sure you're within the 30-second window
- Check that the operation was actually completed
- Try the CLI interface for more control

#### "I'm getting import errors"
- Run `python test_imports.py` to check your installation
- Make sure you're in the project root directory
- Verify all dependencies are installed

## Getting Help

If you need assistance:
1. **Check this guide** for common solutions
2. **Try the troubleshooting section** in the installation guide
3. **Use the test script** to verify your setup
4. **Open an issue** on GitHub with detailed information 