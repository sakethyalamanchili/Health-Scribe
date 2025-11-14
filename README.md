# CareGuide - AI Health Engagement System

## 🏆 Agentic AI Hackathon Submission

**CareGuide** is an intelligent health engagement system that transforms fragmented patient health records into actionable, personalized care plans. Built with a deterministic multi-agent architecture, it demonstrates production-ready AI that is reliable, compliant, and trustworthy.

## 🎯 The Problem We Solve

**The $4.9 Trillion Crisis:** 42% of U.S. adults manage multiple chronic conditions, with health data scattered across incompatible systems. Patients become human data integrators, leading to medical errors and delayed care.

**Our Solution:** CareGuide automates patient data integration, analyzes complete health histories, and generates a "Health Engagement Score" - a gamified metric showing exactly what health actions to take next.

## 🏗️ Architecture: The "AI Assembly Line"

Unlike unpredictable single-agent systems, CareGuide uses a **Deterministic Multi-Agent Pipeline** with specialized agents:

1. **De-identification Agent** - HIPAA-compliant PHI removal
2. **Summarization Agents** - Basic & advanced patient summaries
3. **Recommendation Agents** - Multi-source health advice (Web + USPSTF RAG)
4. **Consolidation Agent** - Semantic deduplication with ML
5. **Assessment Agent** - Fuzzy reasoning to find evidence in patient records

## 🛡️ Three Layers of Trust

1. **Compliance Guardrail** - HIPAA Safe Harbor de-identification
2. **Hallucination Guardrail** - RAG with USPSTF guidelines database
3. **Human-in-the-Loop** - Smart questions when data is missing

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

\`\`\`bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env

# 3. Edit .env and add your Google Gemini API key
# Replace 'your_google_gemini_api_key_here' with your actual API key
\`\`\`

### Verify Setup

\`\`\`bash
# Check if everything is configured correctly
python check_setup.py
\`\`\`

This will verify:
- ✅ .env file exists
- ✅ GOOGLE_API_KEY is set correctly
- ✅ All dependencies are installed
- ✅ Sample data files are present

### Run the Application

\`\`\`bash
# Start the Streamlit app
streamlit run streamlit_app.py
\`\`\`

Or use the convenience scripts:
\`\`\`bash
# Unix/Mac/Linux
./run_local.sh

# Windows
./run_local.ps1
\`\`\`

## 📊 How It Works

1. **Upload** your health record (text file)
2. **AI Analysis** - Multi-agent pipeline processes your data
3. **Dashboard** - See your Health Engagement Score
4. **Action Items** - View completed activities and recommendations
5. **Confirm** - Answer questions to complete your health profile

## 🎓 Why This Wins

- **Agentic-Mandatory Design** - Solves tasks impossible for traditional code
- **Production-Ready** - Pydantic validation, error handling, scalability
- **Clinically Grounded** - Uses official USPSTF guidelines
- **HIPAA-Aware** - Built-in compliance from day one
- **Real Impact** - Addresses a $4.9T healthcare problem

## 📁 Project Structure

\`\`\`
CareGuide/
├── streamlit_app.py          # Main Streamlit UI
├── orchestrator.py           # Pipeline coordinator
├── agents.py                 # All AI agent implementations
├── models.py                 # Pydantic data models
├── config.py                 # Configuration settings
├── utils.py                  # Utility functions
├── check_setup.py           # Setup verification script
├── test_system.py           # Test the entire pipeline
├── data/
│   ├── demo_patient_record.txt    # Sample patient data
│   └── uspstf_guidelines.json     # Medical guidelines
├── output/                   # Generated assessments
├── requirements.txt
├── .env                      # Your API keys (create from .env.example)
├── .env.example             # Template for environment variables
└── README.md
\`\`\`

## 🔑 Environment Variables

Create a `.env` file with:

\`\`\`env
# Required
GOOGLE_API_KEY=your-actual-gemini-key-here
\`\`\`

## 🧪 Testing

Test the entire system without the UI:

\`\`\`bash
python test_system.py
\`\`\`

This runs a complete assessment using the sample patient record and displays results.

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `GOOGLE_API_KEY` in Secrets (Streamlit Cloud dashboard)
5. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 💡 Demo Tips

For your hackathon presentation:

1. **Start with the problem** - Show the $4.9T crisis slide
2. **Upload sample record** - Use `data/demo_patient_record.txt`
3. **Showcase agents** - Explain each agent as it processes
4. **Highlight trust layers** - HIPAA, RAG, human-in-loop
5. **Show the score** - Gamification drives engagement
6. **Export JSON** - Production-ready structured output

See [HACKATHON_PITCH.md](HACKATHON_PITCH.md) for your complete pitch script.

## 🐛 Troubleshooting

**"Google Gemini API key not found"**
- Run `python check_setup.py` to diagnose
- Ensure `.env` file exists and has `GOOGLE_API_KEY=your-key`
- Make sure there are NO quotes around the API key
- Restart the Streamlit app after editing `.env`

**"Module not found"**
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.9+

**"Rate limit error"**
- You've hit Google's API rate limit
- Wait a few seconds and try again
- Google Gemini has generous free tier limits

## 📝 License

MIT License - Built for educational hackathon purposes

## 👥 Team

Built with passion for the Agentic AI Hackathon

---

**Note:** This is a demonstration system. Always consult healthcare professionals for medical decisions.
