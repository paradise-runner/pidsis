#!/usr/bin/env python
"""Launcher script for the pidsis Streamlit app."""
import os
import sys
import streamlit.web.cli as stcli
from pathlib import Path

def main():
    """Run the Streamlit app."""
    # Get the directory of this script
    current_dir = Path(__file__).parent
    
    # Path to the app module
    app_path = current_dir / "pidsis" / "run_app.py"
    
    if not app_path.exists():
        print(f"Error: App file not found at {app_path}", file=sys.stderr)
        return 1
    
    # Launch the Streamlit app
    sys.argv = ["streamlit", "run", str(app_path), "--server.headless", "true"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()