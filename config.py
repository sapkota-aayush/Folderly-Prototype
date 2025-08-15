# ============================================================================
# FOLDERLY CONFIGURATION
# ============================================================================
import os

# Change this to any folder you want to manage
# Examples: "Desktop", "Documents", "Downloads", "Pictures", "Work", "Projects"
TARGET_FOLDER = "Desktop"  # Easy to change!

# ============================================================================
# SECURE API CONFIGURATION
# ============================================================================
# Get API key from environment variable (most secure)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ============================================================================
# ADVANCED CONFIGURATION (Optional)
# ============================================================================

# Maximum depth for tree structure display
MAX_TREE_DEPTH = 3

# Undo window in seconds
UNDO_WINDOW_SECONDS = 30

# Backup retention in seconds
BACKUP_RETENTION_SECONDS = 300  # 5 minutes

# ============================================================================
# SECURITY NOTES:
# ============================================================================
# 🔒 NEVER hardcode API keys in your code!
# 🔒 Use environment variables: export OPENAI_API_KEY="your_key_here"
# 🔒 Keep .env files out of version control (already in .gitignore)
