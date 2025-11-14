````markdown
# Quick Start Guide – CareGuide

Get up and running in **5 minutes**!

---

## 🚀 Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
````

This installs:

* `streamlit` — Web UI framework
* `google-generativeai` — Google Gemini API client
* `pydantic` — Data validation
* `python-dotenv` — Environment variable management
* Other utilities

---

## 🔑 Step 2: Get Your Google Gemini API Key (2 min)

1. Visit: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign up or log in with your Google account
3. Click **“Create API key in new project”**
4. Copy the generated key

**Important:** Keep this key secret — *never commit it to GitHub.*

---

## ⚙️ Step 3: Configure Environment (1 min)

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and replace the placeholder:

```env
GOOGLE_API_KEY=YOUR-ACTUAL-GEMINI-KEY-HERE
```

### Common Mistakes to Avoid

* ❌ `GOOGLE_API_KEY="YOUR-KEY..."` (no quotes)
* ❌ `GOOGLE_API_KEY = YOUR-KEY...` (no spaces)
* ✅ `GOOGLE_API_KEY=YOUR-KEY...` (correct format)

---

## 🧪 Step 4: Verify Setup (30 seconds)

```bash
python check_setup.py
```

You should see:

```
✅ .env file exists
✅ GOOGLE_API_KEY is set
✅ streamlit installed
✅ google-generativeai installed
✅ All checks passed!
```

*(If needed, update `check_setup.py` so it checks for `GOOGLE_API_KEY` and `google-generativeai`.)*

---

## ▶️ Step 5: Run the App (30 seconds)

```bash
streamlit run streamlit_app.py
```

The app will open at:

```
http://localhost:8501
```

---

## 📈 What’s Next?

1. **Upload a health record** — Try `data/demo_patient_record.txt`
2. **Watch the AI work** — See each agent analyze the record
3. **Review results** — Check your Health Engagement Score
4. **Export data** — Download the structured JSON output

---

## 🐛 Troubleshooting

### ❗ “Google Gemini API key not found”

* Ensure `.env` exists in the project root
* Make sure the API key has *no quotes or spaces*
* Restart Streamlit (`Ctrl + C` → run again)

### ❗ “Module not found: streamlit”

* Run:

  ```bash
  pip install -r requirements.txt
  ```
* Ensure you're inside the correct project directory

### ❗ “Rate limit exceeded”

* You reached your Gemini free tier limit
* Wait 60 seconds and retry

### ❗ App feels slow

* `gemini-flash-latest` is fast and cost-efficient (default)
* First run may take 10–15 seconds to initialize
* Subsequent runs are faster

---

## 🧪 Testing Without the UI

To test the entire system quickly:

```bash
python test_system.py
```

This runs the full AI pipeline and prints the output in your terminal.

---

## 📚 Need Help?

Check these files:

* `README.md` — Full project documentation
* `DEPLOYMENT.md` — Deploying to Streamlit Cloud
* `HACKATHON_PITCH.md` — Your polished presentation script