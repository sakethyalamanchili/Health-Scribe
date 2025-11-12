# Deployment Guide for Project Asha

## Deploying to Streamlit Cloud

Streamlit Cloud is the easiest way to deploy your Project Asha application for the hackathon.

### Prerequisites

1. GitHub account
2. Streamlit Cloud account (free at https://streamlit.io/cloud)
3. OpenAI API key

### Step 1: Push to GitHub

\`\`\`bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit - Project Asha"

# Create repository on GitHub and push
git remote add origin https://github.com/yourusername/project-asha.git
git branch -M main
git push -u origin main
\`\`\`

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository
4. Set main file path: `streamlit_app.py`
5. Click "Advanced settings"
6. Add your secrets:

\`\`\`toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
TAVILY_API_KEY = "tvly-your-tavily-key-here"  # Optional
\`\`\`

7. Click "Deploy"

### Step 3: Wait for Deployment

Streamlit Cloud will automatically:
- Install dependencies from requirements.txt
- Build your application
- Provide a public URL

### Alternative: Local Deployment

To run locally for testing:

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run the app
streamlit run streamlit_app.py
\`\`\`

The app will open at http://localhost:8501

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `TAVILY_API_KEY` - For enhanced web search (free tier available)

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Ensure all dependencies are in requirements.txt

### Issue: "API key not found"
**Solution:** Check that secrets are correctly configured in Streamlit Cloud settings

### Issue: Slow performance
**Solution:** 
- Use `gpt-4o-mini` model (default) for faster responses
- Reduce number of recommendations being processed
- Consider caching with `@st.cache_data`

### Issue: Memory limits on Streamlit Cloud
**Solution:** Streamlit Cloud free tier has memory limits. Optimize by:
- Processing fewer activities at once
- Reducing context window size
- Using streaming responses

## Production Considerations

For production deployment beyond the hackathon:

1. **Use FastAPI Backend**: Separate frontend and backend as described in the technical report
2. **Add Database**: Store assessments in PostgreSQL or MongoDB
3. **Add Authentication**: Implement user accounts and auth
4. **HIPAA Compliance**: Use BAA-compliant hosting and APIs
5. **Add Monitoring**: Use logging and error tracking
6. **Scale Computing**: Use cloud functions or container orchestration

## Support

For hackathon support, refer to:
- README.md for project overview
- Technical report (will.ts) for architecture details
- GitHub Issues for bug reports
