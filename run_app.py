# """
# Helper script to run Streamlit with environment variables loaded
# """

# import os
# from dotenv import load_dotenv
# import subprocess
# import sys

# # Load environment variables
# load_dotenv(override=True)

# # Verify API key is loaded
# api_key = os.getenv("OPENAI_API_KEY", "")
# if not api_key:
#     print("❌ ERROR: OPENAI_API_KEY not found in .env file!")
#     print("\nPlease ensure your .env file exists and contains:")
#     print("OPENAI_API_KEY=sk-proj-your-key-here")
#     sys.exit(1)

# print(f"✅ API Key loaded: {api_key[:7]}...{api_key[-4:]}")
# print("🚀 Starting Streamlit...\n")

# # Run Streamlit with environment variables
# subprocess.run(["streamlit", "run", "streamlit_app.py"])
