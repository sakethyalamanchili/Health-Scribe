"""
Pydantic Models for CareGuide - Health Engagement System
These models ensure structured, validated outputs from all AI agents
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum


class HealthActivityStatus(str, Enum):
    """Enumeration for health activity completion status"""
    COMPLETED = "Completed"
    RECOMMENDED = "Recommended"
    NEEDS_CONFIRMATION = "Needs user confirmation"


class HealthActivityRecommendation(BaseModel):
    """Individual health activity recommendation"""
    activity_id: str = Field(description="Unique identifier for this activity")
    recommendation_short_str: str = Field(
        description="Brief activity description (max 100 chars)",
        max_length=150
    )
    recommendation_long_str: str = Field(
        description="Detailed activity description"
    )
    frequency_short_str: str = Field(
        description="Frequency description (max 120 chars)",
        max_length=120
    )
    category: Literal[
        "Preventive Screening",
        "Vaccination",
        "Lifestyle & Wellness",
        "Chronic Disease Management",
        "Mental Health",
        "Other"
    ] = Field(description="Health activity category")
    source: str = Field(description="Source of recommendation (e.g., USPSTF, Web Research)")


class HealthActivityRecommendationList(BaseModel):
    """Consolidated list of unique health activity recommendations"""
    activities: List[HealthActivityRecommendation] = Field(
        description="List of consolidated, deduplicated health activities"
    )


class HealthActivityAssessmentOutput(BaseModel):
    """Assessment result for a single health activity"""
    activity_id: str = Field(description="ID of the activity being assessed")
    recommendation_short_str: str = Field(description="Activity name")
    
    confidence_score: Optional[int] = Field(
        default=None,
        description="Confidence in this assessment (0-100)"
    )
    
    # --- NEW URGENCY FIELD ---
    urgency: Literal["High", "Medium", "Low"] = Field(
        default="Medium",
        description="Medical urgency of this activity for this patient (High, Medium, Low)"
    )
    
    recommendation_long_str: str = Field(description="Detailed activity description", default="")
    frequency_short_str: str = Field(description="Frequency description", default="")
    category: str = Field(description="Health activity category", default="Other")

    status: HealthActivityStatus = Field(
        description="Completion status of this activity"
    )
    supporting_evidence: str = Field(
        description="Evidence from patient record supporting this status"
    )
    user_input_questions: List[str] = Field(
        default=[],
        description="Questions for the user if confirmation is needed"
    )
    completion_date: Optional[str] = Field(
        default=None,
        description="Date of completion if found in record"
    )

# --- MODEL FOR TREND ANALYSIS ---
class ChronicDiseaseTrend(BaseModel):
    """Analysis of a single chronic disease metric over time."""
    metric_name: str = Field(description="The name of the metric being tracked (e.g., 'HbA1c', 'Blood Pressure', 'Weight (BMI)')")
    trend: Literal["Improving", "Worsening", "Stable", "Not Enough Data"] = Field(description="The direction of the trend")
    analysis: str = Field(description="The AI's one-sentence analysis of this trend.")
    data_points: List[str] = Field(description="A list of the raw data points and dates found in the text (e.g., '7.8% on 10/15/2024')")
    
class ChronicDiseaseTrendList(BaseModel):
    """A container for the list of chronic disease trends."""
    trends: List[ChronicDiseaseTrend] = Field(description="A list of the chronic disease trend analyses.")

class MedicationAnalysis(BaseModel):
    """Analysis of a single medication or interaction."""
    medication_name: str = Field(description="The primary medication being analyzed (e.g., 'Lisinopril')")
    analysis_type: Literal["Interaction", "Condition Conflict", "Outdated"] = Field(description="The *type* of issue found.")
    urgency: Literal["High", "Medium", "Low"] = Field(description="The urgency of discussing this with a doctor.")
    explanation: str = Field(description="The AI's explanation of the potential issue for the user to discuss with their doctor.")

    supporting_evidence: str = Field(
        description="The exact data from the context (med list or summary) that justifies this analysis."
    )

class MedicationAnalysisList(BaseModel):
    """A container for the list of medication analyses."""
    analyses: List[MedicationAnalysis] = Field(description="A list of the AI-flagged medication issues.")

class HealthAssessmentOutput(BaseModel):
    """Final output containing all assessed health activities"""
    patient_summary: str = Field(description="Brief patient demographic summary")
    total_activities: int = Field(description="Total number of activities assessed")
    completed_count: int = Field(description="Number of completed activities")
    recommended_count: int = Field(description="Number of recommended activities")
    needs_confirmation_count: int = Field(
        description="Number of activities needing user input"
    )
    health_engagement_score: float = Field(
        description="Overall health engagement score (0-100)",
        ge=0,
        le=100
    )
    disease_trends: List[ChronicDiseaseTrend] = Field(
        default=[],
        description="List of chronic disease trend analyses"
    )
    medication_analysis_list: List[MedicationAnalysis] = Field(
        default=[],
        description="List of AI-flagged medication issues for review."
    )
    activity_assessments: List[HealthActivityAssessmentOutput] = Field(
        description="List of all activity assessments"
    )

class PatientSummary(BaseModel):
    """Patient demographic and medical summary"""
    age: Optional[int] = Field(default=None, description="Patient age")
    sex: Optional[str] = Field(default=None, description="Patient sex")
    basic_summary: str = Field(description="Brief demographic summary")
    advanced_summary: str = Field(description="Detailed medical summary including conditions")
    
    current_medications: List[str] = Field(
        default=[],
        description="A list of the patient's current medications (e.g., ['Lisinopril 20mg', 'Metformin 1000mg'])"
    )

class USPSTFRecommendation(BaseModel):
    """USPSTF guideline recommendation"""
    title: str
    description: str
    population: str
    grade: Literal["A", "B"]
    category: str
    
