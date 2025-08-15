# 🔒 Folderly Security Setup Guide

## **IMPORTANT: API Key Security** 🚨

**Never hardcode API keys in your code!** This is a major security risk that could expose your API keys to anyone who sees your code.

## **How to Set Up Your API Key Securely** ✅

### **Option 1: Environment Variables (Recommended)**

#### **Windows (PowerShell):**
```powershell
# Set for current session
$env:OPENAI_API_KEY="your_actual_api_key_here"

# Set permanently (requires restart)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_actual_api_key_here", "User")
```

#### **Windows (Command Prompt):**
```cmd
# Set for current session
set OPENAI_API_KEY=your_actual_api_key_here

# Set permanently (requires restart)
setx OPENAI_API_KEY "your_actual_api_key_here"
```

#### **macOS/Linux:**
```bash
# Set for current session
export OPENAI_API_KEY="your_actual_api_key_here"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="your_actual_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### **Option 2: .env File (Alternative)**

1. **Create a `.env` file** in your project root:
```bash
# .env file content
OPENAI_API_KEY=your_actual_api_key_here
```

2. **The `.env` file is already protected** by `.gitignore` and won't be committed

## **Get Your OpenAI API Key** 🔑

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Keep it secret!** Never share it publicly

## **Verify Your Setup** ✅

After setting up your API key, test it:

```bash
# Windows
echo %OPENAI_API_KEY%

# macOS/Linux
echo $OPENAI_API_KEY
```

You should see your API key (or nothing if not set).

## **Security Best Practices** 🛡️

- ✅ **Use environment variables** when possible
- ✅ **Keep .env files local** and never commit them
- ✅ **Rotate API keys** regularly
- ✅ **Monitor API usage** in OpenAI dashboard
- ✅ **Use least privilege** - only give necessary permissions
- ❌ **Never hardcode** API keys in source code
- ❌ **Never commit** API keys to version control
- ❌ **Never share** API keys publicly

## **Troubleshooting** 🔧

### **"API key not found" error:**
1. Check if environment variable is set correctly
2. Restart your terminal/IDE after setting environment variables
3. Verify the variable name is exactly `OPENAI_API_KEY`

### **"Permission denied" error:**
1. Check if your API key is valid
2. Verify you have sufficient OpenAI credits
3. Check OpenAI service status

## **Need Help?** 🆘

If you're still having issues:
1. Check the [OpenAI API documentation](https://platform.openai.com/docs)
2. Verify your API key format (should start with `sk-`)
3. Ensure you have sufficient account credits

---

**Remember: Security is everyone's responsibility!** 🔒
