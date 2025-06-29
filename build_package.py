#!/usr/bin/env python3
"""
Build Autonomous Vehicle Simulator Package
"""

import os
import sys
import subprocess
import shutil
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

def clean_build_dirs():
    """Clean build and dist directories."""
    print("Cleaning build directories...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    
    for dir_pattern in dirs_to_clean:
        for path in Path(".").glob(dir_pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing {path}")
                path.unlink()
    
    print("✓ Build directories cleaned")

def check_dependencies():
    """Check if required build dependencies are installed."""
    print("Checking build dependencies...")
    
    required_packages = ["setuptools", "wheel", "twine", "build"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        install_command = [sys.executable, "-m", "pip", "install"] + missing_packages
        if not run_command(install_command, "Install missing packages"):
            return False
    
    return True

def validate_package():
    """Validate the package structure."""
    print("Validating package structure...")
    
    required_files = [
        "pyproject.toml",
        "setup.py", 
        "MANIFEST.in",
        "README.md",
        "LICENSE",
        "requirements.txt",
        "src/main.py",
        "src/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"✗ Missing: {file_path}")
        else:
            print(f"✓ Found: {file_path}")
    
    if missing_files:
        print(f"\n✗ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✓ Package structure is valid")
    return True

def build_package():
    """Build the package."""
    print("Building package...")
    
    # Use modern build system
    build_command = [sys.executable, "-m", "build"]
    if not run_command(build_command, "Build package"):
        return False
    
    return True

def check_built_package():
    """Check the built package."""
    print("Checking built package...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("✗ dist directory not found")
        return False
    
    # List built files
    built_files = list(dist_dir.glob("*"))
    if not built_files:
        print("✗ No built files found")
        return False
    
    print("Built files:")
    for file_path in built_files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"  {file_path.name} ({size_mb:.2f} MB)")
    
    # Check with twine
    check_command = [sys.executable, "-m", "twine", "check", "dist/*"]
    if not run_command(check_command, "Twine check"):
        return False
    
    return True

def main():
    """Main build process."""
    print("=" * 60)
    print("Autonomous Vehicle Simulator - Package Builder")
    print("=" * 60)
    
    # Clean build directories
    clean_build_dirs()
    
    # Check dependencies
    if not check_dependencies():
        print("✗ Dependency check failed")
        sys.exit(1)
    
    # Validate package structure
    if not validate_package():
        print("✗ Package validation failed")
        sys.exit(1)
    
    # Build package
    if not build_package():
        print("✗ Package build failed")
        sys.exit(1)
    
    # Check built package
    if not check_built_package():
        print("✗ Built package check failed")
        sys.exit(1)
    
    print("=" * 60)
    print("✓ Package built successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test the package locally: pip install dist/*.whl")
    print("2. Publish to TestPyPI: python publish_to_pypi.py")
    print("3. Publish to PyPI: python publish_to_pypi.py")
    print("=" * 60)

if __name__ == "__main__":
    main() 