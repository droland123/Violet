# setup_system.py
import subprocess
import sys
import os

def setup_macos():
    """Setup system dependencies on macOS"""
    try:
        # Check for Homebrew
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            print("Homebrew is installed")
        except subprocess.CalledProcessError:
            print("Installing Homebrew...")
            subprocess.run([
                "/bin/bash", 
                "-c", 
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            ])

        # Install required system packages
        packages = [
            "ffmpeg",
            "chromaprint",
            "taglib"
        ]

        for package in packages:
            print(f"Installing {package}...")
            subprocess.run(["brew", "install", package], check=True)

        print("\nSystem dependencies installed successfully!")
        print("You can now run create_app_bundle.py")

    except Exception as e:
        print(f"Error setting up system dependencies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "darwin":
        setup_macos()
    else:
        print("This script is for macOS only")