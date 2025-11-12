"""
Quick setup checker to validate your environment before running the app
"""

import os
from pathlib import Path

def check_environment():
    """Check if the environment is properly configured"""
    print("🔍 Checking Project Asha setup...\n")
    
    issues = []
    warnings = []
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        issues.append("❌ .env file not found!")
        print("❌ .env file not found!")
        print("   → Copy .env.example to .env and add your API keys\n")
    else:
        print("✅ .env file exists\n")
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openai_key:
        issues.append("❌ OPENAI_API_KEY not set in .env file")
        print("❌ OPENAI_API_KEY not set in .env file")
        print("   → Get your key from: https://platform.openai.com/api-keys")
        print("   → Add to .env: OPENAI_API_KEY=sk-proj-...\n")
    elif openai_key == "your_openai_api_key_here":
        issues.append("❌ OPENAI_API_KEY still has placeholder value")
        print("❌ OPENAI_API_KEY still has placeholder value")
        print("   → Replace with your actual API key from OpenAI\n")
    elif not openai_key.startswith("sk-"):
        warnings.append("⚠️ OPENAI_API_KEY format looks incorrect")
        print(f"⚠️ OPENAI_API_KEY format looks incorrect (should start with 'sk-')")
        print(f"   Current value starts with: {openai_key[:10]}...\n")
    else:
        print(f"✅ OPENAI_API_KEY is set (starts with: {openai_key[:10]}...)\n")
    
    # Check Tavily API key (optional)
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        print("ℹ️  TAVILY_API_KEY not set (optional for web search)")
        print("   → Get from: https://tavily.com\n")
    else:
        print(f"✅ TAVILY_API_KEY is set (starts with: {tavily_key[:10]}...)\n")
    
    # Check required directories
    data_dir = Path("data")
    if not data_dir.exists():
        print("⚠️ data/ directory not found, will be created")
        data_dir.mkdir(exist_ok=True)
    else:
        print("✅ data/ directory exists")
    
    # Check sample data
    sample_data = data_dir / "demo_patient_record.txt"
    if sample_data.exists():
        print("✅ Sample patient record found\n")
    else:
        warnings.append("⚠️ Sample patient record not found")
        print("⚠️ Sample patient record not found (data/demo_patient_record.txt)\n")
    
    # Check dependencies
    try:
        import streamlit
        print("✅ streamlit installed")
    except ImportError:
        issues.append("❌ streamlit not installed")
        print("❌ streamlit not installed")
        print("   → Run: pip install -r requirements.txt\n")
    
    try:
        import openai
        print("✅ openai installed")
    except ImportError:
        issues.append("❌ openai not installed")
        print("❌ openai not installed")
        print("   → Run: pip install -r requirements.txt\n")
    
    try:
        import pydantic
        print("✅ pydantic installed\n")
    except ImportError:
        issues.append("❌ pydantic not installed")
        print("❌ pydantic not installed")
        print("   → Run: pip install -r requirements.txt\n")
    
    # Summary
    print("=" * 60)
    if issues:
        print(f"\n🚨 Found {len(issues)} critical issue(s) that must be fixed:")
        for issue in issues:
            print(f"   {issue}")
        print("\n❌ Setup incomplete. Fix the issues above before running the app.\n")
        return False
    elif warnings:
        print(f"\n⚠️ Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   {warning}")
        print("\n✅ Setup looks good! You can run the app with: streamlit run streamlit_app.py\n")
        return True
    else:
        print("\n✅ All checks passed! Setup is complete.")
        print("🚀 Run the app with: streamlit run streamlit_app.py\n")
        return True


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📄 Loaded .env file\n")
    except ImportError:
        print("ℹ️  python-dotenv not installed (optional)\n")
    except Exception as e:
        print(f"⚠️  Could not load .env: {e}\n")
    
    check_environment()
