# **CareGuide – AI Health Engagement System**

## 🏆 Agentic AI Hackathon Submission

**CareGuide** is an intelligent health-engagement system that transforms fragmented patient health records into actionable and personalized care plans. Built with a deterministic multi-agent architecture, it demonstrates production-ready AI that is reliable, compliant, and trustworthy.

---

## 🎯 Problem Statement

### **The $4.9 Trillion U.S. Healthcare Crisis**

* 42% of U.S. adults manage multiple chronic conditions.
* Health data is scattered across incompatible EHR systems.
* Patients become accidental “data integrators,” leading to:

  * Medical errors
  * Missed preventive screenings
  * Delayed or incorrect treatments

### **Our Solution**

**CareGuide** automatically integrates patient data, analyzes complete health histories, and generates a **Health Engagement Score** — a gamified metric showing what health actions the patient should take next.

---

## 🧠 Architecture: The “AI Assembly Line”

Unlike unpredictable single-agent systems, CareGuide uses a **Deterministic Multi-Agent Pipeline**:

1. **De-Identification Agent** – Removes PHI to meet HIPAA Safe Harbor standards
2. **Summarization Agents** – Generate both basic and advanced summaries
3. **Recommendation Agents** – Provide health actions using Web + USPSTF RAG
4. **Consolidation Agent** – Performs semantic deduplication
5. **Assessment Agent** – Uses fuzzy reasoning to detect evidence in patient records

---

## 🛡️ Trust & Safety Layers

1. **Compliance Guardrail** – HIPAA-aligned de-identification
2. **Hallucination Guardrail** – RAG system grounded in USPSTF guidelines
3. **Human-in-the-Loop** – Intelligent follow-up questions when data is missing

---

## 🚀 Quick Start

### **Prerequisites**

* Python **3.9+**
* Google Gemini API key *(Get one at Google AI Studio)*

### **Installation**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create environment variables
cp .env.example .env

# 3. Add your Gemini API key in the .env file
```

### **Verify Setup**

```bash
python check_setup.py
```

This checks:

* `.env` file exists
* `GOOGLE_API_KEY` is configured
* Dependencies installed
* Sample data available

### **Run the Application**

```bash
streamlit run streamlit_app.py
```

Or use convenience scripts:

```bash
# Unix / Mac / Linux
./run_local.sh

# Windows
./run_local.ps1
```

---

## 📊 How CareGuide Works

1. **Upload** your health record (text format)
2. **AI Pipeline** processes it using the agent architecture
3. **Dashboard** shows your Health Engagement Score
4. **Action Items** include completed and recommended activities
5. **User Confirmation** refines your health profile

---

## 🎓 Why This Project Wins

* **Agentic-First Design** – Uses multi-agent chaining to solve complex tasks
* **Production-Ready** – Pydantic validation, error handling, modular design
* **Clinically Grounded** – USPSTF evidence-based guidelines
* **HIPAA-Aware Architecture** – De-identification from day one
* **Real Impact** – Solves a massive healthcare accessibility and engagement gap

---

## 📁 Project Structure

```
CareGuide/
├── streamlit_app.py            # Streamlit UI
├── orchestrator.py             # Pipeline coordinator
├── agents.py                   # All AI agents
├── models.py                   # Pydantic data models
├── config.py                   # Config & settings
├── utils.py                    # Utility functions
├── check_setup.py              # Setup verification
├── test_system.py              # Full pipeline test
├── data/
│   ├── demo_patient_record.txt
│   └── uspstf_guidelines.json
├── output/                     # Generated assessments
├── requirements.txt
├── .env                        # API keys (user-created)
└── .env.example                # Template
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key
```

---

## 🧪 Testing

Run the full system pipeline without the UI:

```bash
python test_system.py
```

---

## 🚀 Deployment

### **Deploy on Streamlit Cloud**

1. Push repo to GitHub
2. Open **share.streamlit.io**
3. Connect your repository
4. Add `GOOGLE_API_KEY` in **Secrets**
5. Deploy

---

## 💡 Demo Tips for the Hackathon

1. Start with the **$4.9T healthcare problem**
2. Upload the sample patient record
3. Walk through each agent’s role
4. Highlight trust layers (HIPAA + RAG + HITL)
5. Display the **Health Engagement Score**
6. Export the structured JSON output

---

## 🐛 Troubleshooting

**API key not found**

* Check `.env`
* Run `python check_setup.py`
* Ensure no quotes around the key
* Restart Streamlit

**Module not found**

* Run `pip install -r requirements.txt`
* Use Python 3.9+

**Rate limits**

* Retry after a few seconds
* Google’s free tier usually handles typical usage

---

## 📝 License

MIT License – Built for hackathon and educational purposes.

---

## 👥 Team

Built with passion for the **Agentic AI Hackathon**.
