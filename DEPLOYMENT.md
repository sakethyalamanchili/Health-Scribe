````markdown
# Deployment Guide for CareGuide

This guide explains how to deploy **CareGuide** to **Streamlit Cloud** for your hackathon demo.

---

## 🚀 Deploying to Streamlit Cloud

Streamlit Cloud is the easiest and fastest way to deploy CareGuide without managing servers.

---

## ✅ Prerequisites

Make sure you have:

1. A **GitHub** account  
2. A **Streamlit Cloud** account  
   → https://streamlit.io/cloud  
3. A **Google Gemini API Key**

---

## 📤 Step 1: Push Code to GitHub

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit - CareGuide"

# Add GitHub repo and push
git remote add origin https://github.com/yourusername/CareGuide.git
git branch -M main
git push -u origin main
````

Make sure your repo includes:

* `streamlit_app.py`
* `requirements.txt`
* `.env.example`
* `data/uspstf_guidelines.json`
* All agent, model, and orchestrator files

---

## 🌐 Step 2: Deploy on Streamlit Cloud

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click **“New app”**
3. Select your **CareGuide GitHub repository**
4. Set **Main file path** →

   ```
   streamlit_app.py
   ```
5. Open **Advanced settings**
6. Add your secrets:

```toml
GOOGLE_API_KEY = "YOUR-ACTUAL-GEMINI-KEY-HERE"
```

7. Click **Deploy**

---

## ⏳ Step 3: Wait for Deployment

Streamlit Cloud will automatically:

* Install dependencies from `requirements.txt`
* Build your CareGuide application
* Host it on a **public URL**
* Restart automatically when you push updates

---

## 💻 Alternative: Run Locally

If you want to test before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Copy env template
cp .env.example .env
# Edit .env with your real API key

# Run Streamlit
streamlit run streamlit_app.py
```

Your app opens at:

```
http://localhost:8501
```

---

## 🔐 Environment Variables

Required:

* `GOOGLE_API_KEY` — Your Gemini API key

**Note:** Use Streamlit Cloud **Secrets Manager** (never push `.env` to GitHub).

---

## 🐛 Troubleshooting

### ❗ Issue: "Module not found"

**Solution:**
Ensure all dependencies are listed in `requirements.txt`.

---

### ❗ Issue: "API key not found"

**Solution:**
Verify that `GOOGLE_API_KEY` is correctly added in:

**Streamlit Cloud → App Settings → Secrets**

---

### ❗ Issue: Slow performance

**Solutions:**

* Use `gemini-flash-latest` (fastest + cheapest)
* Add caching:

```python
@st.cache_data
def load_data():
    ...
```

---

### ❗ Issue: Memory limits on Streamlit Cloud

Streamlit free tier has modest RAM.

**Optimizations:**

* Process fewer activities at once
* Reduce prompt size before sending to the API
* Avoid large file uploads

---

## 🏭 Production-Level Considerations

For post-hackathon real-world deployment:

1. **Add a FastAPI backend**
   Separate UI (Streamlit) from agent pipeline.

2. **Use a Database**
   Store patient histories, generated scores, and logs.

3. **Add Authentication**
   OAuth, Firebase Auth, or Auth0.

4. **HIPAA-Compliant Hosting**
   Use cloud providers offering BAAs.

5. **Monitoring & Error Tracking**
   Add structured logs and Sentry-style reporting.

---

## 🔧 Support

Helpful project files:

* **README.md** — Full documentation
* **HACKATHON_PITCH.md** — Your demo script
* **DEPLOYMENT.md** — This file
* **GitHub Issues** — Report problems

---

Deployment is now complete — you're ready to demo **CareGuide**! 🚀

```