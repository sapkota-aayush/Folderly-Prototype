# Folderly - Smart Desktop File Management with AI Integration 🚀

Folderly is an intelligent desktop file management system that combines powerful file operations with AI-powered assistance. It helps you organize, declutter, and manage your files across Desktop, Documents, Downloads, and other folders with natural language commands and smart automation.

## ✨ **Current Features (v1.0)**

### **🤖 AI-Powered Interface**
- **Natural language commands** - "list my desktop", "create a folder called work", "move all txt files to documents"
- **Smart function selection** - AI automatically chooses the right operation for your request
- **Beautiful formatted output** - Clean, emoji-enhanced results with full paths for operations
- **Multi-task handling** - Execute multiple operations from a single command

### **📁 Core File Operations**
- **List and explore** files/folders with advanced filtering (extension, type, date, size)
- **Create directories** - Single or multiple nested folders
- **Move files/folders** - Bulk operations with smart execution
- **Copy items** - Safe copying with conflict handling
- **Rename items** - Batch renaming operations
- **Delete safely** - Files go to recycle bin (not permanent deletion)
- **Search and filter** - By pattern, extension, file type, or modification date

### **⚡ Performance & Smart Execution**
- **Async operations** - Non-blocking file operations for better performance
- **Smart execution strategy** - Automatic parallel/sequential mode selection
- **Parallel processing** - Multiple independent operations run simultaneously
- **Sequential safety** - Dependent operations execute in order

### **🎯 Easy Configuration**
- **Flexible targeting** - Manage Desktop, Documents, Downloads, Pictures, Music, Videos
- **OneDrive support** - Automatic detection of OneDrive folder structures
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Simple setup** - Just set your OpenAI API key and start using

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- OpenAI API key

### **Installation**

#### **Option 1: Poetry (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd Folderly-ProtoType

# Install dependencies
poetry install

# Set up your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Start using Folderly!
poetry run folderly-ai
```

#### **Option 2: Traditional Python**
```bash
# Clone the repository
git clone <repository-url>
cd Folderly-ProtoType

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Start using Folderly!
python -m src.ai.ai_integration
```

## 💬 **Usage Examples**

### **Listing and Exploring**
```
💭 You: list my desktop
🤖 📋 Items in Desktop:
    1. .git.lnk
    2. ai_test_destination  
    3. Animals
    4. async practice
    5. Backup

💭 You: show me all PDF files in documents
🤖 📋 PDF Files in Documents:
    1. report.pdf
    2. presentation.pdf
    3. manual.pdf
```

### **Creating and Organizing**
```
💭 You: create a folder called "work" and move all txt files there
🤖 🎯 Operation Results:
    ✅ Created: 'work' folder
       📍 Location: Desktop
       🗂️ Full Path: C:/Users/username/Desktop/work

    ✅ Moved: 'notes.txt', 'todo.txt', 'ideas.txt'
       📍 Destination: work folder
       🗂️ Full Path: C:/Users/username/Desktop/work/[filename]
```

### **Bulk Operations**
```
💭 You: delete all temporary files and create backup folders
🤖 🎯 Operation Results:
    ✅ Deleted: 'temp1.txt', 'temp2.txt', 'temp3.txt'
       📍 Method: sent_to_trash
       🗂️ Files moved to recycle bin

    ✅ Created: 'backup_2024', 'backup_2023', 'backup_2022'
       📍 Location: Desktop
       🗂️ Full Path: C:/Users/username/Desktop/backup_[year]
```

## 🏗️ **Project Structure**

```
Folderly-ProtoType/
├── src/
│   ├── core/           # Core file operations
│   │   ├── core.py     # Main file operations (async)
│   │   └── search.py   # Search functionality
│   ├── ai/             # AI integration
│   │   ├── ai_integration.py    # AI conversation interface
│   │   ├── function_schemas.py  # OpenAI function definitions
│   │   └── prompts.py          # AI system prompts
│   ├── cli/            # Command line interface
│   │   └── cli.py     # Traditional CLI
│   └── utils/          # Utility functions
│       └── utils.py    # General utilities
├── tests/              # Test files
├── docs/               # Documentation
├── pyproject.toml      # Poetry configuration
└── requirements.txt    # Dependencies
```

## 🔧 **Technical Features**

### **Async Architecture**
- **Non-blocking I/O** - File operations don't freeze the interface
- **Smart execution modes** - Automatic parallel/sequential selection
- **Performance optimization** - Bulk operations run efficiently

### **AI Integration**
- **OpenAI GPT-4o** - Latest AI model for natural language understanding
- **Function calling** - Precise operation execution
- **Context awareness** - AI remembers conversation history
- **Structured responses** - Clean, formatted output

### **Safety & Reliability**
- **Safe deletion** - Files go to recycle bin, not permanently deleted
- **Error handling** - Graceful failure with helpful error messages
- **Permission checking** - Respects file system permissions
- **Conflict resolution** - Handles naming conflicts intelligently

## 📦 **Dependencies**

### **Core Dependencies**
- **openai** - AI integration and function calling
- **python-dotenv** - Environment variable management
- **send2trash** - Safe file deletion (recycle bin)

### **Development Dependencies**
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Code linting

## 🔮 **Future Enhancements**

The following features are planned for future versions:

### **File Monitoring & Automation**
- **Real-time file watching** - Monitor folders for changes
- **Automated organization** - Smart file sorting and categorization
- **Scheduled operations** - Automated cleanup and maintenance

### **Advanced Undo & Recovery**
- **Extended undo window** - Longer operation history
- **Selective undo** - Choose which operations to reverse
- **Operation replay** - Replay successful operations

### **Enhanced AI Features**
- **Learning patterns** - AI learns from your file organization habits
- **Predictive suggestions** - Suggest operations before you ask
- **Smart categorization** - Automatic file type detection and organization

### **Cloud Integration**
- **Multi-device sync** - Access your organization from anywhere
- **Cloud storage support** - Google Drive, OneDrive, Dropbox integration
- **Backup automation** - Automatic cloud backups

## 🧪 **Testing**

```bash
# Run all tests
poetry run pytest

# Run specific test files
poetry run pytest tests/test_core.py

# Run with coverage
poetry run pytest --cov=src
```

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `poetry run pytest`
5. **Submit a pull request**

### **Development Setup**
```bash
# Install development dependencies
poetry install --with dev

# Run linting
poetry run black src/
poetry run flake8 src/

# Run tests
poetry run pytest
```

## 📝 **License**

This project is open source and available under the MIT License.

## 🙏 **Acknowledgments**

- **OpenAI** - For providing the AI capabilities
- **Python Community** - For the excellent libraries and tools
- **Contributors** - Everyone who helps improve Folderly

---

**Folderly: Your files, intelligently organized.** 🚀✨

*Ready to transform your file management experience? Start with `poetry run folderly-ai` and let AI handle the rest!*