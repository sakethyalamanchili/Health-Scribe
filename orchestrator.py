"""
Main Orchestrator for Project Asha - The AI Assembly Line
Coordinates the multi-agent pipeline in a deterministic sequence
"""

import time
from typing import Dict, Any
from pathlib import Path
import config
import utils
from agents import AshaAgentSystem
from models import HealthAssessmentOutput, HealthActivityAssessmentOutput, HealthActivityStatus


class HealthAssessmentOrchestrator:
    """
    Orchestrates the deterministic multi-agent pipeline.
    
    Pipeline Steps:
    0. Ingestion (load and unify multiple .txt files)
    1. De-identification (HIPAA compliance)
    2. Summarization (basic + advanced)
    3. Multi-source recommendations (web + USPSTF RAG)
    4. Consolidation (semantic deduplication)
    5. Assessment (self-correcting loop for each activity)
    6. Score calculation and output
    """
    
    def __init__(self, api_key: str = None):
        """Initialize orchestrator with agent system"""
        self.agent_system = AshaAgentSystem(api_key=api_key)
    
    def run_full_assessment(
        self,
        text_files: list = None,
        patient_record_text: str = None  # Kept for demo mode and testing
    ) -> HealthAssessmentOutput:
        """
        Run the complete health assessment pipeline.
        
        This function now:
        1. Ingests a list of text files.
        2. Unifies them into a single "master record".
        3. Passes the master record to the agent pipeline.
        """
        
        # ========== STEP 0: INGESTION & UNIFICATION ==========
        print("Step 0: Ingesting and unifying all records...")
        
        all_text_fragments = []

        # Case 1: Direct text (from demo button or main() test)
        if patient_record_text:
            all_text_fragments.append(patient_record_text)
            print("  Processing direct text input (Demo Mode)")

        # Case 2: Files from Streamlit upload
        if text_files:
            for file in text_files:
                content = file.read().decode('utf-8')
                all_text_fragments.append(f"--- START OF FILE: {file.name} ---\n{content}\n--- END OF FILE ---\n")
                print(f"  Ingested text file: {file.name}")

        # Case 3: Fallback for command-line testing (if no files)
        if not all_text_fragments:
            print("  No files or text provided. Falling back to default demo file for testing.")
            raw_patient_data = utils.load_patient_record(config.PATIENT_DATA_FILE)
        else:
            # Create the single "Master Health Record"
            raw_patient_data = "\n\n".join(all_text_fragments)
            print(f"  Unified into one master record.")
        
        
        # ========== STEP 1: DE-IDENTIFICATION ==========
        print("Step 1: De-identifying master patient data (HIPAA compliance)...")
        patient_data = utils.deidentify_patient_data(raw_patient_data)
        
        # ========== STEP 2: PATIENT SUMMARIZATION ==========
        print("Step 2: Creating patient summaries from master record...")
        patient_summary = self.agent_system.create_patient_summary(patient_data)
        print(f"  Basic: {patient_summary.basic_summary}")
        print(f"  Advanced: {patient_summary.advanced_summary}")
        
        # ========== STEP 3: MULTI-SOURCE RECOMMENDATIONS ==========
        print("Step 3: Gathering recommendations from multiple sources...")
        
        # Source 1: General web recommendations
        print("  Source 1: General health recommendations...")
        general_recs = self.agent_system.generate_web_recommendations(
            patient_summary=patient_summary.basic_summary,
            is_advanced=False
        )
        print(f"    Found {len(general_recs)} general recommendations")
        
        # Source 2: Condition-specific web recommendations
        print("  Source 2: Condition-specific recommendations...")
        specific_recs = self.agent_system.generate_web_recommendations(
            patient_summary=patient_summary.advanced_summary,
            is_advanced=True
        )
        print(f"    Found {len(specific_recs)} specific recommendations")
        
        # Source 3: USPSTF guidelines (RAG)
        print("  Source 3: USPSTF guidelines (RAG)...")
        uspstf_data = utils.load_uspstf_guidelines(config.USPSTF_DATA_FILE)
        filtered_uspstf = utils.filter_uspstf_by_demographics(
            uspstf_data,
            age=patient_summary.age,
            sex=patient_summary.sex
        )
        uspstf_recs = self.agent_system.get_uspstf_recommendations(
            patient_summary=patient_summary,
            uspstf_guidelines=filtered_uspstf
        )
        print(f"    Found {len(uspstf_recs)} USPSTF recommendations")
        
        # ========== STEP 4: CONSOLIDATION ==========
        print("Step 4: Consolidating and deduplicating recommendations...")
        consolidated_activities = self.agent_system.consolidate_recommendations(
            [general_recs, specific_recs, uspstf_recs]
        )
        print(f"  Consolidated to {len(consolidated_activities)} unique activities")
        
        # ========== STEP 5: ASSESSMENT LOOP ==========
        print("Step 5: Assessing each activity against patient record...")
        activity_assessments = []
        
        for i, activity in enumerate(consolidated_activities, 1):
            print(f"  [{i}/{len(consolidated_activities)}] Assessing: {activity.recommendation_short_str}")
            
            assessment = self.agent_system.assess_activity(
                activity=activity,
                patient_data=patient_data
            )
            
            activity_assessments.append(assessment)
            print(f"    Status: {assessment.status}")

            time.sleep(6) # Keep this to respect the free-tier rate limit!
        
        # ========== STEP 6: CALCULATE METRICS ==========
        print("Step 6: Calculating health engagement score...")
        
        # --- THIS IS THE UPDATED SCORING CALL ---
        # It now calls your new weighted score function
        score_data = utils.calculate_weighted_health_engagement_score(activity_assessments)
        health_score = score_data["score"]
        # ----------------------------------------
        
        # We still need the simple counts for the UI display
        completed_count = sum(
            1 for a in activity_assessments
            if a.status == HealthActivityStatus.COMPLETED
        )
        recommended_count = sum(
            1 for a in activity_assessments
            if a.status == HealthActivityStatus.RECOMMENDED
        )
        needs_confirmation_count = sum(
            1 for a in activity_assessments
            if a.status == HealthActivityStatus.NEEDS_CONFIRMATION
        )
        
        print(f"  Weighted Health Engagement Score: {health_score:.1f}/100")
        print(f"  Task Counts: Completed: {completed_count}, Recommended: {recommended_count}, Needs Confirmation: {needs_confirmation_count}")
        
        # ========== STEP 7: BUILD FINAL OUTPUT ==========
        final_output = HealthAssessmentOutput(
            patient_summary=patient_summary.basic_summary,
            total_activities=len(activity_assessments),
            completed_count=completed_count,
            recommended_count=recommended_count,
            needs_confirmation_count=needs_confirmation_count,
            health_engagement_score=health_score,
            activity_assessments=activity_assessments
        )
        
        print("\nAssessment complete!")
        return final_output


def main():
    """
    Main entry point for command-line testing.
    """
    print("=" * 60)
    print("PROJECT ASHA - Health Engagement Assessment System")
    print("=" * 60)
    print()
    
    # Initialize orchestrator
    orchestrator = HealthAssessmentOrchestrator()
    
    # Run full assessment
    try:
        # This will call run_full_assessment() with no arguments
        # The function will then use its fallback to load the demo file
        result = orchestrator.run_full_assessment()
        
        # Save output
        output_path = utils.save_output(result.model_dump())
        print(f"\nOutput saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError during assessment: {e}")
        raise


if __name__ == "__main__":
    main()