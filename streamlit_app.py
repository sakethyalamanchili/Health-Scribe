"""
Streamlit Frontend for Project Asha - Health Engagement System
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import os
import utils

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
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Process Health Record", "📊 View Demo", "ℹ️ How It Works", "🔮 What-If Analysis"])
    
    with tab1:
        st.header("Upload Health Records")
        st.markdown("Upload all of your .txt health records from different doctors. Asha will unify them.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # --- THIS IS THE SIMPLIFIED UPLOADER ---
            uploaded_text_files = st.file_uploader(
                "Upload Text Files (.txt)",
                type=['txt'],
                accept_multiple_files=True
            )
            # ----------------------------------------
            
            if not uploaded_text_files:
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
        
        # --- THIS LOGIC IS NOW SIMPLIFIED ---
        if uploaded_text_files:
            st.divider()
            
            with st.expander("📝 View Uploaded Files"):
                st.markdown("**Text Files:**")
                for f in uploaded_text_files:
                    st.caption(f.name)
            
            if st.button("🚀 Analyze All Records", use_container_width=True):
                # We pass the list of text files
                process_health_record(text_files=uploaded_text_files)
    
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
        
        agents = [
            {
                "name": "1. Unifier & Summarizer Agent",
                "icon": "📝",
                "description": "Combines all text files into a single 'master record', then creates a structured summary.",
                "output": "PatientSummary model (age, sex, summaries)"
            },
            {
                "name": "2. Recommendation Agents (RAG + Web)",
                "icon": "🌐",
                "description": "Generates recommendations from both the LLM's broad knowledge and a specific USPSTF guidelines database (RAG).",
                "output": "Two lists of HealthActivityRecommendation"
            },
            {
                "name": "3. Consolidation Agent",
                "icon": "🔄",
                "description": "Uses semantic understanding to merge and deduplicate recommendations from all sources.",
                "output": "A single, clean list of unique activities"
            },
            {
                "name": "4. Self-Correcting Assessment Agent",
                "icon": "🧠",
                "description": "A 2-step loop: An 'Assessor' drafts an assessment, then a 'Validator' agent reviews it, assigns a confidence score, and corrects it if needed.",
                "output": "Final assessment with status and confidence score"
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
    
    with tab4:
        st.header("🔮 What-If Analysis")
        st.markdown("See how your Health Engagement Score changes by completing recommended tasks.")

        # This feature only works *after* a report is generated
        if not st.session_state.health_report:
            st.info("Please run an analysis on the 'Process Health Record' or 'View Demo' tab first to use this feature.")
            st.stop()
        
        # If we're here, the report exists.
        result = st.session_state.health_report
        
        # Get *only* the recommended activities
        recommended_activities = [
            a for a in result.activity_assessments 
            if a.status == HealthActivityStatus.RECOMMENDED
        ]
        
        if not recommended_activities:
            st.success("Congratulations! You have no recommended activities left to complete.")
            st.stop()

        # Create a list of names for the selectbox
        activity_names = [a.recommendation_short_str for a in recommended_activities]
        
        selected_name = st.selectbox("Select a recommended activity to simulate:", activity_names)
        
        if st.button("Simulate Completion", use_container_width=True):
            # 1. GET CURRENT DATA
            current_completed = result.completed_count
            current_total = result.total_activities
            current_needs_confirm = result.needs_confirmation_count
            current_score = result.health_engagement_score

            # 2. CALCULATE NEW SCORE (LOCAL MATH)
            new_completed_count = current_completed + 1
            new_score = utils.calculate_health_engagement_score(
                completed=new_completed_count,
                total=current_total,
                needs_confirmation=current_needs_confirm 
            )
            
            # 3. DISPLAY THE METRICS
            st.markdown("### 📈 Simulated Score")
            col1, col2 = st.columns(2)
            score_delta = new_score - current_score
            
            with col1:
                st.metric(
                    label="Current Score",
                    value=f"{current_score:.0f}/100"
                )
            with col2:
                st.metric(
                    label=f"New Score (after completing '{selected_name}')",
                    value=f"{new_score:.0f}/100",
                    delta=f"{score_delta:+.0f} points"
                )
            
            # --- 4. THIS IS THE NEW "WHY" SECTION ---
            st.markdown("---")
            st.markdown("#### 💡 Asha's Analysis")
            
            # We need the full report and summary to give the agent context
            report_json = result.model_dump_json()
            patient_summary = result.patient_summary
            
            with st.spinner("Asha is analyzing the 'why'..."):
                # Call your new What-If Analyst Agent
                analysis_text = st.session_state.orchestrator.agent_system.run_what_if_analysis_agent(
                    patient_summary=patient_summary,
                    health_report_json=report_json,
                    selected_activity_name=selected_name,
                    current_score=current_score,
                    new_score=new_score
                )
                # Display the AI's personalized text response
                st.info(analysis_text) 

            # --- 5. THIS IS THE "SHOW MATH" SECTION ---
            with st.expander("Show Detailed Score Calculation..."):
                st.markdown("#### How Your Score is Calculated")
                st.markdown(
                    "Your score is based on a formula that gives **full credit (100%)** "
                    "for 'Completed' tasks and **partial credit (50%)** for tasks that "
                    "'Need Confirmation'."
                )
                st.code(
                    "Completed_Score = (Completed_Tasks / Total_Tasks) * 100\n"
                    "Confirmation_Score = (Needs_Confirmation_Tasks / Total_Tasks) * 50\n"
                    "Final_Score = Completed_Score + Confirmation_Score",
                    language="python"
                )
                
                st.markdown("---")
                
                st.markdown("##### 1. Your Current Score Calculation")
                current_base_score = (current_completed / current_total) * 100
                current_partial_score = (current_needs_confirm / current_total) * 50
                st.markdown(
                    f"* **Completed Score:** (`{current_completed}` / `{current_total}`) * 100 = **`{current_base_score:.1f}`** points\n"
                    f"* **Confirmation Score:** (`{current_needs_confirm}` / `{current_total}`) * 50 = **`{current_partial_score:.1f}`** points\n"
                    f"* **Final Score:** `{current_base_score:.1f}` + `{current_partial_score:.1f}` = **`{current_score:.1f}`**"
                )
                
                st.markdown("---")

                st.markdown("##### 2. Your Simulated Score Calculation")
                new_base_score = (new_completed_count / current_total) * 100
                new_partial_score = (current_needs_confirm / current_total) * 50
                st.markdown(
                    f"* **Completed Score:** (`{new_completed_count}` / `{current_total}`) * 100 = **`{new_base_score:.1f}`** points\n"
                    f"* **Confirmation Score:** (`{current_needs_confirm}` / `{current_total}`) * 50 = **`{new_partial_score:.1f}`** points\n"
                    f"* **Final Score:** `{new_base_score:.1f}` + `{new_partial_score:.1f}` = **`{new_score:.1f}`**"
                )
    
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


def process_health_record(text_files):
    """Process uploaded health record through the agent pipeline"""
    
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
                st.info("Processing through 4 specialized AI agents...")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Execute the full assessment
                with st.spinner("Executing multi-agent pipeline..."):
                    # --- THIS IS THE SIMPLIFIED ORCHESTRATOR CALL ---
                    result = st.session_state.orchestrator.run_full_assessment(
                        text_files=text_files
                    )
                
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