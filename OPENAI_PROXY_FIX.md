# Fix for OpenAI "proxies" Error

## Problem
The chatbot was returning this error:
```
Client.__init__() got an unexpected keyword argument 'proxies'
```

## Root Cause
The OpenAI library version 1.12.0 had compatibility issues with proxy detection in certain environments.

## Solution Applied

### 1. Updated OpenAI Library
- **Old version**: `openai==1.12.0`
- **New version**: `openai>=1.30.0` (installed: 2.21.0)
- **File**: `backend/requirements.txt`

### 2. Enhanced Client Initialization
Updated `backend/chatbot/ai_service.py` to:
- Use explicit parameters for OpenAI client initialization
- Added timeout and max_retries parameters
- Added specific error handling for TypeError related to proxies
- Better error messages for debugging

### 3. Code Changes

**Before:**
```python
client = OpenAI(api_key=settings.OPENAI_API_KEY)
```

**After:**
```python
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=30.0,
    max_retries=2
)
```

## Testing Steps

1. **Restart the Django server** (if it's running):
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   cd backend
   python manage.py runserver
   ```

2. **Test the chatbot** with these queries:
   - "What products do you have?"
   - "Show me all available products"
   - "List all products"
   - "Which products are under $50?"

3. **Expected behavior**:
   - The chatbot should now respond without errors
   - It will list all approved products with:
     - Product name
     - Description
     - Price
     - Business name
   - Responses will be well-formatted with line breaks

## If You Still Get Errors

If you still encounter issues after restarting the server:

1. **Check your virtual environment is activated**:
   ```bash
   # Windows
   venv\Scripts\activate
   ```

2. **Verify OpenAI version**:
   ```bash
   pip show openai
   # Should show Version: 2.21.0 or higher
   ```

3. **Check your .env file has the OpenAI API key**:
   ```env
   OPENAI_API_KEY=sk-...your-key-here...
   ```

4. **Clear Python cache** (optional):
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   # Or on Windows PowerShell:
   Get-ChildItem -Path . -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force
   ```

## Additional Notes

- The new OpenAI client version (2.21.0) has better error handling and compatibility
- The explicit timeout and retry parameters make the client more robust
- The enhanced error handling will provide clearer messages if other issues occur
