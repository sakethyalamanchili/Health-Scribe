"""
Utility functions for Project Asha
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import config


def deidentify_patient_data(text: str) -> str:
    """
    De-identify patient data using HIPAA Safe Harbor method.
    Removes 18 PHI identifiers to make data safe for API calls.
    
    Args:
        text: Raw patient health record text
        
    Returns:
        De-identified text safe for processing
    """
    deidentified = text
    
    # Remove names (simple pattern - would be more sophisticated in production)
    name_patterns = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
        r'\bMr\.|Mrs\.|Ms\.|Dr\. [A-Z][a-z]+\b',  # Titles with names
    ]
    for pattern in name_patterns:
        deidentified = re.sub(pattern, '[NAME]', deidentified)
    
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
        r'\b(\d{3}[-.]?\d{3}[-.]?\d{4}|$$\d{3}$$\s*\d{3}[-.]?\d{4})\b',
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
    deidentified = re.sub(
        r'\b\d{3}-\d{2}-\d{4}\b',
        '[SSN]',
        deidentified
    )
    
    # Remove medical record numbers (MRN)
    deidentified = re.sub(
        r'\b(MRN|Medical Record Number|Record #|Patient ID)[:\s]*[A-Z0-9-]+\b',
        '[MRN]',
        deidentified,
        flags=re.IGNORECASE
    )
    
    # Remove specific addresses (keep city/state for demographic info)
    deidentified = re.sub(
        r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b',
        '[ADDRESS]',
        deidentified,
        flags=re.IGNORECASE
    )
    
    # Remove ZIP codes (keep first 3 digits for regional info if needed)
    deidentified = re.sub(r'\b\d{5}(-\d{4})?\b', '[ZIP]', deidentified)
    
    return deidentified


def load_patient_record(file_path: Path) -> str:
    """
    Load patient health record from file.
    
    Args:
        file_path: Path to patient record file
        
    Returns:
        Patient record text
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Patient record not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_uspstf_guidelines(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load USPSTF guidelines from JSON file.
    
    Args:
        file_path: Path to USPSTF guidelines JSON
        
    Returns:
        List of guideline dictionaries
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
    
    Args:
        guidelines: Full list of USPSTF guidelines
        age: Patient age
        sex: Patient sex
        
    Returns:
        Filtered guidelines applicable to patient
    """
    if not guidelines:
        return []
    
    filtered = []
    for guideline in guidelines:
        population = guideline.get('population', '').lower()
        
        # Simple age filtering (would be more sophisticated in production)
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


def calculate_health_engagement_score(
    completed: int,
    total: int,
    needs_confirmation: int
) -> float:
    """
    Calculate health engagement score (0-100).
    
    Formula:
    - Completed activities contribute 100%
    - Activities needing confirmation contribute 50% (partial credit)
    - Higher weight for having more activities tracked
    
    Args:
        completed: Number of completed activities
        total: Total number of activities
        needs_confirmation: Number of activities needing confirmation
        
    Returns:
        Health engagement score (0-100)
    """
    if total == 0:
        return 0.0
    
    # Base score from completion
    base_score = (completed / total) * 100
    
    # Bonus for partially completed (needs confirmation)
    partial_score = (needs_confirmation / total) * 50
    
    # Combine scores
    raw_score = base_score + partial_score
    
    # Cap at 100
    return min(raw_score, 100.0)


def save_output(output_data: Dict[str, Any], filename: str = None):
    """
    Save assessment output to JSON file.
    
    Args:
        output_data: Assessment data to save
        filename: Output filename (auto-generated if None)
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assessment_{timestamp}.json"
    
    output_path = config.OUTPUT_DIR / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    return output_path
