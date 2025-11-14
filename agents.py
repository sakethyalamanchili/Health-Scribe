"""
AI Agents for CareGuide - Multi-Agent Health Engagement System
Each agent is specialized for a specific task in the pipeline
"""

import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import config
from models import (
    PatientSummary,
    HealthActivityRecommendation,
    HealthActivityRecommendationList,
    HealthActivityAssessmentOutput,
    HealthActivityStatus,
    ChronicDiseaseTrend,
    ChronicDiseaseTrendList,
    MedicationAnalysis,
    MedicationAnalysisList
)


class AshaAgentSystem:
    """Main orchestrator for the multi-agent health assessment pipeline"""
    
    def __init__(self, api_key: str = None):
        """Initialize the agent system with Google Gemini client"""
        genai.configure(api_key=api_key or config.GOOGLE_API_KEY)
        self.model_name = config.GEMINI_MODEL
        self.temperature = config.GEMINI_TEMPERATURE
        
        # Initialize the model
        generation_config = {
            "temperature": self.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 16384, # Increased token limit
        }

        # --- THIS IS THE NEW SAFETY SETTINGS BLOCK ---
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        # -----------------------------------------------

        # --- STORE THE SETTINGS ON THE CLASS INSTANCE ---
        self.safety_settings = safety_settings
        # -----------------------------------------------
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            safety_settings=self.safety_settings  # Pass them here during init
        )
    
    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Any = None
    ) -> Any:
        """
        Call Google Gemini LLM with system and user prompts.
        """
        # Combine system and user prompts for Gemini
        full_prompt = f"""{system_prompt}

---

{user_prompt}"""

        if response_format:
            # Request JSON output for structured responses
            full_prompt += f"""

Please respond with valid JSON matching this schema:
{response_format.model_json_schema()}

Return ONLY the JSON, no additional text."""
        
        # --- THIS IS THE CORRECTED CALL ---
        # It now passes the safety settings on every call
        response = self.model.generate_content(
            full_prompt,
            safety_settings=self.safety_settings 
        )
        # ----------------------------------
        
        if response_format:
            # Parse JSON response into Pydantic model
            try:
                response_text = response.text
                # Clean up response (remove markdown code blocks if present)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                return response_format.model_validate_json(response_text)
            
            # --- THIS IS THE SAFER EXCEPT BLOCK ---
            except Exception as e:
                print(f"Error parsing structured response: {e}")
                print(f"Full response object on error: {str(response)}")
                raise
            # ------------------------------------
        else:
            # This is for the chatbot, which wants a plain string
            try:
                return response.text
            except Exception as e:
                print(f"Error getting text response (likely safety block): {e}")
                print(f"Full response object on error: {str(response)}")
                return "I'm sorry, I encountered an error and cannot provide a response at this time."    
    
    # ========== AGENT 1: PATIENT SUMMARIZATION ==========
    
    def create_patient_summary(self, patient_data: str) -> PatientSummary:
        """
        Create basic and advanced patient summaries from health record AND extract a list of current medications.
        """
        system_prompt = """You are a medical data analyst specializing in patient record summarization.

Your task is to extract key information from a patient's health record and create two types of summaries:

1. BASIC SUMMARY: Demographics only (age, sex, basic info)
   Example: "44-year-old male"

2. ADVANCED SUMMARY: Demographics + key medical conditions
   Example: "44-year-old male with obesity (BMI 32), prediabetes (HbA1c 6.2%), hypertension"
   
3. CURRRENT MEDICATIONS: A plain list of strings of the patient's current medications. (e.g., ["Lisinopril 20mg", "Metformin 1000mg"]).

Extract:
- Age (calculate from birth year if needed)
- Sex/Gender
- Major chronic conditions (diabetes, hypertension, obesity, heart disease, etc.)
- Risk factors (smoking, family history, etc.)

Be concise and clinically relevant. Only list medications found under a "Current Medications" or active "PLAN" section. """

        user_prompt = f"""Analyze this patient health record, create both summaries and also extract the 3 items for Current Medications:

{patient_data[:3000]}

If the record is incomplete, make reasonable inferences from available data."""

        response = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=PatientSummary
        )
        
        return response
    
    # --- NEW TREND ANALYSIS AGENT ---
    # ========== AGENT 1.5: TREND ANALYST ==========

    def run_trend_analysis_agent(
        self, 
        patient_summary: PatientSummary, 
        patient_data: str
    ) -> List[ChronicDiseaseTrend]:
        """
        Analyzes the complete patient record for longitudinal trends
        in key chronic disease metrics.
        """

        # Find out which chronic diseases to even look for
        conditions = patient_summary.advanced_summary.lower()
        metrics_to_track = []
        if "diabetes" in conditions or "prediabetes" in conditions:
            metrics_to_track.append("HbA1c")
        if "hypertension" in conditions:
            metrics_to_track.append("Blood Pressure (BP)")
        if "obesity" in conditions:
            metrics_to_track.append("Weight (BMI)")

        if not metrics_to_track:
            print("  No trackable chronic diseases found for trend analysis.")
            return []

        system_prompt = f"""You are a clinical data analyst. Your job is to perform a longitudinal trend analysis for a patient's chronic conditions.
You will be given a de-identified record where dates are formatted like `[DATE]/YYYY`.

**CRITICAL RULE:** Your final output MUST be human-readable.
- When you find a data point like `7.2% on [DATE]/2024`, you MUST re-format it in your `data_points` list to only include the value and the year.
- **Correct format:** "7.2% (in 2024)"
- **Incorrect format:** "7.2% on [DATE]/2024"

You must scan the *entire* patient record to find all data points for the following metrics: {', '.join(metrics_to_track)}.

For each metric, you will:
1.  **Find Data Points:** Extract all available data and **re-format them** as human-readable strings (e.g., "7.2% (in 2024)").
2.  **Determine Trend:** Analyze the data points chronologically and set the 'trend' to "Improving", "Worsening", "Stable", or "Not Enough Data".
3.  **Write Analysis:** Provide a concise, one-sentence analysis, also using only the year (e.g., "The patient's HbA1c was 7.2% in 2024.").

You must return a JSON list, one entry for each metric.
"""

        user_prompt = f"""**Patient Summary:**
{patient_summary.advanced_summary}

**Full Patient Record:**
{patient_data}

---
Please generate the trend analysis for the metrics: {', '.join(metrics_to_track)}
"""

        # Ask for the new container model
        response_model = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=ChronicDiseaseTrendList  # <-- Use the new container
        )
        
        # Return the list *inside* the container
        return response_model.trends
    
    # ========== AGENT 2: WEB-BASED RECOMMENDATIONS ==========
    
    def generate_web_recommendations(
        self,
        patient_summary: str,
        is_advanced: bool = False
    ) -> List[HealthActivityRecommendation]:
        """
        Generate health recommendations using web search (or LLM knowledge).
        """
        system_prompt = """You are a preventive health advisor. Generate evidence-based health activity recommendations.

Your recommendations should include:
- Preventive screenings (cancer, cardiovascular, infectious disease)
- Vaccinations (flu, pneumonia, COVID, etc.)
- Lifestyle interventions (diet, exercise, sleep)
- Chronic disease management activities
- Mental health screenings

Base recommendations on:
- USPSTF guidelines (A and B grade recommendations)
- CDC recommendations
- Professional society guidelines (AHA, ADA, etc.)

Format each recommendation with:
- recommendation_short_str: Brief title. **MUST be 100 characters or less.**
- recommendation_long_str: Detailed description.
- frequency_short_str: How often (e.g., "Annually", "Every 5 years"). **MUST be 120 characters or less.**
- category: Appropriate health category
- source: Where this recommendation comes from"""

        context_type = "condition-specific" if is_advanced else "general"
        user_prompt = f"""Generate {context_type} health recommendations for this patient:

Patient: {patient_summary}

Provide 5-10 evidence-based recommendations appropriate for this patient's profile.
Focus on actionable, specific health activities."""

        response_text = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=HealthActivityRecommendationList
        )
        
        return response_text.activities
    
    # ========== AGENT 2.5: MEDICATION AUDITOR ==========

    def run_medication_analysis_agent(
        self,
        patient_summary: PatientSummary,
        patient_data: str  # Pass full record for context
    ) -> List[MedicationAnalysis]:
        """
        Analyzes the patient's current medication list for potential
        interactions, condition conflicts, or outdated scripts.
        """

        if not patient_summary.current_medications:
            print("  No current medications found to analyze.")
            return []

        system_prompt = """You are an expert AI Pharmacist-Auditor. Your job is to review a patient's medication list and flag potential issues for a *doctor's review*.

**CRITICAL RULES:**
1.  **YOU ARE AN AUDITOR, NOT A DOCTOR.** You MUST NOT give medical advice or tell the user to "stop taking" medication.
2.  **GROUND YOUR ANALYSIS:** Your analysis MUST be based *only* on the provided `Patient Summary` and `Current Medications` list.
3.  **CITE YOUR EVIDENCE:** For every issue you flag, you MUST fill the `supporting_evidence` field with the *exact* data you used (e.g., "Conflict found between 'Med: Aspirin 81mg' and 'Condition: Atrial Fibrillation'").
4.  **NO HALLUCINATIONS:** You are **FORBIDDEN** from analyzing or mentioning redacted data like `[NAME]` or `[REDACTED]`. If the medication list is empty or only contains redacted text, you must return an empty list.

**YOUR TASK:**
Review the `current_medications` list and check for 3 types of issues:
1.  **Interaction:** A significant interaction *between two* medications on the list.
2.  **Condition Conflict:** A medication that is risky for a condition in the `advanced_summary`.
3.  **Outdated:** A medication that is for short-term use (e.g., antibiotic) but appears to be on a permanent list.

Return a JSON list of all issues you find. If you find no issues, return an empty list.
"""

        user_prompt = f"""**Patient Summary:**
{patient_summary.advanced_summary}

**Current Medications:**
{json.dumps(patient_summary.current_medications)}

**Full Patient Record (for context):**
{patient_data}

---
Please analyze the medication list and return a list of potential issues.
"""

        response_model = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=MedicationAnalysisList  
        )

        return response_model.analyses
    
    # ========== AGENT 3: USPSTF GUIDELINES (RAG) ==========
    
    def get_uspstf_recommendations(
        self,
        patient_summary: PatientSummary,
        uspstf_guidelines: List[Dict[str, Any]]
    ) -> List[HealthActivityRecommendation]:
        """
        Generate recommendations from USPSTF guidelines database (RAG approach).
        """
        if not uspstf_guidelines:
            return []
        
        # Convert guidelines to readable format for LLM
        guidelines_text = "\n\n".join([
            f"Title: {g['title']}\n"
            f"Description: {g['description']}\n"
            f"Population: {g['population']}\n"
            f"Grade: {g['grade']}"
            for g in uspstf_guidelines[:15]  # Limit to top 15 to stay within context
        ])
        
        system_prompt = """You are a clinical guidelines specialist. Convert USPSTF guidelines into patient-friendly recommendations.

Your task:
1. Review the provided USPSTF guidelines (Grades A & B).
2. Select those applicable to the patient's demographics.
3. Convert each into a clear, actionable health activity using this exact format:

- recommendation_short_str: Brief title. **MUST be 100 characters or less.**
- recommendation_long_str: Detailed description.
- frequency_short_str: How often (e.g., "Annually", "Every 5 years"). **MUST be 120 characters or less.**
- category: Appropriate health category (e.g., "Preventive Screening").
- source: "USPSTF Grade A" or "USPSTF Grade B".

Be concise, accurate, and strictly follow the output format."""

        user_prompt = f"""Patient: {patient_summary.basic_summary}

        USPSTF Guidelines Database:
        {guidelines_text}

        Generate health activity recommendations based on applicable guidelines.
        Source should be "USPSTF Grade A" or "USPSTF Grade B"."""

        response = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=HealthActivityRecommendationList
        )
        
        return response.activities
    
    # ========== AGENT 4: CONSOLIDATION & DEDUPLICATION ==========
    
    def consolidate_recommendations(
        self,
        recommendations_list: List[List[HealthActivityRecommendation]]
    ) -> List[HealthActivityRecommendation]:
        """
        Consolidate and deduplicate recommendations from multiple sources.
        """
        # Flatten all recommendations
        all_recs = []
        for rec_group in recommendations_list:
            all_recs.extend(rec_group)
        
        if not all_recs:
            return []
        
        # Convert to JSON for LLM processing
        recs_json = json.dumps(
            [rec.model_dump() for rec in all_recs],
            indent=2
        )
        
        system_prompt = """You are a data consolidation specialist for health recommendations.

Your task: Remove duplicate and semantically similar recommendations.

Examples of duplicates:
- "Get flu shot" = "Receive influenza vaccine"
- "Blood pressure check" = "Hypertension screening"

When consolidating:
1. Keep the most specific and clear wording.
2. Combine sources (e.g., "CDC, USPSTF").
3. **Frequency Handling (IMPORTANT):** The 'frequency_short_str' MUST be 120 characters or less.
   - If frequencies are identical, use it.
   - If frequencies are different (e.g., "Annually" and "Every 5 years"), pick the MOST frequent one (e.g., "Annually") or use a short, general term like "Varies" or "As directed".
   - **Do NOT** combine them into a long string like "Annually; Every 5 years".
4. Generate a unique activity_id for each unique recommendation.

Your output must be a deduplicated list with NO semantic duplicates and all fields must respect the length constraints."""

        user_prompt = f"""Consolidate these recommendations into a unique, deduplicated list:

        {recs_json}

        Remove ALL duplicates and similar recommendations. Return clean, consolidated list."""

        response = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=HealthActivityRecommendationList
        )
        
        return response.activities
    
    # ========== AGENT 5: ACTIVITY ASSESSMENT (The "Brain") ==========
    
    def assess_activity(
        self,
        activity: HealthActivityRecommendation,
        patient_data: str
    ) -> HealthActivityAssessmentOutput:
        """
        Assess if a health activity was completed based on patient record.
        
        This is now a 2-STEP SELF-CORRECTION LOOP:
        1. "Assessor" agent generates a first draft.
        2. "Validator" agent reviews the draft for accuracy and provides a
           final, corrected assessment.
        """
        
        # ========== STEP 1: THE "ASSESSOR" (FIRST DRAFT) ==========
        
        system_prompt_assessor = """You are a medical record analyst and clinical triage expert.

    Your task: Determine the status of a health activity AND its medical urgency.
    You will be given text that has been de-identified and contains tokens like [NAME] or [DATE].

    **CRITICAL RULE:** Your final output MUST be human-readable.
    - Do NOT include redacted tokens like `[NAME]` or `[DATE]` in your output.
    - For `supporting_evidence`, **paraphrase** your finding (e.g., "A normal lipid panel was recorded in Sep 2024.").
    - For `completion_date`, provide the general date (e.g., "Sep 2024" or "2023").

    You must perform "fuzzy reasoning" to determine the status (Completed, Recommended, Needs user confirmation).

    You must also assign an 'urgency' level:
    - 'High': Critical, overdue screenings or unmanaged chronic conditions.
    - 'Medium': Routine annual tasks or follow-ups.
    - 'Low': General wellness advice.
    
    Be thorough. Your output must be a valid, human-readable JSON."""

        user_prompt_assessor = f"""Activity to assess:
    {activity.model_dump_json(indent=2)}

    Patient Health Record:
    {patient_data}

    Analyze the entire record and determine the status and urgency of this activity."""

        try:
            # Generate the first draft
            draft_assessment = self._call_llm(
                system_prompt=system_prompt_assessor,
                user_prompt=user_prompt_assessor,
                response_format=HealthActivityAssessmentOutput
            )
        except Exception as e:
            print(f"Error during DRAFT assessment: {e}")
            # If draft fails, create a default "Recommended" to be validated
            draft_assessment = HealthActivityAssessmentOutput(
                activity_id=activity.activity_id,
                recommendation_short_str=activity.recommendation_short_str,
                status=HealthActivityStatus.RECOMMENDED, # <-- CORRECTED
                urgency="Medium", # <-- Set a default urgency
                supporting_evidence="Error during initial AI assessment. Defaulting to 'Recommended'.",
                user_input_questions=[]
            )

        # ========== STEP 2: THE "VALIDATOR" (SELF-CORRECTION) ==========
        
        system_prompt_validator = """You are a meticulous Quality Control agent. You will review an AI's assessment of a patient record.
The record has been de-identified and contains tokens like [NAME] or [DATE].

**CRITICAL RULE:** The final output you approve or create MUST be human-readable.
- Do NOT include redacted tokens like `[NAME]` or `[DATE]`.
- All `supporting_evidence` must be a **paraphrase** (e.g., "A normal lipid panel was recorded in Sep 2024.").
- All `completion_date` fields must be general (e.g., "Sep 2024" or "2023").

Your job:
1. Review the "Activity" and the "Patient Record".
2. Critically analyze the "First-Draft Assessment" for accuracy AND for this human-readability rule.
3. Check if the 'supporting_evidence' truly supports the 'status'.
4. **Critically review the 'urgency' level.** Is 'High' appropriate for this patient's risks?
5. Assign a 'confidence_score' (0-100) for the draft.
6. **Final Decision:**
   - If confidence < 70 OR if the draft includes redacted tokens, you MUST provide a *new, corrected, human-readable assessment*.
   - If confidence >= 70 and the draft is human-readable, return the *original draft assessment* (but add your confidence score).

7. **MANDATORY RULE:** If the final 'status' is "Needs user confirmation", you MUST generate 'user_input_questions'.

Your final output MUST be a single, valid, human-readable JSON object."""

        user_prompt_validator = f"""**1. Original Activity to Assess:**
    {activity.model_dump_json(indent=2)}

    **2. Patient Health Record:**
    {patient_data}

    **3. AI's First-Draft Assessment:**
    {draft_assessment.model_dump_json(indent=2)}

    ---
    Review the draft against the record. Assign a confidence score. If confidence is low, provide a new, corrected assessment. If it's high, return the draft with your score.
    """

        try:
            # Generate the final, validated assessment
            final_assessment = self._call_llm(
                system_prompt=system_prompt_validator,
                user_prompt=user_prompt_validator,
                response_format=HealthActivityAssessmentOutput
            )
        except Exception as e:
            print(f"Error during VALIDATION assessment: {e}")
            # If validator fails, just return the original draft
            final_assessment = draft_assessment

        # --- Final Step: Copy over original data ---
        # This ensures no data is lost during validation
        final_assessment.activity_id = activity.activity_id
        final_assessment.recommendation_short_str = activity.recommendation_short_str
        final_assessment.recommendation_long_str = activity.recommendation_long_str
        final_assessment.frequency_short_str = activity.frequency_short_str
        final_assessment.category = activity.category
        
        return final_assessment


    # ========== AGENT 6: CONVERSATIONAL CHATBOT ==========
    
    def run_chat_agent(
            self,
            user_question: str,
            patient_summary: str,
            health_report_json: str
        ) -> str:
            """
            A conversational agent that answers questions about the generated report.
            It uses the report and summary as its ONLY source of context.
            """
            
            system_prompt = """You are CareGuide, a friendly and helpful AI health assistant.
        
        Your job is to answer the user's questions about their "Health Engagement Report".
        
        **CRITICAL RULES:**
        1.  You MUST answer questions *only* using the provided "Patient Summary" and "Health Report JSON" as your context.
        2.  Do NOT invent information or answer general medical questions that are not in the report.
        3.  If the answer isn't in the report, you must say "I don't have that specific information in your report."
        4.  Be empathetic, clear, and conversational.
        
        **Example:**
        User: "Why do I need a flu shot?"
        You: "The report recommends a flu shot because it's an important preventive vaccination. The system did not find any evidence in your record that you've received one this season."
        """
            
            user_prompt = f"""Here is the patient's information:
        
        **Patient Summary:**
        {patient_summary}
        
        **Full Health Report (JSON):**
        {health_report_json}
        
        ---
        **User's Question:**
        {user_question}
        
        Please answer the user's question based *only* on the information above.
        """
            
            # Call the LLM for a simple text response
            response = self._call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format=None
            )
            
            return response

    # ========== AGENT 7: WHAT-IF ANALYST AGENT ==========
    
    def run_what_if_analysis_agent(
        self,
        patient_summary: str,
        health_report_json: str,
        selected_activity_name: str,
        current_score: float,
        new_score: float
    ) -> str:
        """
        A specialized agent that analyzes a "What-If" scenario and provides
        a personalized explanation for the medical and score-based reasons.
        """
        
        system_prompt = """You are a precision AI analyst named 'CareGuide'.
Your job is to analyze a 'what-if' scenario for a user about their health report.

**CRITICAL RULES:**
1.  **NO OUTSIDE KNOWLEDGE:** You are FORBIDDEN from using any information not explicitly provided in the `Patient Summary` or `Health Report JSON`.
2.  **USE THE CONTEXT:** Your analysis MUST be based *only* on the provided data. Reference the patient's specific conditions (like 'Type 2 Diabetes' or 'Hypertension') from the summary.
3.  **QUOTE YOUR EVIDENCE:** When explaining the medical reason, you should briefly cite the patient's condition (e.g., "Because your summary notes you are managing Type 2 Diabetes...").
4.  **STAY FOCUSED:** Do not be overly chatty. Provide two clear sections: "1. The Medical Reason" and "2. The Score Reason".

**YOUR TASK:**
1.  **The Medical Reason:** Explain why the `selected_activity` is medically important, *specifically* for the conditions listed in the `Patient Summary`.
2.  **The Score Reason:** Explain how the `current_score` changed to the `new_score` based on the weighted scoring system (High=3, Medium=2, Low=1).
"""
        
        user_prompt = f"""Here is the simulation context:

**Patient Summary:**
{patient_summary}

**Full Health Report (JSON):**
{health_report_json}

**Selected Activity to Simulate:**
{selected_activity_name}

**Score Change:**
- Current Score: {current_score:.1f}
- Simulated New Score: {new_score:.1f}

---
Please provide your analysis, starting with the medical reason for this activity's importance.
"""
        response = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=None  
        )
        
        return response