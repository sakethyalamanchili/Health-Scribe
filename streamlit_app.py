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


# --- HELPER FUNCTION FOR RISK STRATIFICATION ---
def get_urgency_emoji(urgency: str) -> str:
    """Returns a color-coded emoji for the urgency level."""
    if urgency == "High":
        return "🔴"  # Urgent
    if urgency == "Medium":
        return "🟡"  # Soon
    if urgency == "Low":
        return "🟢"  # Routine
    return "⚪"  # Default


def show_acknowledgment_page():
    """
    Displays the acknowledgment and disclaimer page.
    This is the "front door" of the app.
    """
    st.markdown('<h1 class="main-header">🏥 Welcome to CareGuide</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Intelligent Health Auditor & Guide</p>', unsafe_allow_html=True)
    
    st.divider()

    st.markdown("### Before You Begin: Please Acknowledge")
    
    # This is the "Human-in-Charge" disclaimer you wrote.
    st.info(
        """
        **CareGuide is an intelligent health auditor, not a doctor.**
        
        This application is a smart assistant. Its purpose is to help you find
        what's in your own files and compare it to a checklist. The goal is to
        empower you with organized information.

        - This project's output is **not a diagnosis**.
        - The documents you upload are the "ground truth."
        - The output generated is the AI's *analysis* of that truth.

        **You must always consult a human medical professional for medical advice.**
        """
    )
    
    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("I Understand and Agree", use_container_width=True):
            st.session_state.agreed_to_terms = True
            st.rerun()
            
    with col2:
        if st.button("I Do Not Agree", use_container_width=True):
            st.session_state.show_disagree_message = True

    if "show_disagree_message" in st.session_state and st.session_state.show_disagree_message:
        st.warning(
            "That's perfectly fine. CareGuide is here to provide an easy-to-understand "
            "audit of your records. If you change your mind and are interested in "
            "making your health information easier to navigate, simply refresh the page and agree to the terms to get started."
        )


def run_careguide_app():
    """
    This function contains your ENTIRE main application (the sidebar, tabs, etc.)
    It only runs *after* the user has agreed to the terms.
    """
    
    # Check Google Gemini API key before proceeding
    if not config.GOOGLE_API_KEY:
        st.error("🚨 Google Gemini API key not found! Please set GOOGLE_API_KEY in your .env file")
        
        st.info("📝 Create a .env file in the project root with: GOOGLE_API_KEY=your-key-here")
        
        with st.expander("🔧 Quick Fix Options"):
            st.code("""
# Option 1: Create .env file
echo "GOOGLE_API_KEY=your-key-here" > .env
# ... (rest of the help text) ...
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
    
    # Header
    st.markdown('<h1 class="main-header">🏥 CareGuide</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Intelligent Health Auditor & Guide</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("About CareGuide")
        
        # --- THIS IS YOUR DISCLAIMER (MOVED FROM HERE) ---
        # We moved the main disclaimer to the acknowledgment page.
        # We can keep a smaller one here.
        st.warning(
            """
            **Disclaimer:** This is an AI-powered auditor, not a doctor.
            Always consult a medical professional for advice.
            """
        )

        st.markdown(
            "This system uses a team of specialized AI agents to unify and "
            "audit your health records, creating a single, prioritized checklist."
        )
        
        st.divider()
        
        st.subheader("System Status")
        st.success(f"✅ API: Connected")
        st.info(f"🤖 Model: {config.GEMINI_MODEL}")
        st.info(f"⚡ Agents: 6 Active + 2 Chatbots") # <-- Updated agent count
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Process Health Record", "📊 View Demo", "ℹ️ How It Works", "🔮 What-If Analysis"])
    
    with tab1:
        st.header("Upload Health Records")
        st.markdown("Upload all of your .txt health records from different doctors. CareGuide will unify them.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_text_files = st.file_uploader(
                "Upload Text Files (.txt)",
                type=['txt'],
                accept_multiple_files=True
            )
            
            if not uploaded_text_files:
                st.info("💡 Don't have a file? Click 'View Demo' tab to see a sample analysis!")
        
        with col2:
            st.markdown("**Supported Formats:**")
            st.markdown("- Clinical notes")
            st.markdown("- Health summaries")
            st.markdown("- EHR exports")
            st.markdown("")
            st.markdown("**Data Privacy:**")
            st.markdown("✓ HIPAA de-identification")
            st.markdown("✓ No data storage")
            st.markdown("✓ Secure processing")
        
        if uploaded_text_files:
            st.divider()
            
            with st.expander("📝 View Uploaded Files"):
                st.markdown("**Text Files:**")
                for f in uploaded_text_files:
                    st.caption(f.name)
            
            if st.button("🚀 Analyze All Records", use_container_width=True):
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
        
        CareGuide uses a deterministic pipeline of specialized AI agents:
        """)
        
        agents = [
            {
                "name": "1. Ingestion & De-Identification (Utility Steps)",
                "icon": "🛡️",
                "description": "Non-AI steps. Merges all files and uses RegEx to strip 18 types of PHI (HIPAA Safe Harbor) *before* any AI calls.",
                "output": "A single, de-identified master health record"
            },
            {
                "name": "2. Core Analysis (Agents 1-3)",
                "icon": "📝",
                "description": "A team of 3 agents: Summarizer, Trend Analyst, and Medication Auditor build the core patient profile.",
                "output": "Structured models for Summary, Trends, and Meds"
            },
            {
                "name": "3. Recommendation (Agents 4-5)",
                "icon": "🌐",
                "description": "Two agents (Web + RAG) gather recommendations from LLM knowledge and the USPSTF guidelines database.",
                "output": "Multiple lists of recommendations"
            },
            {
                "name": "4. Consolidation (Agent 6)",
                "icon": "🔄",
                "description": "A semantic agent that merges and deduplicates all recommendations into one unique, master list.",
                "output": "A single, clean list of unique activities"
            },
            {
                "name": "5. Assessment (Agent 7)",
                "icon": "🧠",
                "description": "A 2-step (Assess + Validate) loop that scans the record for evidence and assigns an urgency (🔴/🟡/🟢) to each activity.",
                "output": "Final assessment with status, confidence, and urgency"
            },
            {
                "name": "6. Scoring & Assembly (Utility Steps)",
                "icon": "📊",
                "description": "Non-AI steps. Calculates the final weighted score (0-100) and assembles the complete, final report.",
                "output": "The final HealthAssessmentOutput object"
            },
            {
                "name": "7. Interactive Layer (Agents 8-9)",
                "icon": "💬",
                "description": "Two agents that power the UI: The 'Conversational Agent' (for chat) and the 'What-If Analyst' (for simulations).",
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
        - **Pharmaceutical Knowledge:** Auditing complex drug interactions.
        - **Clinical Prioritization:** Reasoning about medical urgency.
        - **Self-Correction:** An agent must review and validate its own "fuzzy" assessments.
        - **Semantic Understanding:** Merging "flu shot" and "influenza vaccine".
        - **Evidence-Based Reasoning:** RAG with medical guidelines.
        
        Traditional rule-based systems cannot handle these nuanced requirements.
        """)
    
    with tab4:
        st.header("What-If Analysis")
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
    # == 5. REPORT DISPLAY & CHATBOT ==
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
                        help="Overall score based on weighted urgency of completed tasks")
        
        with col2:
            st.metric("Completed Activities", f"{result.completed_count}/{result.total_activities}",
                        help="Number of fully completed health activities")
        
        with col3:
            completion_rate = (result.completed_count / result.total_activities * 100) if result.total_activities > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.0f}%",
                        help="Percentage of activities marked as completed")
        
        # --- NEW: DISPLAY CHRONIC DISEASE TRENDS ---
        if result.disease_trends:
            st.markdown("### 📈 Chronic Disease Trends")
            
            # Create columns based on the number of trends found
            cols = st.columns(len(result.disease_trends))
            
            for i, trend in enumerate(result.disease_trends):
                with cols[i]:
                    st.metric(label=f"{trend.metric_name} Trend", value=trend.trend)
                    st.caption(trend.analysis)
                    # Show the data points in an expander
                    with st.expander("Show Data Points"):
                        for dp in trend.data_points:
                            st.markdown(f"- `{dp}`")
            st.divider()
        # -----------------------------------------------

        # --- NEW: DISPLAY MEDICATION AUDIT ---
        if result.medication_analysis_list:
            st.markdown("### 💊 Medication Audit")
            st.caption("The AI auditor has flagged potential items to discuss with your doctor. **Do not stop or change any medication without medical advice.**")
            
            # Sort by urgency
            meds_sorted = sorted(result.medication_analysis_list, key=lambda x: (x.urgency == 'High', x.urgency == 'Medium'), reverse=True)

            for med_issue in meds_sorted:
                emoji = get_urgency_emoji(med_issue.urgency)
                with st.expander(f"{emoji} **{med_issue.medication_name}** (Issue: {med_issue.analysis_type})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Explanation:** {med_issue.explanation}")
                        if med_issue.supporting_evidence:
                            st.markdown("**Evidence:**")
                            st.code(med_issue.supporting_evidence, language="json")
                    with col2:
                        if med_issue.urgency == "High":
                            st.error(f"**Urgency:** {med_issue.urgency}")
                        elif med_issue.urgency == "Medium":
                            st.warning(f"**Urgency:** {med_issue.urgency}")
                        else:
                            st.info(f"**Urgency:** {med_issue.urgency}")
            st.divider()
        # -----------------------------------------------
        
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
                        st.caption(f"**Urgency:** {activity.urgency}") 
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
                    st.caption(f"**Urgency:** {activity.urgency}") 
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
                    st.caption(f"**Urgency:** {activity.urgency}")
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

        # Display existing chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 2. Check for new user input
        if prompt := st.chat_input("Why do I need a colonoscopy?"):
            
            # 3. Add the user's new message to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # 4. Call the AI agent to get a response
            with st.chat_message("assistant"):
                with st.spinner("CareGuide is thinking..."):
                    response = st.session_state.orchestrator.agent_system.run_chat_agent(
                        user_question=prompt,
                        patient_summary=result.patient_summary,
                        health_report_json=result.model_dump_json() # Give agent full context
                    )
                    st.markdown(response)
            
            # 5. Add the AI's response to state
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 6. Force a re-run from the top
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
        
        st.rerun()  # <-- ADD THIS LINE


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

    st.rerun()  # <-- ADD THIS LINE


# --- NEW "GATEKEEPER" MAIN FUNCTION ---
def main():
    """
    This is the main "gatekeeper" function.
    It checks if the user has agreed to the terms.
    If not, it shows the acknowledgment page.
    If yes, it runs the full CareGuide app.
    """
    
    # Page config must be the first Streamlit command
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
        /* ... (rest of your CSS) ... */
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
    
    # Initialize session state for agreement
    if "agreed_to_terms" not in st.session_state:
        st.session_state.agreed_to_terms = False

    # Check the agreement
    if st.session_state.agreed_to_terms:
        # If they agreed, run the full app
        run_careguide_app()
    else:
        # If they haven't agreed, show the acknowledgment page
        show_acknowledgment_page()


if __name__ == "__main__":
    main()