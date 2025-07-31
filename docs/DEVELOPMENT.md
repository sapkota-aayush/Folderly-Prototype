# Development Guide

## Project Architecture

### Module Structure
```
src/
├── core/           # Core file operations
│   ├── core.py     # Main file operations (list, create, delete)
│   └── search.py   # Search and filtering functionality
├── utils/          # Utility functions
│   ├── utils.py    # General utilities and metadata management
│   ├── backup.py   # Backup system for safe operations
│   ├── undo_expiry.py  # Auto-cleanup of expired backups
│   ├── undo_manager.py # Undo operation management
│   └── move_manager.py # Move operations with undo support
├── ai/             # AI integration
│   ├── ai_integration.py  # Main AI interface
│   └── function_schemas.py # OpenAI function schemas
└── cli/            # Command line interface
    └── cli.py      # Traditional CLI interface
```

### Key Design Principles

#### 1. Structured Data Returns
- **No console prints** in core functions
- **Return JSON dictionaries** for AI parsing
- **Consistent response format** across all modules

#### 2. Threading for Background Operations
- **Auto-expiry cleanup** runs in background threads
- **Non-blocking operations** for better UX
- **Thread-safe operations** with proper synchronization

#### 3. Safety First
- **Backup before any destructive operation**
- **30-second undo window** for all operations
- **Soft delete** using recycle bin
- **Metadata tracking** for operation history

## Development Setup

### Prerequisites
```bash
# Install development tools
pip install uv
pip install black flake8 pytest

# Install project dependencies
uv pip install -r requirements.txt
```

### Code Style
```bash
# Format code with black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/
```

### Running Tests
```bash
# Run import tests
python test_imports.py

# Run specific tests
python tests/test_delete_undo.py

# Run all tests (when pytest is set up)
pytest tests/
```

## Adding New Features

### 1. Core Operations
When adding new file operations:

```python
# In src/core/core.py
def new_operation() -> Dict[str, Any]:
    """
    New operation description.
    
    Returns:
        Dict with operation status and results
    """
    try:
        # Your operation logic here
        
        return {
            "success": True,
            "message": "Operation completed successfully",
            "data": result_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### 2. AI Integration
When adding new AI functions:

```python
# In src/ai/function_schemas.py
def get_function_schemas():
    return [
        {
            "name": "new_operation",
            "description": "Description for AI",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param1"]
            }
        }
    ]
```

### 3. CLI Integration
When adding CLI options:

```python
# In src/cli/cli.py
def new_operation_menu():
    """New operation menu"""
    print("\n=== New Operation ===")
    # Your CLI logic here
```

## Threading Guidelines

### Background Operations
```python
import threading

def background_task():
    """Background task that doesn't block the main thread"""
    thread = threading.Thread(target=task_function, daemon=True)
    thread.start()
    return thread

def task_function():
    """The actual task to run in background"""
    # Your background logic here
    pass
```

### Thread Safety
- **Use locks** for shared resources
- **Avoid global variables** when possible
- **Handle exceptions** in background threads
- **Use daemon threads** for cleanup operations

## Testing Guidelines

### Unit Tests
```python
# In tests/test_new_feature.py
import pytest
from src.core.core import new_operation

def test_new_operation_success():
    """Test successful operation"""
    result = new_operation()
    assert result["success"] == True
    assert "data" in result

def test_new_operation_failure():
    """Test operation failure"""
    # Test with invalid inputs
    result = new_operation()
    assert result["success"] == False
    assert "error" in result
```

### Integration Tests
```python
def test_ai_integration():
    """Test AI integration with new feature"""
    # Test that AI can call the new function
    # Test that AI gets proper response format
    pass
```

## Error Handling

### Consistent Error Format
```python
def handle_operation():
    try:
        # Operation logic
        return {"success": True, "data": result}
    except FileNotFoundError as e:
        return {"success": False, "error": f"File not found: {e}"}
    except PermissionError as e:
        return {"success": False, "error": f"Permission denied: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

def operation_with_logging():
    logger.info("Starting operation")
    try:
        # Operation logic
        logger.info("Operation completed successfully")
        return {"success": True}
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return {"success": False, "error": str(e)}
```

## Performance Considerations

### File Operations
- **Batch operations** when possible
- **Use pathlib** for cross-platform compatibility
- **Avoid unnecessary file reads**
- **Cache frequently accessed data**

### AI Integration
- **Limit API calls** to necessary operations
- **Cache function schemas** after first load
- **Handle API timeouts** gracefully
- **Use async operations** for long-running tasks

## Security Guidelines

### File Operations
- **Validate file paths** before operations
- **Check file permissions** before access
- **Sanitize user inputs** for file names
- **Use absolute paths** when possible

### API Keys
- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Validate API key format** before use
- **Handle API key errors** gracefully

## Contributing

### Pull Request Process
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** following the guidelines above
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run tests** to ensure everything works
7. **Submit a pull request** with clear description

### Code Review Checklist
- [ ] **Code follows style guidelines**
- [ ] **Functions return structured data**
- [ ] **Error handling is comprehensive**
- [ ] **Tests are included**
- [ ] **Documentation is updated**
- [ ] **No console prints** in core functions
- [ ] **Thread safety** for background operations

## Debugging

### Common Issues

#### Import Errors
```bash
# Check import structure
python test_imports.py

# Verify module paths
python -c "import src.core.core; print('Core imports work')"
```

#### AI Integration Issues
```bash
# Test AI integration
python -m src.ai.ai_integration

# Check API key
python -c "import os; print('API Key:', bool(os.getenv('OPENAI_API_KEY')))"
```

#### Threading Issues
- **Check for daemon threads** for cleanup operations
- **Verify thread safety** for shared resources
- **Monitor thread lifecycle** in background operations

## Future Enhancements

### Planned Features
- **Web interface** for easier access
- **Plugin system** for extensibility
- **Cloud backup integration**
- **Advanced file analysis**
- **Machine learning** for file organization

### Architecture Improvements
- **Async/await** for better performance
- **Database integration** for metadata
- **Event-driven architecture**
- **Microservices** for scalability 