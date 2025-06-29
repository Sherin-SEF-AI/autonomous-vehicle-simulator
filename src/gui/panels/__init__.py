"""
Panel widgets for the autonomous vehicle simulator.
"""

from .control_panel import ControlPanel
from .sensor_panel import SensorPanel
from .scene_tree import SceneTreePanel
from .property_inspector import PropertyInspectorPanel
from .timeline import TimelinePanel
from .ai_navigation_panel import AINavigationPanel

__all__ = [
    'ControlPanel',
    'SensorPanel', 
    'SceneTreePanel',
    'PropertyInspectorPanel',
    'TimelinePanel',
    'AINavigationPanel',
] 