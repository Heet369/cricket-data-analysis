"""
Root entry point for Streamlit Cloud deployment.
Loads and runs the main app from the web app directory.
"""
import sys
import os
from pathlib import Path

# Add web app directory to Python path (handles spaces in directory names)
web_app_dir = Path(__file__).parent / "web app"
sys.path.insert(0, str(web_app_dir))

# Change working directory so relative imports work
os.chdir(web_app_dir)

# Import and run the main app
import importlib.util
spec = importlib.util.spec_from_file_location("main_app", web_app_dir / "app.py")
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

# Run main function if it exists
if hasattr(main_app, 'main'):
    main_app.main()
