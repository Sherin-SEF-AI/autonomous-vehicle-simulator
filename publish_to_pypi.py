#!/usr/bin/env python3
"""
Publish Autonomous Vehicle Simulator to PyPI
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("Checking prerequisites...")
    
    # Check if dist directory exists
    if not Path("dist").exists():
        print("✗ dist directory not found. Please run build_package.py first.")
        return False
    
    # Check if wheel files exist
    wheel_files = list(Path("dist").glob("*.whl"))
    if not wheel_files:
        print("✗ No wheel files found in dist directory.")
        return False
    
    # Check if source distribution exists
    sdist_files = list(Path("dist").glob("*.tar.gz"))
    if not sdist_files:
        print("✗ No source distribution found in dist directory.")
        return False
    
    print(f"✓ Found {len(wheel_files)} wheel files and {len(sdist_files)} source distributions")
    return True

def check_package():
    """Check the package with twine."""
    print("Checking package with twine...")
    
    if not run_command([sys.executable, "-m", "twine", "check", "dist/*"], "Package check"):
        return False
    
    return True

def upload_to_testpypi():
    """Upload to TestPyPI."""
    print("Uploading to TestPyPI...")
    
    print("Note: You'll need to create a TestPyPI account at https://test.pypi.org/account/register/")
    print("And get an API token from https://test.pypi.org/manage/account/token/")
    
    username = input("Enter your TestPyPI username: ").strip()
    password = getpass.getpass("Enter your TestPyPI password/token: ")
    
    if not username or not password:
        print("✗ Username and password are required")
        return False
    
    # Set environment variables for twine
    env = os.environ.copy()
    env["TWINE_USERNAME"] = username
    env["TWINE_PASSWORD"] = password
    
    command = [sys.executable, "-m", "twine", "upload", "--repository", "testpypi", "dist/*"]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
        print("✓ Upload to TestPyPI completed successfully")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Upload to TestPyPI failed: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def upload_to_pypi():
    """Upload to PyPI."""
    print("Uploading to PyPI...")
    
    print("Note: You'll need to create a PyPI account at https://pypi.org/account/register/")
    print("And get an API token from https://pypi.org/manage/account/token/")
    
    username = input("Enter your PyPI username: ").strip()
    password = getpass.getpass("Enter your PyPI password/token: ")
    
    if not username or not password:
        print("✗ Username and password are required")
        return False
    
    # Set environment variables for twine
    env = os.environ.copy()
    env["TWINE_USERNAME"] = username
    env["TWINE_PASSWORD"] = password
    
    command = [sys.executable, "-m", "twine", "upload", "dist/*"]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
        print("✓ Upload to PyPI completed successfully")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Upload to PyPI failed: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Main publish process."""
    print("=" * 60)
    print("Autonomous Vehicle Simulator - PyPI Publisher")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("✗ Prerequisites not met. Please run build_package.py first.")
        sys.exit(1)
    
    # Check package
    if not check_package():
        print("✗ Package check failed")
        sys.exit(1)
    
    # Ask user what to do
    print("\nChoose an option:")
    print("1. Upload to TestPyPI (recommended for testing)")
    print("2. Upload to PyPI (production)")
    print("3. Both (TestPyPI first, then PyPI)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        if not upload_to_testpypi():
            sys.exit(1)
        print("\n✓ Package uploaded to TestPyPI successfully!")
        print("You can test installation with: pip install --index-url https://test.pypi.org/simple/ autonomous-vehicle-simulator")
        
    elif choice == "2":
        if not upload_to_pypi():
            sys.exit(1)
        print("\n✓ Package uploaded to PyPI successfully!")
        print("You can install with: pip install autonomous-vehicle-simulator")
        
    elif choice == "3":
        if not upload_to_testpypi():
            sys.exit(1)
        print("\n✓ Package uploaded to TestPyPI successfully!")
        
        test_install = input("\nTest the installation from TestPyPI? (y/n): ").strip().lower()
        if test_install == 'y':
            print("Testing installation from TestPyPI...")
            test_command = [
                sys.executable, "-m", "pip", "install", 
                "--index-url", "https://test.pypi.org/simple/",
                "autonomous-vehicle-simulator"
            ]
            if run_command(test_command, "Test installation"):
                print("✓ Test installation successful!")
            else:
                print("✗ Test installation failed. Please check the package before uploading to PyPI.")
                sys.exit(1)
        
        proceed = input("\nProceed with PyPI upload? (y/n): ").strip().lower()
        if proceed == 'y':
            if not upload_to_pypi():
                sys.exit(1)
            print("\n✓ Package uploaded to PyPI successfully!")
            print("You can install with: pip install autonomous-vehicle-simulator")
        else:
            print("PyPI upload cancelled.")
    
    else:
        print("✗ Invalid choice")
        sys.exit(1)
    
    print("=" * 60)
    print("✓ Publishing process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 