"""
Main toolbar widget for the autonomous vehicle simulator.
"""

from PyQt5.QtWidgets import QToolBar, QAction, QWidget, QHBoxLayout, QLabel, QComboBox, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont


class MainToolBar(QToolBar):
    """Main toolbar with simulation controls and common actions."""
    
    # Signals
    simulation_control_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        """Initialize the main toolbar."""
        super().__init__('Main Toolbar', parent)
        
        self.setMovable(True)
        self.setFloatable(False)
        self.setIconSize(QSize(24, 24))
        
        self.setup_actions()
        self.setup_controls()
    
    def setup_actions(self):
        """Setup toolbar actions."""
        # File actions
        self.addAction('New', 'Ctrl+N')
        self.addAction('Open', 'Ctrl+O')
        self.addAction('Save', 'Ctrl+S')
        self.addSeparator()
        
        # Simulation actions
        self.addAction('Start', 'F5')
        self.addAction('Pause', 'F6')
        self.addAction('Stop', 'F7')
        self.addAction('Reset', 'F8')
        self.addSeparator()
        
        # View actions
        self.addAction('Reset View', 'R')
        self.addAction('Toggle Grid', 'G')
        self.addAction('Toggle Axes', 'A')
        self.addSeparator()
        
        # Recording actions
        self.addAction('Start Recording', 'Ctrl+R')
        self.addAction('Stop Recording', 'Ctrl+Shift+R')
    
    def setup_controls(self):
        """Setup toolbar controls."""
        # Time scale control
        self.addWidget(QLabel('Time Scale:'))
        self.time_scale_spin = QSpinBox()
        self.time_scale_spin.setRange(1, 1000)
        self.time_scale_spin.setValue(100)
        self.time_scale_spin.setSuffix('%')
        self.time_scale_spin.valueChanged.connect(
            lambda value: self.simulation_control_changed.emit('time_scale', value / 100.0)
        )
        self.addWidget(self.time_scale_spin)
        
        self.addSeparator()
        
        # Camera mode control
        self.addWidget(QLabel('Camera:'))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(['Free', 'Follow', 'Top', 'First Person'])
        self.camera_combo.currentTextChanged.connect(
            lambda text: self.simulation_control_changed.emit('camera_mode', text)
        )
        self.addWidget(self.camera_combo)
    
    def addAction(self, text: str, shortcut: str = None):
        """Add an action to the toolbar."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(lambda: self.on_action_triggered(text))
        super().addAction(action)
        return action
    
    def on_action_triggered(self, action_name: str):
        """Handle action triggers."""
        self.simulation_control_changed.emit('action', action_name) 