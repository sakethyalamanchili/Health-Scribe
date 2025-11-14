"""
Streamlit Frontend for CareGuide - Health Engagement System
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


def get_urgency_emoji(urgency: str) -> str:
    """Returns a color-coded emoji for the urgency level."""
    if urgency == "High":
        return "🔴"  # Urgent
    if urgency == "Medium":
        return "🟡"  # Soon
    if urgency == "Low":
        return "🟢"  # Routine
    return "⚪"  # Default


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
        page_title="CareGuide - Health Engagement",
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
    st.markdown('<h1 class="main-header">🏥 CareGuide</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Intelligent Health Engagement System powered by Multi-Agent AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("About CareGuide")
        
        st.warning(
            """
            **Disclaimer: Human-in-Charge**
            
            This project's output is **not a diagnosis**; it is an **audit**.
            
            It's a smart assistant that helps you find what's in your own files and
            compares it to a checklist. The documents you upload are the "ground truth,"
            and this output is the AI's analysis of that truth.
            
            **Always consult a human medical professional for medical advice.**
            """
        )
        
        st.markdown("""
        "This system uses a team of specialized AI agents to unify and audit your health records, creating a single, prioritized checklist."
        
        This system uses a team of specialized AI agents to:
        - Unify multiple, fragmented health records (.txt files)
        - Cross-reference against medical guidelines (RAG)
        - **Prioritize** tasks by medical urgency (🔴 High, 🟡 Medium, 🟢 Low)
        - **Self-correct** its own assessments with a confidence score
        - Answer your questions about your report
        
        **Technology Stack:**
        - Multi-Agent AI Architecture
        - Google Gemini 1.5 Pro
        - Agentic Self-Correction Loop
        - USPSTF Clinical Guidelines (RAG)
        - HIPAA De-identification
        """)
        
        st.divider()
        
        st.subheader("System Status")
        st.success(f"✅ API: Connected")
        st.info(f"🤖 Model: {config.GEMINI_MODEL}")
        st.info(f"⚡ Agents: 5 Active + 2 Chatbots")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Process Health Record", "📊 View Demo", "ℹ️ How It Works", "🔮 What-If Analysis"])
    
    with tab1:
        st.header("Upload Health Records")
        st.markdown("Upload all of your health records from different doctors. CareGuide will unify them.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # --- THIS IS THE SIMPLIFIED UPLOADER ---
            uploaded_text_files = st.file_uploader(
                "Upload Text Files ",
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
        st.markdown("See how CareGuide processes a sample patient record through our multi-agent pipeline.")
        
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
        
        Project CareGuide uses a deterministic pipeline of specialized AI agents:
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
                "description": "A 2-step loop: An 'Assessor' drafts an assessment, then a 'Validator' agent reviews it, assigns a confidence score, **prioritizes it (🔴/🟡/🟢)**, and corrects it if needed.",
                "output": "Final assessment with status, confidence, and urgency"
            },
            {
                "name": "5. Conversational & Analyst Agents",
                "icon": "💬",
                "description": "A team of agents that answer user questions about the report and analyze 'What-If' scenarios.",
                "output": "Natural language explanations"
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
        ### Why Agents?
        
        This problem is **Agentic-Mandatory** because it requires:
        - **Clinical Prioritization:** Reasoning about medical urgency.
        - **Self-Correction:** An agent must review and validate its own "fuzzy" assessments.
        - **Semantic Understanding:** Merging "flu shot" and "influenza vaccine".
        - **Evidence-Based Reasoning:** RAG with medical guidelines.
        
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

        # --- NEW: Sort activities by urgency for the dropdown ---
        recommended_activities.sort(key=lambda x: (x.urgency == 'High', x.urgency == 'Medium'), reverse=True)
        activity_names = [f"{get_urgency_emoji(a.urgency)} {a.recommendation_short_str} ({a.urgency} Urgency)" for a in recommended_activities]
        
        selected_display_name = st.selectbox("Select a recommended activity to simulate:", activity_names)
        
        # Find the original activity name
        selected_name = selected_display_name.split(" ", 1)[1].rsplit(" (", 1)[0]
        
        # Find the activity object
        selected_activity = next(
            a for a in recommended_activities if a.recommendation_short_str == selected_name
        )

        if st.button("Simulate Completion", use_container_width=True):
            # 1. GET CURRENT DATA
            current_score = result.health_engagement_score

            # 2. CREATE A HYPOTHETICAL LIST OF ASSESSMENTS
            hypothetical_assessments = []
            for a in result.activity_assessments:
                if a.activity_id == selected_activity.activity_id:
                    # Create a copy and "complete" it
                    new_a = a.model_copy()
                    new_a.status = HealthActivityStatus.COMPLETED
                    hypothetical_assessments.append(new_a)
                else:
                    hypothetical_assessments.append(a)
            
            # 3. CALCULATE NEW SCORE (using the new WEIGHTED function)
            new_score_data = utils.calculate_weighted_health_engagement_score(hypothetical_assessments)
            new_score = new_score_data["score"]

            # 4. DISPLAY THE METRICS
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
                    delta=f"{score_delta:+.1f} points"
                )
            
            # 5. CALL THE "WHY" AGENT (AGENT 7)
            st.markdown("---")
            st.markdown("#### 💡 CareGuide's Analysis")
            
            report_json = result.model_dump_json()
            patient_summary = result.patient_summary
            
            with st.spinner("CareGuide is analyzing the 'why'..."):
                # Call your new What-If Analyst Agent
                analysis_text = st.session_state.orchestrator.agent_system.run_what_if_analysis_agent(
                    patient_summary=patient_summary,
                    health_report_json=report_json,
                    selected_activity_name=selected_name,
                    current_score=current_score,
                    new_score=new_score
                )
                st.info(analysis_text) 

            # 6. SHOW THE DETAILED MATH
            with st.expander("Show Detailed Score Calculation..."):
                st.markdown("#### How Your Score is Calculated")
                st.markdown(
                    "Your score is weighted by urgency: **🔴 High = 3 pts**, **🟡 Medium = 2 pts**, **🟢 Low = 1 pt**. "
                    "'Needs Confirmation' tasks get 50% credit."
                )
                st.code(
                    "Earned_Points = (Completed_Points) + (Confirmation_Points * 0.5)\n"
                    "Final_Score = (Earned_Points / Total_Possible_Points) * 100",
                    language="python"
                )
                
                st.markdown("---")
                
                st.markdown("##### 1. Your Current Score Calculation")
                current_score_data = utils.calculate_weighted_health_engagement_score(result.activity_assessments)
                st.markdown(
                    f"* **Points Earned:** `{current_score_data['earned_points']:.1f}`\n"
                    f"* **Total Possible:** `{current_score_data['total_possible']}`\n"
                    f"* **Final Score:** (`{current_score_data['earned_points']:.1f}` / `{current_score_data['total_possible']}`) * 100 = **`{current_score_data['score']:.1f}`**"
                )
                
                st.markdown("---")

                st.markdown("##### 2. Your Simulated Score Calculation")
                st.markdown(
                    f"* **Points Earned:** `{new_score_data['earned_points']:.1f}`\n"
                    f"* **Total Possible:** `{new_score_data['total_possible']}`\n"
                    f"* **Final Score:** (`{new_score_data['earned_points']:.1f}` / `{new_score_data['total_possible']}`) * 100 = **`{new_score_data['score']:.1f}`**"
                )
                
                st.markdown("---")
                
                st.markdown("#### Why Your Score Changed (The Math)")
                st.success(
                    f"By completing '{selected_name}' (a **{selected_activity.urgency}-urgency** task), "
                    f"you earned **{new_score_data['earned_points'] - current_score_data['earned_points']:.1f}** more points, "
                    f"boosting your total score."
                )
    
    # ===============================================
    # == 4. REPORT DISPLAY & CHATBOT ==
    # ===============================================
    
    # This section only appears AFTER a report has been generated and stored in session_state
    if st.session_state.health_report:
        
        # We can now re-use the result variable
        result = st.session_state.health_report
        
        st.divider()
        st.markdown("## 📊 Health Engagement Report")
        
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
        st.caption("Activities are automatically prioritized by urgency: 🔴 Urgent, 🟡 Soon, 🟢 Routine")
        
        # Group by status (use the enum for reliable comparison)
        completed = [a for a in result.activity_assessments if a.status == HealthActivityStatus.COMPLETED]
        recommended = [a for a in result.activity_assessments if a.status == HealthActivityStatus.RECOMMENDED]
        needs_confirmation = [a for a in result.activity_assessments if a.status == HealthActivityStatus.NEEDS_CONFIRMATION]

        # --- NEW: Sort all lists by urgency ---
        completed.sort(key=lambda x: (x.urgency == 'High', x.urgency == 'Medium'), reverse=True)
        recommended.sort(key=lambda x: (x.urgency == 'High', x.urgency == 'Medium'), reverse=True)
        needs_confirmation.sort(key=lambda x: (x.urgency == 'High', x.urgency == 'Medium'), reverse=True)

        
        # Display completed activities
        if completed:
            st.markdown("#### ✅ Completed Activities")
            for activity in completed:
                # --- THIS IS THE CRITICAL UPDATE (Urgency Emoji) ---
                emoji = get_urgency_emoji(activity.urgency)
                with st.expander(f"✅ {emoji} {activity.recommendation_short_str}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Category:** {activity.category}")
                        if activity.supporting_evidence:
                            st.markdown("**Evidence Found:**")
                            st.info(activity.supporting_evidence)
                    
                    with col2:
                        st.success(f"**Status:** {activity.status}")
                        st.caption(f"**Urgency:** {activity.urgency}") # <-- Show text
                        if activity.confidence_score:
                            st.caption(f"**AI Confidence:** {activity.confidence_score}%")
                        if activity.completion_date:
                            st.caption(f"Completed on: {activity.completion_date}")
        
        # Display recommended activities
        if recommended:
            st.markdown("#### 💡 Recommended Activities")
            for activity in recommended:
                emoji = get_urgency_emoji(activity.urgency)
                with st.expander(f"💡 {emoji} {activity.recommendation_short_str}"):
                    st.caption(f"**Urgency:** {activity.urgency}") # <-- Show text
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
                emoji = get_urgency_emoji(activity.urgency)
                with st.expander(f"❓ {emoji} {activity.recommendation_short_str}"):
                    st.markdown(f"**Description:** {activity.recommendation_long_str}")
                    st.markdown(f"**Category:** {activity.category}")
                    st.caption(f"**Urgency:** {activity.urgency}") # <-- Show text
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
        st.markdown("## 💬 Ask CareGuide About Your Report")

        # 1. Display ALL messages from session state
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 2. Check for new user input
        if prompt := st.chat_input("Why do I need a colonoscopy?"):
            
            # 3. Add the user's new message to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # 4. Call the AI agent to get a response
            with st.spinner("CareGuide is thinking..."):
                response = st.session_state.orchestrator.agent_system.run_chat_agent(
                    user_question=prompt,
                    patient_summary=result.patient_summary,
                    health_report_json=result.model_dump_json() # Give agent full context
                )
            
            # 5. Add the AI's response to state
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 6. Force a re-run from the top
            # This will clear the input box and run the "Display ALL messages"
            # loop (step 1) to render the new Q&A
            st.rerun()


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