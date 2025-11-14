"""
Test script to verify the CareGuide system works end-to-end
Run this before deploying to catch any issues
"""

import sys
from pathlib import Path
import config
from orchestrator import HealthAssessmentOrchestrator


def test_configuration():
    """Test that configuration is properly set up"""
    print("=" * 60)
    print("TESTING CONFIGURATION")
    print("=" * 60)
    
    # Check API key
    if not config.OPENAI_API_KEY:
        print("❌ FAIL: OPENAI_API_KEY not set")
        print("   Please set it in your .env file")
        return False
    print("✅ PASS: OpenAI API key configured")
    
    # Check data files exist
    if not config.PATIENT_DATA_FILE.exists():
        print(f"❌ FAIL: Patient data file not found at {config.PATIENT_DATA_FILE}")
        return False
    print(f"✅ PASS: Patient data file found")
    
    if not config.USPSTF_DATA_FILE.exists():
        print(f"❌ FAIL: USPSTF guidelines file not found at {config.USPSTF_DATA_FILE}")
        return False
    print(f"✅ PASS: USPSTF guidelines file found")
    
    # Check output directory
    if not config.OUTPUT_DIR.exists():
        print(f"❌ FAIL: Output directory not found at {config.OUTPUT_DIR}")
        return False
    print(f"✅ PASS: Output directory exists")
    
    return True


def test_imports():
    """Test that all required packages can be imported"""
    print("\n" + "=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    required_packages = [
        ('openai', 'OpenAI'),
        ('pydantic', 'Pydantic'),
        ('streamlit', 'Streamlit'),
    ]
    
    all_passed = True
    for package_name, display_name in required_packages:
        try:
            __import__(package_name)
            print(f"✅ PASS: {display_name} imported successfully")
        except ImportError:
            print(f"❌ FAIL: {display_name} not installed")
            print(f"   Run: pip install {package_name}")
            all_passed = False
    
    return all_passed


def test_simple_assessment():
    """Test a simple health assessment"""
    print("\n" + "=" * 60)
    print("TESTING ASSESSMENT PIPELINE")
    print("=" * 60)
    print("Running simplified test with sample data...")
    print()
    
    try:
        # Create simple test data
        test_data = """
        Patient: 45-year-old male
        Last colonoscopy: 2023
        Flu shot: October 2023
        Blood pressure: 130/85
        No diabetes
        """
        
        orchestrator = HealthAssessmentOrchestrator()
        
        # Test just the summarization agent
        print("Testing summarization agent...")
        summary = orchestrator.agent_system.create_patient_summary(test_data)
        print(f"✅ Summary created: {summary.basic_summary}")
        
        print("\n✅ PASS: Basic pipeline components working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Pipeline test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "CAREGUIDE - SYSTEM TEST" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests = [
        ("Configuration", test_configuration),
        ("Package Imports", test_imports),
        ("Assessment Pipeline", test_simple_assessment),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Your system is ready for deployment!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Please fix the issues above before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
