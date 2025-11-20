# Troubleshooting Guide - 401 Error "User not found"

## Problem
Getting `401 - User not found` error when calling OpenRouter API with all models.

## Root Causes

### 1. **API Key Issues**
- API key may be invalid or expired
- API key may not be correctly loaded from `.env` file
- API key format may be incorrect

### 2. **OpenRouter API Requirements**
OpenRouter requires specific HTTP headers:
- `Authorization: Bearer {api_key}`
- `HTTP-Referer` (optional but recommended)
- `X-Title` (optional but recommended)

### 3. **Account Issues**
- OpenRouter account may not be properly set up
- Account may have insufficient credits
- API key may not have proper permissions

## Solutions

### Solution 1: Verify API Key

1. **Check .env file exists and contains correct key:**
   ```bash
   type .env
   ```

2. **Verify API key format:**
   - Should start with `sk-or-v1-`
   - Should be a long string (usually 100+ characters)

3. **Test API key directly:**
   ```python
   import requests
   
   response = requests.post(
       "https://openrouter.ai/api/v1/chat/completions",
       headers={
           "Authorization": f"Bearer YOUR_API_KEY",
           "HTTP-Referer": "https://github.com/yourusername/ise547project",
           "X-Title": "Chat with Your Data"
       },
       json={
           "model": "openai/gpt-4",
           "messages": [{"role": "user", "content": "Hello"}]
       }
   )
   print(response.json())
   ```

### Solution 2: Check OpenRouter Account

1. **Visit OpenRouter Dashboard:**
   - Go to https://openrouter.ai/keys
   - Verify your API key is active
   - Check account balance/credits

2. **Verify API key permissions:**
   - Make sure the key has access to the models you're trying to use
   - Some models may require special permissions

### Solution 3: Update Code (Already Fixed)

The code has been updated to include required headers. Make sure you're using the latest version of `llm_providers/openrouter_provider.py`.

### Solution 4: Re-run Setup

1. **Delete existing .env file:**
   ```bash
   del .env
   ```

2. **Re-run setup:**
   ```bash
   setup_env.bat
   ```

3. **Restart the application:**
   ```bash
   python frontend.py
   ```

### Solution 5: Check API Key in Code

Add debug logging to verify API key is loaded:

```python
# In frontend.py, after loading API key
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
print(f"API Key loaded: {OPENROUTER_API_KEY[:20]}...")  # Print first 20 chars
```

## Common Issues

### Issue 1: API Key Not Loading
**Symptom:** Error says API key is not set
**Solution:** 
- Make sure `.env` file is in the same directory as `frontend.py`
- Run `setup_env.bat` again
- Restart the application

### Issue 2: Invalid API Key Format
**Symptom:** 401 error persists
**Solution:**
- Verify API key from OpenRouter dashboard
- Make sure there are no extra spaces or newlines
- Copy the key directly from OpenRouter website

### Issue 3: Account Not Found
**Symptom:** "User not found" error
**Solution:**
- Log into OpenRouter account
- Verify account is active
- Check if you need to verify email
- Ensure you have credits/balance

### Issue 4: Model Access Issues
**Symptom:** Works with some models but not others
**Solution:**
- Some models may require special access
- Check OpenRouter model availability
- Verify your account tier supports the models

## Verification Steps

1. **Check .env file:**
   ```bash
   type .env
   ```
   Should show:
   ```
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

2. **Test API key manually:**
   Use the Python test script above

3. **Check application logs:**
   Look for "OpenRouter API client initialized successfully" message

4. **Try a simple request:**
   Use the model selector to try different models

## Still Having Issues?

1. **Check OpenRouter Status:**
   - Visit https://status.openrouter.ai
   - Check for service outages

2. **Contact OpenRouter Support:**
   - Visit https://openrouter.ai/docs
   - Check their Discord or support channels

3. **Verify Network:**
   - Make sure you can access https://openrouter.ai
   - Check firewall/proxy settings

## Updated Code

The code has been updated to include proper headers. Make sure you have the latest version with:
- `HTTP-Referer` header
- `X-Title` header
- Proper error handling




