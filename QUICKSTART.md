# Quick Start Guide - CareGuide

Get up and running in 5 minutes!

## Step 1: Install Dependencies (1 min)

\`\`\`bash
pip install -r requirements.txt
\`\`\`

This installs:
- `streamlit` - Web UI framework
- `openai` - OpenAI API client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management
- Other utilities

## Step 2: Get Your OpenAI API Key (2 min)

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-` or `sk-`)

**Important:** Keep this key secret! Never commit it to GitHub.

## Step 3: Configure Environment (1 min)

\`\`\`bash
# Copy the example file
cp .env.example .env
\`\`\`

Edit `.env` and replace the placeholder:

\`\`\`env
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
\`\`\`

**Common mistakes to avoid:**
- ❌ Don't use quotes: `OPENAI_API_KEY="sk-..."`
- ❌ Don't add spaces: `OPENAI_API_KEY = sk-...`
- ✅ Correct format: `OPENAI_API_KEY=sk-proj-...`

## Step 4: Verify Setup (30 seconds)

\`\`\`bash
python check_setup.py
\`\`\`

You should see:
\`\`\`
✅ .env file exists
✅ OPENAI_API_KEY is set
✅ streamlit installed
✅ openai installed
✅ All checks passed!
\`\`\`

## Step 5: Run the App (30 seconds)

\`\`\`bash
streamlit run streamlit_app.py
\`\`\`

The app will open in your browser at `http://localhost:8501`

## What's Next?

1. **Upload a health record** - Try `data/demo_patient_record.txt`
2. **Watch the AI work** - See each agent process the data
3. **Review results** - Check your Health Engagement Score
4. **Export data** - Download JSON for further analysis

## Troubleshooting

### "OpenAI API key not found"
- Make sure `.env` file exists in the project root
- Check that the API key has no quotes or extra spaces
- Restart the Streamlit app (`Ctrl+C` then run again)

### "Module not found: streamlit"
- Run `pip install -r requirements.txt` again
- Make sure you're in the correct directory

### "Rate limit exceeded"
- You've used up your OpenAI free tier
- Wait 60 seconds and try again
- Or upgrade your OpenAI account

### App is slow
- `gpt-4o-mini` is fast and cheap (default)
- First run loads AI models (10-15 seconds)
- Subsequent runs are faster

## Testing Without UI

Want to test the system quickly?

\`\`\`bash
python test_system.py
\`\`\`

This runs the complete pipeline and prints results to terminal.

## Need Help?

Check these files:
- `README.md` - Full documentation
- `DEPLOYMENT.md` - How to deploy to Streamlit Cloud
- `HACKATHON_PITCH.md` - Your presentation script

---

**Ready to win that hackathon? Let's go! 🚀**
