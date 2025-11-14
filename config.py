"""
Configuration settings for CareGuide
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PATIENT_DATA_FILE = DATA_DIR / "demo_patient_record.txt"
USPSTF_DATA_FILE = DATA_DIR / "uspstf_guidelines.json"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

# Debug: Print API key status (without exposing the key)
if GOOGLE_API_KEY:
    print(f"✅ Google Gemini API key loaded: {GOOGLE_API_KEY[:7]}...{GOOGLE_API_KEY[-4:]}")
else:
    print("❌ Google Gemini API key NOT found in environment!")
    print(f"Current working directory: {os.getcwd()}")
    print(f".env file exists: {(BASE_DIR / '.env').exists()}")

# In config.py
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_TEMPERATURE = 0.1  # Low temperature for deterministic outputs

# HIPAA Safe Harbor - 18 PHI identifiers to remove
PHI_IDENTIFIERS = [
    "names",
    "geographic_subdivisions",
    "dates",
    "phone_numbers",
    "fax_numbers",
    "email_addresses",
    "ssn",
    "mrn",
    "health_plan_numbers",
    "account_numbers",
    "certificate_numbers",
    "vehicle_identifiers",
    "device_identifiers",
    "urls",
    "ip_addresses",
    "biometric_identifiers",
    "photos",
    "other_identifiers"
]

# Streamlit configuration
STREAMLIT_TITLE = "CareGuide - Your AI Health Companion"
STREAMLIT_ICON = "🏥"
