# Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.8 or higher
- **Memory**: At least 4GB RAM
- **Storage**: 100MB free space

### Required Software
1. **Python 3.8+**
   ```bash
   # Check your Python version
   python --version
   ```

2. **Git** (for cloning the repository)
   ```bash
   # Check if Git is installed
   git --version
   ```

3. **OpenAI API Key** (for AI features)
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Create an API key
   - Keep it secure (you'll need it for setup)

## Installation Steps

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Folderly-ProtoType
```

### Step 2: Set Up Python Environment

#### Option A: Using uv (Recommended)
```bash
# Install uv if you haven't already
pip install uv

# Install dependencies
uv pip install -r requirements.txt
```

#### Option B: Using pip
```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure OpenAI API Key

Create a `.env` file in the project root:
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Or manually create `.env` file with:
```
OPENAI_API_KEY=your_actual_api_key_here
```

### Step 4: Verify Installation

Run the import test to ensure everything is working:
```bash
python test_imports.py
```

You should see:
```
🧪 Testing imports from new module structure...
✅ Core imports successful
✅ Utils imports successful
✅ AI imports successful
✅ CLI imports successful
🎉 All imports working correctly!
```

## Troubleshooting

### Common Issues

#### 1. "No module named 'src'"
**Solution**: Make sure you're in the project root directory and run:
```bash
python -m src.ai.ai_integration
```

#### 2. "OPENAI_API_KEY not found"
**Solution**: Check that your `.env` file exists and contains the correct API key.

#### 3. Import errors
**Solution**: Ensure all dependencies are installed:
```bash
uv pip install -r requirements.txt
```

#### 4. Permission errors on Windows
**Solution**: Run PowerShell as Administrator or use:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

After successful installation:
1. **Test the AI interface**: `python -m src.ai.ai_integration`
2. **Try the CLI**: `python -m src.cli.cli`
3. **Read the usage guide**: See `docs/USAGE.md`

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the error messages carefully
3. Ensure all prerequisites are met
4. Open an issue on GitHub with detailed error information 