"""
Root entry point for Streamlit Cloud deployment.
This imports and runs the main app from the web app directory.
"""
import sys
import os

# Add web app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web app'))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
