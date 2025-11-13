"""
Streamlit Frontend for Project Asha - Health Engagement System
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv(override=True)

import config
from orchestrator import HealthAssessmentOrchestrator
from models import HealthActivityStatus


def main():
    # Check Google Gemini API key before proceeding
    if not config.GOOGLE_API_KEY:
        st.error("🚨 Google Gemini API key not found! Please set GOOGLE_API_KEY in your .env file")
        
        st.info("📝 Create a .env file in the project root with: GOOGLE_API_KEY=your-key-here")
        
        with st.expander("🔧 Quick Fix Options"):
            st.code("""
# Option 1: Create .env file
echo "GOOGLE_API_KEY=your-key-here" > .env

# Option 2: Set environment variable (Mac/Linux)
export GOOGLE_API_KEY=your-key-here
streamlit run streamlit_app.py

# Option 3: Set environment variable (Windows PowerShell)
$env:GOOGLE_API_KEY="your-key-here"
streamlit run streamlit_app.py
            """, language="bash")
        
        st.stop()
    
    # Initialize session state for chatbot and report
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "health_report" not in st.session_state:
        st.session_state.health_report = None
    if "orchestrator" not in st.session_state:
        # Create the orchestrator once and store it in session state
        st.session_state.orchestrator = HealthAssessmentOrchestrator(api_key=config.GOOGLE_API_KEY)
    
    # Page configuration
    st.set_page_config(
        page_title="Project Asha - Health Engagement",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .agent-step {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 3px solid #28a745;
        }
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            border-radius: 8px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Project Asha</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Intelligent Health Engagement System powered by Multi-Agent AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("About Project Asha")
        st.markdown("""
        **Asha** means "hope" in Sanskrit.
        
        This system uses 5 specialized AI agents to:
        - Read and understand patient health records
        - Cross-reference against medical guidelines (RAG)
        - Assess which health activities are "Completed" or "Recommended"
        - Calculate a real-time health engagement score
        - Answer your questions about your report
        
        **Technology Stack:**
        - Multi-Agent AI Architecture
        - Google Gemini 1.5 Pro
        - USPSTF Clinical Guidelines (RAG)
        - Pydantic Structured Output
        - HIPAA De-identification
        """)
        
        st.divider()
        
        st.subheader("System Status")
        st.success(f"✅ API: Connected")
        st.info(f"🤖 Model: {config.GEMINI_MODEL}")
        st.info(f"⚡ Agents: 5 Active + 1 Chatbot")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📄 Process Health Record", "📊 View Demo", "ℹ️ How It Works"])
    
    with tab1:
        st.header("Upload Health Record")
        st.markdown("Upload a patient's health record to analyze their health engagement and receive personalized recommendations.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a text file containing health records",
                type=['txt'],
                help="Upload a plain text file with health information"
            )
            
            if not uploaded_file:
                st.info("💡 Don't have a file? Click 'View Demo' tab to see a sample analysis!")
        
        with col2:
            st.markdown("**Supported Formats:**")
            st.markdown("- Clinical notes (.txt)")
            st.markdown("- Health summaries (.txt)")
            st.markdown("- EHR exports (.txt)")
            st.markdown("")
            st.markdown("**Data Privacy:**")
            st.markdown("✓ HIPAA de-identification")
            st.markdown("✓ No data storage")
            st.markdown("✓ Secure processing")
        
        if uploaded_file:
            st.divider()
            
            with st.expander("📝 View Uploaded Content"):
                content = uploaded_file.read().decode('utf-8')
                st.text_area("Health Record Content", content, height=200, disabled=True)
                uploaded_file.seek(0)  # Reset file pointer
            
            if st.button("🚀 Analyze Health Record", use_container_width=True):
                process_health_record(uploaded_file)
    
    with tab2:
        st.header("Demo Analysis")
        st.markdown("See how Project Asha processes a sample patient record through our multi-agent pipeline.")
        
        demo_file_path = Path("data/demo_patient_record.txt")
        
        if demo_file_path.exists():
            with st.expander("📄 View Demo Patient Record"):
                with open(demo_file_path, 'r') as f:
                    demo_content = f.read()
                st.text_area("Sample Health Record", demo_content, height=300, disabled=True)
            
            if st.button("🎯 Run Demo Analysis", use_container_width=True):
                with open(demo_file_path, 'r') as f:
                    process_demo(f.read())
        else:
            st.warning("Demo file not found. Please ensure data/demo_patient_record.txt exists.")
    
    with tab3:
        st.header("How It Works")
        
        st.markdown("""
        ### Multi-Agent Architecture
        
        Project Asha uses a deterministic pipeline of 5 specialized AI agents (plus a 6th for chat):
        """)
        
        # --- THIS AGENT LIST IS NOW CORRECTED TO MATCH YOUR CODE ---
        agents = [
            {
                "name": "1. Summarization Agent",
                "icon": "📝",
                "description": "Extracts demographics and conditions, creating 'basic' and 'advanced' patient summaries.",
                "output": "PatientSummary model (age, sex, summaries)"
            },
            {
                "name": "2. Web Recommendation Agent",
                "icon": "🌐",
                "description": "Generates general and condition-specific recommendations based on the LLM's broad knowledge.",
                "output": "List of HealthActivityRecommendation"
            },
            {
                "name": "3. USPSTF RAG Agent",
                "icon": "🏥",
                "description": "Performs RAG to find and format recommendations from the USPSTF guidelines database.",
                "output": "Evidence-based list of HealthActivityRecommendation"
            },
            {
                "name": "4. Consolidation Agent",
                "icon": "🔄",
                "description": "Uses semantic understanding to merge and deduplicate recommendations from all sources.",
                "output": "A single, clean list of unique activities"
            },
            {
                "name": "5. Assessment Agent (The 'Brain')",
                "icon": "🧠",
                "description": "Uses fuzzy reasoning to analyze the patient record for each activity to determine its status.",
                "output": "Assessment with status ('Completed', 'Recommended', 'Needs user confirmation')"
            }
        ]
        
        for agent in agents:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"### {agent['icon']}")
                with col2:
                    st.markdown(f"**{agent['name']}**")
                    st.markdown(agent['description'])
                    st.caption(f"Output: {agent['output']}")
                st.divider()
        
        st.markdown("""
        ### Health Engagement Score
        
        The system calculates a **gamified score (0-100)** based on:
        - Completed preventive care activities
        - Adherence to clinical guidelines
        - Temporal relevance of activities
        
        ### Why Agents?
        
        This problem is **Agentic-Mandatory** because it requires:
        - Temporal reasoning (understanding dates and recency)
        - Semantic understanding (merging "flu shot" and "influenza vaccine")
        - Evidence-based reasoning (RAG with medical guidelines)
        - Fuzzy logic assessment (interpreting partial completion)
        
        Traditional rule-based systems cannot handle these nuanced requirements.
        """)

    # ===============================================
    # == 4. REPORT DISPLAY & CHATBOT (NEW!) ==
    # ===============================================
    
    # This section only appears AFTER a report has been generated and stored in session_state
    if st.session_state.health_report:
        
        # We can now re-use the result variable
        result = st.session_state.health_report
        
        st.divider()
        st.markdown("## 📊 Health Engagement Report")
        
        # --- This is all the report display code cut from the other functions ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Health Engagement Score", f"{result.health_engagement_score:.0f}/100", 
                      help="Overall score based on completed preventive care activities")
        
        with col2:
            st.metric("Completed Activities", f"{result.completed_count}/{result.total_activities}",
                      help="Number of fully completed health activities")
        
        with col3:
            completion_rate = (result.completed_count / result.total_activities * 100) if result.total_activities > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.0f}%",
                      help="Percentage of activities marked as completed")
        
        # Activity breakdown
        st.markdown("### 📋 Activity Assessment Details")
        
        # Group by status (use the enum for reliable comparison)
        completed = [a for a in result.activity_assessments if a.status == HealthActivityStatus.COMPLETED]
        recommended = [a for a in result.activity_assessments if a.status == HealthActivityStatus.RECOMMENDED]
        needs_confirmation = [a for a in result.activity_assessments if a.status == HealthActivityStatus.NEEDS_CONFIRMATION]
        
        # Display completed activities
        if completed:
            st.markdown("#### ✅ Completed Activities")
            for activity in completed:
                with st.expander(f"✅ {activity.recommendation_short_str}"):
                    col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Category:** {activity.category}")
                    if activity.supporting_evidence:
                        st.markdown("**Evidence Found:**")
                        st.info(activity.supporting_evidence)
                
                with col2:
                    st.success(f"**Status:** {activity.status}")
                    
                    # --- THIS IS THE CRITICAL UPDATE ---
                    if activity.confidence_score:
                        st.caption(f"**AI Confidence:** {activity.confidence_score}%")
                    # ---------------------------------
                        
                    if activity.completion_date:
                        st.caption(f"Completed on: {activity.completion_date}")
        
        # Display recommended activities
        if recommended:
            st.markdown("#### 💡 Recommended Activities")
            for activity in recommended:
                with st.expander(f"💡 {activity.recommendation_short_str}"):

                    # --- THIS IS THE CRITICAL UPDATE ---
                    if activity.confidence_score:
                        st.caption(f"**AI Confidence:** {activity.confidence_score}%")

                    st.markdown(f"**Description:** {activity.recommendation_long_str}")
                    st.markdown(f"**Category:** {activity.category}")
                    st.markdown(f"**Frequency:** {activity.frequency_short_str}")
                    st.warning("This activity was not found in your health record. Consider scheduling it.")
        
        # Display activities needing confirmation
        if needs_confirmation:
            st.markdown("#### ❓ Activities Needing Confirmation")
            for activity in needs_confirmation:
                with st.expander(f"❓ {activity.recommendation_short_str}"):
                    st.markdown(f"**Description:** {activity.recommendation_long_str}")
                    st.markdown(f"**Category:** {activity.category}")

                    # --- THIS IS THE CRITICAL UPDATE ---
                    if activity.confidence_score:
                        st.caption(f"**AI Confidence:** {activity.confidence_score}%")
                    
                    if activity.user_input_questions:
                        st.markdown("**Please answer these questions to clarify:**")
                        for i, question in enumerate(activity.user_input_questions, 1):
                            st.checkbox(question, key=f"q_{activity.activity_id}_{i}")
        
        # Export option
        st.markdown("### 📥 Export Results")
        
        export_data = result.model_dump()
        
        st.download_button(
            label="📄 Download JSON Report",
            data=json.dumps(export_data, indent=2),
            file_name=f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

        # --- CHATBOT UI ---
        st.divider()
        st.markdown("## 💬 Ask Asha About Your Report")

        # Display existing chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Get new user input
        if prompt := st.chat_input("Why do I need a colonoscopy?"):
            # Add user message to history and display it
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display agent response
            with st.chat_message("assistant"):
                with st.spinner("Asha is thinking..."):
                    # Use the orchestrator stored in session state
                    response = st.session_state.orchestrator.agent_system.run_chat_agent(
                        user_question=prompt,
                        patient_summary=result.patient_summary,
                        health_report_json=result.model_dump_json() # Give agent full context
                    )
                    st.markdown(response)
            
            # Add agent response to history
            st.session_state.messages.append({"role": "assistant", "content": response})


def process_health_record(uploaded_file):
    """Process uploaded health record through the agent pipeline"""
    
    content = uploaded_file.read().decode('utf-8')
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Container for results
    with st.container():
        st.markdown("### 🤖 Multi-Agent Pipeline Execution")
        
        agent_outputs = st.expander("View Detailed Agent Outputs", expanded=True)
        
        with agent_outputs:
            try:
                status_text.text("Running multi-agent health assessment pipeline...")
                progress_bar.progress(10)
                
                st.markdown('<div class="agent-step">', unsafe_allow_html=True)
                st.markdown("**🔄 Starting Pipeline**")
                st.info("Processing through 5 specialized AI agents...")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Execute the full assessment
                with st.spinner("Executing multi-agent pipeline..."):
                    # Use the orchestrator from session state
                    result = st.session_state.orchestrator.run_full_assessment(patient_record_text=content)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis Complete!")
                
                # Store report in session state to trigger display
                st.session_state.health_report = result
                # Clear previous chat history
                st.session_state.messages = [] 
                
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")
                st.exception(e)
                return


def process_demo(demo_content: str):
    """Process demo patient record"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.container():
        st.markdown("### 🤖 Demo Pipeline Execution")
        
        try:
            status_text.text("Running multi-agent pipeline...")
            progress_bar.progress(50)
            
            with st.spinner("Executing multi-agent pipeline..."):
                # Use the orchestrator from session state
                result = st.session_state.orchestrator.run_full_assessment(patient_record_text=demo_content)
            
            progress_bar.progress(100)
            status_text.text("✅ Demo Analysis Complete!")
            
            # Store report in session state to trigger display
            st.session_state.health_report = result
            # Clear previous chat history
            st.session_state.messages = []

        except Exception as e:
            st.error(f"Error during demo execution: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()