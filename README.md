# Folderly - Smart Desktop File Management with AI Integration

Folderly is an intelligent desktop file management system that combines traditional file operations with AI-powered assistance. It helps you organize, declutter, and manage your Desktop folder with smart suggestions and automated operations.

## 🚀 Features

### **Core File Operations**
- 📁 **List and explore** all files and folders in your target directory
- 🔍 **Search and filter** files by name, extension, or modification date
- 📦 **Create folders** and organize files efficiently
- 🗂️ **Move files** with undo support and backup safety
- 🗑️ **Delete files** safely with recycle bin and undo functionality

### **Easy Configuration**
- ⚙️ **Simple setup** - Change target folder with one line in `config.py`
- 🎯 **Flexible targeting** - Manage Desktop, Documents, Downloads, or any folder
- 🔧 **Quick customization** - No complex setup required

### **AI-Powered Assistance**
- 🤖 **Natural language commands** - "list all my files", "create a folder called work"
- 🧠 **Smart suggestions** based on your file patterns
- 📊 **Activity tracking** with AI analysis of your file usage
- 🔄 **Automated operations** with safety checks
- 🧹 **Automatic cleanup** - 2-day retention policy for activity logs

### **Safety & Undo System**
- 🔒 **Backup system** - All operations create backups
- ↩️ **Undo support** - Reverse operations within 30 seconds
- 🗑️ **Soft delete** - Files go to recycle bin, not permanent deletion
- ⏰ **Auto-cleanup** - Automatic backup cleanup after expiry

## 📁 Project Structure

```
Folderly-ProtoType/
├── src/
│   ├── core/           # Core file operations
│   │   ├── core.py     # Main file operations
│   │   └── search.py   # Search functionality
│   ├── utils/          # Utility functions
│   │   ├── utils.py    # General utilities
│   │   ├── backup.py   # Backup system
│   │   ├── undo_*.py   # Undo management
│   │   └── move_manager.py
│   ├── ai/             # AI integration
│   │   ├── ai_integration.py
│   │   └── function_schemas.py
│   └── cli/            # Command line interface
│       └── cli.py
├── tests/              # Test files
├── data/               # Data files
├── docs/               # Documentation
└── requirements.txt    # Dependencies
```

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.8+
- OpenAI API key (for AI features)

### **Quick Configuration**
```python
# Edit config.py to change your target folder
TARGET_FOLDER = "Desktop"  # Change to "Documents", "Downloads", etc.
```

### **Installation Options**

#### **Option A: Quick Start (uv + requirements.txt)**
```bash
# Clone the repository
git clone <repository-url>
cd Folderly-ProtoType

# Install dependencies (fast)
uv pip install -r requirements.txt

# Set up your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run the app
python -m src.ai.ai_integration
```

#### **Option B: Professional (Poetry)**
```bash
# Clone the repository
git clone <repository-url>
cd Folderly-ProtoType

# Install dependencies with Poetry
poetry install

# Set up your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run with simple commands
poetry run folderly-ai
poetry run folderly-cli
```

## 🚀 Usage

### **AI-Powered Interface (Recommended)**

#### **With Poetry (Simple Commands):**
```bash
poetry run folderly-ai
```

#### **With Traditional Python:**
```bash
python -m src.ai.ai_integration
```

Then use natural language commands:
- "list all my files"
- "create a folder called work"
- "move all txt files to documents"
- "show me recently modified files"

### **Traditional CLI Interface**

#### **With Poetry (Simple Commands):**
```bash
poetry run folderly-cli
```

#### **With Traditional Python:**
```bash
python -m src.cli.cli
```

## 📦 Dependencies

- **openai** - AI integration
- **watchdog** - File system monitoring
- **send2trash** - Safe file deletion
- **python-dotenv** - Environment management

## 🔧 Development

### **Project Organization**
- **Modular structure** with clear separation of concerns
- **Package-based imports** for clean code organization
- **Threading support** for background operations
- **Structured data returns** instead of console prints

### **Testing**
```bash
# Run import tests
python test_imports.py

# Run specific tests
python tests/test_delete_undo.py
```

## 🎯 Key Features Explained

### **Threading & Background Operations**
- **Auto-expiry cleanup** runs in background threads
- **Activity monitoring** tracks file usage patterns
- **Non-blocking operations** for better user experience

### **Safety Systems**
- **Backup creation** before any destructive operation
- **Undo window** (30 seconds) for all operations
- **Soft deletion** using recycle bin
- **Metadata tracking** for operation history

### **AI Integration**
- **Function calling** for precise operations
- **Natural language processing** for user commands
- **Context awareness** for better suggestions
- **Structured responses** for clean output

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

---

**Folderly: Your Desktop, intelligently organized.** 🚀