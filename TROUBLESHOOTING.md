# Troubleshooting Guide

## ❗ Problem: “Google Gemini API key not found!”

This is the most common setup error. It means the Streamlit app cannot find your `GOOGLE_API_KEY`.

---

## ✅ Solution 1: Check Your `.env` File Format

Your `.env` file must look **exactly** like this (no quotes, no spaces):

```

GOOGLE_API_KEY=YOUR-ACTUAL-GEMINI-KEY-HERE

````

### Common Mistakes to Avoid
- ❌ `GOOGLE_API_KEY = "YOUR-KEY-HERE"` (spaces + quotes)
- ❌ `GOOGLE_API_KEY = YOUR-KEY-HERE` (space after =)
- ❌ `"GOOGLE_API_KEY=YOUR-KEY"` (quotes around the whole line)
- ✅ `GOOGLE_API_KEY=YOUR-KEY-HERE` (correct)

---

## 🔄 Solution 2: Completely Restart Streamlit

The `.env` file is only loaded when Streamlit starts.

1. Press **Ctrl + C** in the terminal to stop the app.
2. Restart it with:  
   ```bash
   streamlit run streamlit_app.py
````

---

## 🛠️ Solution 3: Run the Setup Check

Use the setup verification script to diagnose missing or invalid keys:

```bash
python check_setup.py
```

This script reports:

* Whether `.env` exists
* Whether `GOOGLE_API_KEY` is set
* Any missing dependencies

---

## 📁 Solution 4: Verify File Location

Your `.env` file **must be in the root directory** of the project — the same folder as:

* `streamlit_app.py`
* `config.py`
* `orchestrator.py`

If `.env` is in a different folder, the app cannot read it.

---

## 💻 Solution 5: Set the Environment Variable Manually

If `.env` fails, you can export the API key directly in your shell.

### **Windows (CMD):**

```cmd
set GOOGLE_API_KEY=YOUR_API_KEY_HERE
streamlit run streamlit_app.py
```

### **Windows (PowerShell):**

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
streamlit run streamlit_app.py
```

### **Mac/Linux:**

```bash
export GOOGLE_API_KEY=YOUR_API_KEY_HERE
streamlit run streamlit_app.py
```