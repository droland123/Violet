#!/usr/bin/env python3
import subprocess
import json
import os
import sys
import venv
import stat
import shutil
import logging
from datetime import datetime
from pathlib import Path
from error_handler import log_error, ErrorLogger

# Configure logging with different levels for different types of messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_bundle_creator.log')
    ]
)
logger = logging.getLogger('AppBundleCreator')

class AppBundleError(Exception):
    """Custom exception for app bundle creation errors"""
    pass

class AppBundleCreator:
    """Creates a macOS app bundle with Python environment and dependencies"""
    
    def __init__(self):
        # Basic app information
        self.app_name = "Music Sync"
        self.internal_name = "MusicSync"
        
        # Directory paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bundle_path = f"{self.internal_name}.app"
        self.contents_path = os.path.join(self.bundle_path, "Contents")
        self.macos_path = os.path.join(self.contents_path, "MacOS")
        self.resources_path = os.path.join(self.contents_path, "Resources")
        self.lib_path = os.path.join(self.resources_path, "lib")
        self.venv_path = os.path.join(self.resources_path, "venv")
        
        # Required Python packages
        self.dependencies = [
            "PyQt6>=6.4.0",
            "PyQt6-Qt6>=6.4.0",
            "mutagen>=1.46.0",
            "watchdog>=2.1.0",
            "pyloudnorm>=0.1.0",
            "SQLAlchemy>=2.0.0",
            "musicbrainzngs>=0.7.1",
            "pyacoustid>=1.2.0",
            "spotipy>=2.23.0",
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "soundfile>=0.10.0",
            "tinytag>=1.8.1"
        ]
        
        # Required system (Homebrew) packages
        self.system_packages = ['chromaprint', 'ffmpeg']

    @log_error
    def verify_system_access(self):
        """Verify system access and install required system dependencies"""
        # Check write access
        test_file = os.path.join(self.base_dir, ".write_test")
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except (IOError, OSError) as e:
            raise AppBundleError(f"No write access to current directory: {e}")

        # macOS-specific checks
        if sys.platform == 'darwin':
            try:
                # Check for Homebrew
                subprocess.run(['brew', '--version'], 
                             capture_output=True, 
                             check=True)
            except subprocess.CalledProcessError:
                raise AppBundleError("Homebrew is not installed")
            
            # Install required Homebrew packages
            for package in self.system_packages:
                try:
                    # Check if package is installed
                    subprocess.run(['brew', 'list', package], 
                                 capture_output=True, 
                                 check=True)
                    logger.info(f"Found system package: {package}")
                except subprocess.CalledProcessError:
                    # Install if not found
                    logger.info(f"Installing system package: {package}")
                    try:
                        subprocess.run(['brew', 'install', package], check=True)
                    except subprocess.CalledProcessError as e:
                        raise AppBundleError(f"Failed to install {package}: {e}")

        return True

    @log_error
    def cleanup_existing(self):
        """Remove any existing app bundles"""
        paths_to_remove = [
            f"{self.app_name}.app",
            self.bundle_path
        ]
        
        for path in paths_to_remove:
            if os.path.exists(path):
                logger.info(f"Removing existing bundle: {path}")
                try:
                    if os.path.islink(path):
                        os.unlink(path)
                    else:
                        shutil.rmtree(path)
                except Exception as e:
                    logger.warning(f"Error removing {path}: {e}")
        
        return True

    @log_error
    def create_directory_structure(self):
        """Create the app bundle directory structure"""
        os.makedirs(self.macos_path, exist_ok=True)
        os.makedirs(self.lib_path, exist_ok=True)
        return True

    @log_error
    def create_virtual_environment(self):
        """Create and initialize virtual environment"""
        logger.info("Creating virtual environment...")
        venv.create(self.venv_path, with_pip=True)
        
        # Upgrade pip
        pip_path = os.path.join(self.venv_path, "bin", "pip")
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        return True

    @log_error
    def install_dependencies(self):
        """Install Python package dependencies"""
        pip_path = os.path.join(self.venv_path, "bin", "pip")
        logger.info("Installing dependencies...")
        
        for dep in self.dependencies:
            logger.info(f"Installing {dep}")
            try:
                subprocess.run([pip_path, "install", dep], 
                             check=True,
                             capture_output=True,
                             text=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {dep}: {e.stdout}\n{e.stderr}")
                return False
        
        return True

    @log_error
    def create_launch_script(self):
        """Create the application launch script"""
        launch_script = f'''#!/bin/bash
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
VENV_PATH="$DIR/../Resources/venv"
export PYTHONPATH="$DIR/../Resources/lib"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Set environment variables for system libraries
export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"

# Launch application
exec "$VENV_PATH/bin/python3" "$DIR/../Resources/lib/main.py" "$@"
'''
        
        launch_script_path = os.path.join(self.macos_path, self.internal_name)
        with open(launch_script_path, "w") as f:
            f.write(launch_script)
        
        # Make launch script executable
        os.chmod(launch_script_path, 
                os.stat(launch_script_path).st_mode | 
                stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        return True

    @log_error
    def copy_application_files(self):
        """Copy application files to bundle"""
        logger.info("Copying application files...")
        
        # Copy Python files
        python_files = [f for f in os.listdir(self.base_dir) 
                       if f.endswith('.py')]
        for file in python_files:
            shutil.copy2(
                os.path.join(self.base_dir, file),
                self.lib_path
            )
        
        # Copy application directories
        directories = ['config', 'database', 'gui', 'media', 'services']
        for directory in directories:
            src_dir = os.path.join(self.base_dir, directory)
            if os.path.exists(src_dir):
                dst_dir = os.path.join(self.lib_path, directory)
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
        
        return True

    @log_error
    def create_info_plist(self):
        """Create the Info.plist file for macOS"""
        info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.musicsync.app</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>{self.internal_name}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.music</string>
</dict>
</plist>'''

        plist_path = os.path.join(self.contents_path, "Info.plist")
        with open(plist_path, "w") as f:
            f.write(info_plist)
        
        return True

    @log_error
    def create_symlink(self):
        """Create symlink with spaces in name"""
        symlink_path = f"{self.app_name}.app"
        if os.path.exists(symlink_path):
            os.unlink(symlink_path)
        os.symlink(self.bundle_path, symlink_path)
        return True

    @log_error
    def verify_bundle(self):
        """Verify the created bundle structure and files"""
        required_paths = [
            self.bundle_path,
            self.macos_path,
            self.lib_path,
            self.venv_path,
            os.path.join(self.macos_path, self.internal_name),
            os.path.join(self.contents_path, "Info.plist"),
            os.path.join(self.lib_path, "main.py")
        ]
        
        for path in required_paths:
            if not os.path.exists(path):
                raise AppBundleError(f"Missing required path: {path}")
        
        # Verify virtual environment
        python_path = os.path.join(self.venv_path, "bin", "python3")
        if not os.path.exists(python_path):
            raise AppBundleError("Virtual environment not properly created")
        
        return True

    def create_bundle(self):
        """Create the complete app bundle"""
        steps = [
            (self.verify_system_access, "System access verification"),
            (self.cleanup_existing, "Cleanup of existing bundle"),
            (self.create_directory_structure, "Directory structure creation"),
            (self.create_virtual_environment, "Virtual environment creation"),
            (self.install_dependencies, "Dependency installation"),
            (self.create_launch_script, "Launch script creation"),
            (self.copy_application_files, "Application file copying"),
            (self.create_info_plist, "Info.plist creation"),
            (self.create_symlink, "Symlink creation"),
            (self.verify_bundle, "Bundle verification")
        ]
        
        for step_func, step_name in steps:
            logger.info(f"Starting {step_name}...")
            if not step_func():
                logger.error(f"Failed at: {step_name}")
                return False
            logger.info(f"Completed {step_name}")
        
        logger.info("App bundle creation complete!")
        logger.info(f"To run the app, use: open '{self.app_name}.app'")
        return True

def main():
    """Main entry point"""
    try:
        creator = AppBundleCreator()
        success = creator.create_bundle()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()