"""
Root-level entry point for Streamlit Cloud deployment.
This file is a simple redirect to app/main.py
"""
import sys
import os

# Get the project root directory (where this file is located)
project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to the path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Change to project root directory to ensure relative paths work
os.chdir(project_root)

# Import and run the main app
from app.main import main

if __name__ == "__main__":
    main()

