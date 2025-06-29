"""
Autonomous Vehicle Simulator

Advanced autonomous vehicle simulation with PyQt5 GUI, AI path planning, and real-time physics.
"""

__version__ = "1.0.0"
__author__ = "sherin joseph roy"
__email__ = "sherin.joseph@gmail.com"
__description__ = "Advanced autonomous vehicle simulation with PyQt5 GUI, AI path planning, and real-time physics"

# Import main components for easy access
from .core.config_manager import ConfigManager
from .core.simulation_manager import SimulationManager
from .core.data_manager import DataManager
from .gui.main_window import MainWindow

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "ConfigManager",
    "SimulationManager", 
    "DataManager",
    "MainWindow",
]

# Core modules
from .core import *
from .gui import *
from .simulation import *
from .sensors import *
from .visualization import *
from .algorithms import *
from .utils import * 