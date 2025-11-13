"""
Utility functions for Project Asha
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import config
from models import HealthActivityAssessmentOutput, HealthActivityStatus


def deidentify_patient_data(text: str) -> str:
    """
    De-identify patient data using HIPAA Safe Harbor method.
    Removes 18 PHI identifiers to make data safe for API calls.
    """
    deidentified = text
    
    # Simple regex for PII (names, dates, phones, etc.)
    # In a real app, this would be much more robust.
    
    # Remove names (simple pattern)
    deidentified = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', deidentified)
    deidentified = re.sub(r'\bMr\.|Mrs\.|Ms\.|Dr\. [A-Z][a-z]+\b', '[NAME]', deidentified)
    
    # Remove dates (keep year for age calculation, remove month/day)
    deidentified = re.sub(
        r'\b(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/(\d{4})\b',
        r'[DATE]/\3',
        deidentified
    )
    deidentified = re.sub(
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        '[DATE]',
        deidentified,
        flags=re.IGNORECASE
    )
    
    # Remove phone numbers
    deidentified = re.sub(
        r'\b(\d{3}[-.]?\d{3}[-.]?\d{4}|\(\d{3}\)\s*\d{3}[-.]?\d{4})\b',
        '[PHONE]',
        deidentified
    )
    
    # Remove email addresses
    deidentified = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL]',
        deidentified
    )
    
    # Remove SSN
    deidentified = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', deidentified)
    
    # Remove medical record numbers (MRN)
    deidentified = re.sub(
        r'\b(MRN|Record #|Patient ID)[:\s]*[A-Z0-9-]+\b',
        '[MRN]',
        deidentified,
        flags=re.IGNORECASE
    )
    
    # Remove specific addresses
    deidentified = re.sub(
        r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b',
        '[ADDRESS]',
        deidentified,
        flags=re.IGNORECASE
    )
    
    # Remove ZIP codes
    deidentified = re.sub(r'\b\d{5}(-\d{4})?\b', '[ZIP]', deidentified)
    
    return deidentified


def load_patient_record(file_path: Path) -> str:
    """
    Load patient health record from file.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Patient record not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_uspstf_guidelines(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load USPSTF guidelines from JSON file.
    """
    if not file_path.exists():
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_uspstf_by_demographics(
    guidelines: List[Dict[str, Any]],
    age: int = None,
    sex: str = None
) -> List[Dict[str, Any]]:
    """
    Filter USPSTF guidelines by patient demographics.
    (This is a simple filter for the demo)
    """
    if not guidelines:
        return []
    
    filtered = []
    for guideline in guidelines:
        population = guideline.get('population', '').lower()
        
        # Simple age filtering
        if age:
            if 'adults' in population and age >= 18:
                filtered.append(guideline)
            elif 'children' in population and age < 18:
                filtered.append(guideline)
            elif f'{age}' in population:
                filtered.append(guideline)
        
        # Sex filtering
        if sex and (sex.lower() in population or 'all' in population):
            if guideline not in filtered:
                filtered.append(guideline)
    
    return filtered if filtered else guidelines[:10]  # Return top 10 if no match


# --- FUNCTION NAME RENAMED TO FIX BUG ---
def calculate_weighted_health_engagement_score(
    activity_assessments: List[HealthActivityAssessmentOutput]
) -> dict:
    """
    Calculate a realistic, WEIGHTED health engagement score (0-100).
    
    High-urgency tasks are worth more points than low-urgency tasks.
    """
    if not activity_assessments:
        return {"score": 0.0, "earned_points": 0, "total_possible": 0}

    # --- NEW: Urgency Weights ---
    weights = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    total_possible_points = 0
    earned_points = 0.0

    for assessment in activity_assessments:
        # Get the point value for this task
        urgency = assessment.urgency or "Medium"  # Default to Medium if missing
        task_points = weights.get(urgency, 2)  # Default to 2
        
        # Add to the total possible score
        total_possible_points += task_points

        # Add to the earned score based on status
        if assessment.status == HealthActivityStatus.COMPLETED:
            earned_points += task_points  # 100% credit
        elif assessment.status == HealthActivityStatus.NEEDS_CONFIRMATION:
            earned_points += (task_points * 0.5)  # 50% credit
        # 'Recommended' tasks earn 0 points

    if total_possible_points == 0:
        return {"score": 0.0, "earned_points": 0, "total_possible": 0}

    # Calculate final percentage
    score = (earned_points / total_possible_points) * 100
    
    return {
        "score": score,
        "earned_points": earned_points,
        "total_possible": total_possible_points
    }


def save_output(output_data: Dict[str, Any], filename: str = None):
    """
    Save assessment output to JSON file.
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assessment_{timestamp}.json"
    
    output_path = config.OUTPUT_DIR / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    return output_path