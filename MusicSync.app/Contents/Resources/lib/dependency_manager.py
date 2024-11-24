# dependency_manager.py
import subprocess
import json
import os
import sys
import venv
import signal
import atexit
from datetime import datetime, timedelta

class AppBundleCreator:
    def __init__(self):
        # [Previous initialization code]
        self.dependency_manager = DependencyManager()

    def create_bundle(self):
        """Create the app bundle structure"""
        print(f"Creating app bundle: {self.bundle_path}")
        
        # Check system and Python dependencies first
        if not self.dependency_manager.check_dependencies():
            print("Failed to install required dependencies.")
            return False
        
        try:
            # Create directory structure
            os.makedirs(self.macos_path, exist_ok=True)
            os.makedirs(self.lib_path, exist_ok=True)
            
            # Create virtual environment
            print("Creating virtual environment...")
            venv.create(self.venv_path, with_pip=True)
            
            # Create launch script
            self.create_launch_script()
            
            # Copy application files
            self.copy_application_files()
            
            # Install dependencies in the virtual environment
            self.install_bundle_dependencies()
            
            # Create Info.plist
            self.create_info_plist()
            
            # Create symlink with spaces
            self.create_symlink()
            
            print("App bundle creation complete!")
            print(f"To run the app, use: open '{self.app_name}.app'")
            return True
            
        except Exception as e:
            print(f"Error creating bundle: {e}")
            return False

    def install_bundle_dependencies(self):
        """Install dependencies in the bundle's virtual environment"""
        print("Installing bundle dependencies...")
        pip_path = os.path.join(self.venv_path, "bin", "pip")
        
        # First ensure system dependencies are met
        if not self.dependency_manager.check_system_dependencies():
            raise Exception("Failed to install required system dependencies")

        # Then install Python packages
        dependencies = [
            "PyQt6>=6.4.0",
            "PyQt6-Qt6>=6.4.0",
            "mutagen>=1.46.0",
            "watchdog>=2.1.0",
            "pyloudnorm>=0.1.0",
            "SQLAlchemy>=2.0.0",
            "musicbrainzngs>=0.7.1",
            "chromaprint-python>=0.1.0",
            "spotipy>=2.23.0",
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "soundfile>=0.10.0",
            "pytaglib>=1.4.6",
            "tinytag>=1.8.1"
        ]
        
        for dep in dependencies:
            print(f"Installing {dep}")
            try:
                subprocess.run([pip_path, "install", dep], check=True)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to install {dep}: {e}")