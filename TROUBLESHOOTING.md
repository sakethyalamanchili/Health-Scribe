# Troubleshooting Guide

## Problem: "OpenAI API key not found!"

### Solution 1: Check .env File Format

Your `.env` file should look **exactly** like this (no quotes, no spaces):

\`\`\`
OPENAI_API_KEY=YOUR_API_KEY_HERE
TAVILY_API_KEY=YOUR_API_KEY_HERE
\`\`\`

**Common mistakes:**
- ❌ `OPENAI_API_KEY = "sk-proj-..."` (has quotes and spaces)
- ❌ `OPENAI_API_KEY = sk-proj-...` (has space after =)
- ✅ `OPENAI_API_KEY=sk-proj-...` (correct!)

### Solution 2: Completely Restart Streamlit

1. Press `Ctrl+C` in your terminal to stop Streamlit
2. Close the terminal completely
3. Open a NEW terminal window
4. Navigate to your project directory
5. Run: `streamlit run streamlit_app.py`

### Solution 3: Use the Helper Script

Instead of running Streamlit directly, use the helper script:

\`\`\`bash
python run_app.py
\`\`\`

This script ensures environment variables are loaded before starting Streamlit.

### Solution 4: Set Environment Variable Directly

If the .env file isn't working, set the API key directly in your terminal:

**Windows (CMD):**
\`\`\`cmd
set OPENAI_API_KEY=YOUR_API_KEY_HERE
streamlit run streamlit_app.py
\`\`\`

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY_HERE"
streamlit run streamlit_app.py
