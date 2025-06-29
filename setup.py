#!/usr/bin/env python3
"""
Setup script for Autonomous Vehicle Simulator
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="autonomous-vehicle-simulator",
    version="1.0.0",
    author="Sherin Joseph Roy",
    author_email="sherin.joseph@gmail.com",
    description="Advanced autonomous vehicle simulation with PyQt5 GUI, AI path planning, and real-time physics",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/vision2030/autonomous-vehicle-simulator",
    project_urls={
        "Bug Tracker": "https://github.com/vision2030/autonomous-vehicle-simulator/issues",
        "Documentation": "https://github.com/vision2030/autonomous-vehicle-simulator/blob/main/README.md",
        "Source Code": "https://github.com/vision2030/autonomous-vehicle-simulator",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "autonomous-vehicle-sim=src.main:main",
            "av-sim=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt", "*.md"],
    },
    keywords=[
        "autonomous",
        "vehicle",
        "simulation",
        "robotics",
        "ai",
        "path-planning",
        "physics",
        "pyqt5",
        "3d-visualization",
        "machine-learning",
        "reinforcement-learning",
    ],
    license="MIT",
    platforms=["Linux", "Windows", "macOS"],
) 