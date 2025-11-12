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
from models import HealthAssessmentOutput, HealthActivityAssessmentOutput


class HealthAssessmentOrchestrator:
    """
    Orchestrates the deterministic multi-agent pipeline.
    
    Pipeline Steps:
    0. De-identification (HIPAA compliance)
    1. Ingestion (load patient data)
    2. Summarization (basic + advanced)
    3. Multi-source recommendations (web + USPSTF RAG)
    4. Consolidation (semantic deduplication)
    5. Assessment (fuzzy reasoning for each activity)
    6. Score calculation and output
    """
    
    def __init__(self, api_key: str = None):
        """Initialize orchestrator with agent system"""
        self.agent_system = AshaAgentSystem(api_key=api_key)
    
    def run_full_assessment(
        self,
        patient_record_path: Path = None,
        patient_record_text: str = None
    ) -> HealthAssessmentOutput:
        """
        Run the complete health assessment pipeline.
        
        Args:
            patient_record_path: Path to patient record file
            patient_record_text: Direct patient record text (alternative to file)
            
        Returns:
            Complete health assessment with engagement score
        """
        # ========== STEP 0: LOAD RAW DATA ==========
        if patient_record_text:
            raw_patient_data = patient_record_text
        elif patient_record_path:
            raw_patient_data = utils.load_patient_record(patient_record_path)
        else:
            raw_patient_data = utils.load_patient_record(config.PATIENT_DATA_FILE)
        
        # ========== STEP 1: DE-IDENTIFICATION ==========
        print("Step 1: De-identifying patient data (HIPAA compliance)...")
        patient_data = utils.deidentify_patient_data(raw_patient_data)
        
        # ========== STEP 2: PATIENT SUMMARIZATION ==========
        print("Step 2: Creating patient summaries...")
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

            time.sleep(6)
        
        # ========== STEP 6: CALCULATE METRICS ==========
        print("Step 6: Calculating health engagement score...")
        
        completed_count = sum(
            1 for a in activity_assessments
            if a.status == "Completed"
        )
        recommended_count = sum(
            1 for a in activity_assessments
            if a.status == "Recommended"
        )
        needs_confirmation_count = sum(
            1 for a in activity_assessments
            if a.status == "Needs user confirmation"
        )
        
        health_score = utils.calculate_health_engagement_score(
            completed=completed_count,
            total=len(activity_assessments),
            needs_confirmation=needs_confirmation_count
        )
        
        print(f"  Health Engagement Score: {health_score:.1f}/100")
        print(f"  Completed: {completed_count}, Recommended: {recommended_count}, Needs Confirmation: {needs_confirmation_count}")
        
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
        result = orchestrator.run_full_assessment()
        
        # Save output
        output_path = utils.save_output(result.model_dump())
        print(f"\nOutput saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError during assessment: {e}")
        raise


if __name__ == "__main__":
    main()
