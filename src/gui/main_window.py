"""
Main application window for the autonomous vehicle simulator.
"""

import sys
import logging
from typing import Dict, Any, Optional, List
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QDockWidget, QToolBar, QStatusBar, 
    QMenuBar, QAction, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QTabWidget, QMessageBox, QFileDialog, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

from ..core import ConfigManager, SimulationManager, DataManager
from .panels.control_panel import ControlPanel
from .panels.sensor_panel import SensorPanel
from .panels.scene_tree import SceneTreePanel
from .panels.property_inspector import PropertyInspectorPanel
from .panels.timeline import TimelinePanel
from .panels.ai_navigation_panel import AINavigationPanel
from .visualization.viewport_3d import Viewport3D
from .widgets.toolbar import MainToolBar


class MainWindow(QMainWindow):
    """Main application window with advanced GUI features."""
    
    # Signals
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    simulation_paused = pyqtSignal()
    simulation_resumed = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager, 
                 simulation_manager: SimulationManager,
                 data_manager: DataManager):
        """
        Initialize the main window.
        
        Args:
            config_manager: Configuration manager
            simulation_manager: Simulation manager
            data_manager: Data manager
        """
        super().__init__()
        
        self.config = config_manager
        self.simulation_manager = simulation_manager
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI
        self.init_ui()
        self.setup_theme()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        self.setup_dock_widgets()
        self.setup_central_widget()
        self.setup_connections()
        
        # Load window state
        self.load_window_state()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(50)  # 20 FPS
        
        self.logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        # Window properties
        self.setWindowTitle(self.config.get('application.name', 'Autonomous Vehicle Simulator'))
        self.setGeometry(100, 100, *self.config.get('application.window_size', [1920, 1080]))
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
    
    def setup_theme(self):
        """Setup the dark theme."""
        # Dark palette
        palette = QPalette()
        
        # Background colors
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.Light, QColor(180, 180, 180))
        palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
        palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        palette.setColor(QPalette.Mid, QColor(45, 45, 45))
        palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Link colors
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.LinkVisited, QColor(130, 42, 218))
        
        # Apply palette
        self.setPalette(palette)
        
        # Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QDockWidget {
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }
            QDockWidget::title {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4a4a4a, stop: 1 #2a2a2a);
                padding-left: 5px;
                padding-top: 2px;
                border: 1px solid #1a1a1a;
            }
            QTabWidget::pane {
                border: 1px solid #1a1a1a;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #ffffff;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
            QTabBar::tab:hover {
                background-color: #5a5a5a;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #1a1a1a;
                color: #ffffff;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #1a1a1a;
                color: #ffffff;
                padding: 3px;
                border-radius: 2px;
            }
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #1a1a1a;
                color: #ffffff;
                padding: 3px;
                border-radius: 2px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #1a1a1a;
                height: 8px;
                background: #2a2a2a;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a4a4a;
                border: 1px solid #1a1a1a;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #5a5a5a;
            }
            QProgressBar {
                border: 1px solid #1a1a1a;
                border-radius: 3px;
                text-align: center;
                background-color: #2a2a2a;
            }
            QProgressBar::chunk {
                background-color: #4a4a4a;
                border-radius: 2px;
            }
            QTreeWidget, QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #1a1a1a;
                color: #ffffff;
                alternate-background-color: #3a3a3a;
            }
            QTreeWidget::item:selected, QListWidget::item:selected {
                background-color: #4a4a4a;
            }
            QTreeWidget::item:hover, QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
    
    def setup_menus(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New Scenario', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_scenario)
        file_menu.addAction(new_action)
        
        open_action = QAction('&Open Scenario', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_scenario)
        file_menu.addAction(open_action)
        
        save_action = QAction('&Save Scenario', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_scenario)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('&Export Data', self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Simulation menu
        sim_menu = menubar.addMenu('&Simulation')
        
        start_action = QAction('&Start', self)
        start_action.setShortcut('F5')
        start_action.triggered.connect(self.start_simulation)
        sim_menu.addAction(start_action)
        
        pause_action = QAction('&Pause', self)
        pause_action.setShortcut('F6')
        pause_action.triggered.connect(self.pause_simulation)
        sim_menu.addAction(pause_action)
        
        stop_action = QAction('S&top', self)
        stop_action.setShortcut('F7')
        stop_action.triggered.connect(self.stop_simulation)
        sim_menu.addAction(stop_action)
        
        reset_action = QAction('&Reset', self)
        reset_action.setShortcut('F8')
        reset_action.triggered.connect(self.reset_simulation)
        sim_menu.addAction(reset_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        # Add view actions for dock widgets
        self.view_actions = {}
        for dock_name in ['control_panel', 'sensor_panel', 'scene_tree', 'property_inspector', 'timeline', 'ai_navigation']:
            action = QAction(f'&{dock_name.replace("_", " ").title()}', self)
            action.setCheckable(True)
            action.setChecked(True)
            self.view_actions[dock_name] = action
            view_menu.addAction(action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbars(self):
        """Setup the toolbars."""
        # Main toolbar
        self.main_toolbar = MainToolBar(self)
        self.addToolBar(self.main_toolbar)
        
        # Simulation toolbar
        self.sim_toolbar = QToolBar('Simulation')
        self.addToolBar(self.sim_toolbar)
        
        # Add simulation controls to toolbar
        self.sim_toolbar.addAction(self.findChild(QAction, 'start_action'))
        self.sim_toolbar.addAction(self.findChild(QAction, 'pause_action'))
        self.sim_toolbar.addAction(self.findChild(QAction, 'stop_action'))
        self.sim_toolbar.addAction(self.findChild(QAction, 'reset_action'))
    
    def setup_statusbar(self):
        """Setup the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Status indicators
        self.sim_status_label = QLabel('Stopped')
        self.fps_label = QLabel('FPS: 0')
        self.time_label = QLabel('Time: 0.00s')
        
        self.statusbar.addWidget(self.sim_status_label)
        self.statusbar.addPermanentWidget(self.fps_label)
        self.statusbar.addPermanentWidget(self.time_label)
    
    def setup_dock_widgets(self):
        """Setup the docked widgets."""
        self.dock_widgets = {}
        
        # Control Panel (Left)
        self.control_panel = ControlPanel(self.config, self.simulation_manager)
        self.control_dock = QDockWidget('Control Panel', self)
        self.control_dock.setWidget(self.control_panel)
        self.control_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.control_dock)
        self.dock_widgets['control_panel'] = self.control_dock
        
        # Sensor Panel (Right)
        self.sensor_panel = SensorPanel(self.config, self.data_manager)
        self.sensor_dock = QDockWidget('Sensor Data', self)
        self.sensor_dock.setWidget(self.sensor_panel)
        self.sensor_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sensor_dock)
        self.dock_widgets['sensor_panel'] = self.sensor_dock
        
        # Scene Tree (Left)
        self.scene_tree = SceneTreePanel(self.config)
        self.scene_dock = QDockWidget('Scene Tree', self)
        self.scene_dock.setWidget(self.scene_tree)
        self.scene_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.scene_dock)
        self.dock_widgets['scene_tree'] = self.scene_dock
        
        # Property Inspector (Right)
        self.property_inspector = PropertyInspectorPanel(self.config)
        self.property_dock = QDockWidget('Property Inspector', self)
        self.property_dock.setWidget(self.property_inspector)
        self.property_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.property_dock)
        self.dock_widgets['property_inspector'] = self.property_dock
        
        # Timeline (Bottom)
        self.timeline = TimelinePanel(self.config, self.data_manager)
        self.timeline_dock = QDockWidget('Timeline', self)
        self.timeline_dock.setWidget(self.timeline)
        self.timeline_dock.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline_dock)
        self.dock_widgets['timeline'] = self.timeline_dock
        
        # AI Navigation Panel
        self.ai_navigation_panel = AINavigationPanel(self.config, self.simulation_manager)
        self.ai_navigation_dock = QDockWidget("AI Navigation", self)
        self.ai_navigation_dock.setWidget(self.ai_navigation_panel)
        self.ai_navigation_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ai_navigation_dock)
    
    def setup_central_widget(self):
        """Setup the central 3D viewport."""
        # Create splitter for central area
        self.central_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.central_splitter)
        
        # 3D Viewport
        self.viewport_3d = Viewport3D(self.config, self.simulation_manager)
        self.central_splitter.addWidget(self.viewport_3d)
        
        # Set initial splitter sizes
        self.central_splitter.setSizes([800, 200])
    
    def setup_connections(self):
        """Setup signal connections."""
        # Simulation manager connections
        self.simulation_manager.add_event_callback('start', self.on_simulation_started)
        self.simulation_manager.add_event_callback('stop', self.on_simulation_stopped)
        self.simulation_manager.add_event_callback('pause', self.on_simulation_paused)
        self.simulation_manager.add_event_callback('resume', self.on_simulation_resumed)
        
        # Control panel connections
        self.control_panel.simulation_control_changed.connect(self.on_simulation_control_changed)
        
        # Viewport connections
        self.viewport_3d.camera_changed.connect(self.on_camera_changed)
        
        # Dock widget visibility connections
        for dock_name, dock_widget in self.dock_widgets.items():
            dock_widget.visibilityChanged.connect(
                lambda visible, name=dock_name: self.on_dock_visibility_changed(name, visible)
            )
        
        # AI navigation connections
        self.ai_navigation_panel.target_set.connect(self.on_target_set)
        self.ai_navigation_panel.ai_navigation_toggled.connect(self.on_ai_navigation_toggled)
        self.ai_navigation_panel.obstacle_added.connect(self.on_obstacle_added)
    
    def load_window_state(self):
        """Load window state from configuration."""
        # Load dock widget positions and sizes
        for dock_name, dock_widget in self.dock_widgets.items():
            visible = self.config.get(f'gui.panels.{dock_name}.visible', True)
            dock_widget.setVisible(visible)
            
            if dock_name in self.view_actions:
                self.view_actions[dock_name].setChecked(visible)
    
    def save_window_state(self):
        """Save window state to configuration."""
        # Save dock widget visibility
        for dock_name, dock_widget in self.dock_widgets.items():
            self.config.set(f'gui.panels.{dock_name}.visible', dock_widget.isVisible())
        
        # Save window size
        self.config.set('application.window_size', [self.width(), self.height()])
        self.config.save_config()
    
    def update_ui(self):
        """Update UI elements."""
        # Update status bar
        stats = self.simulation_manager.get_stats()
        self.fps_label.setText(f'FPS: {stats.fps:.1f}')
        self.time_label.setText(f'Time: {stats.simulation_time:.2f}s')
        
        # Update simulation status
        state = self.simulation_manager.get_state()
        if state.value == 'running':
            self.sim_status_label.setText('Running')
            self.sim_status_label.setStyleSheet('color: #00ff00;')
        elif state.value == 'paused':
            self.sim_status_label.setText('Paused')
            self.sim_status_label.setStyleSheet('color: #ffff00;')
        else:
            self.sim_status_label.setText('Stopped')
            self.sim_status_label.setStyleSheet('color: #ff0000;')
    
    # Menu actions
    def new_scenario(self):
        """Create a new scenario."""
        self.logger.info("Creating new scenario")
        # TODO: Implement new scenario creation
    
    def open_scenario(self):
        """Open a scenario file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Scenario', '', 'Scenario Files (*.yaml *.json);;All Files (*)'
        )
        if file_path:
            self.logger.info(f"Opening scenario: {file_path}")
            # TODO: Implement scenario loading
    
    def save_scenario(self):
        """Save the current scenario."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Scenario', '', 'Scenario Files (*.yaml *.json);;All Files (*)'
        )
        if file_path:
            self.logger.info(f"Saving scenario: {file_path}")
            # TODO: Implement scenario saving
    
    def export_data(self):
        """Export simulation data."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Export Data', '', 'Data Files (*.pcd *.json *.csv);;All Files (*)'
        )
        if file_path:
            self.logger.info(f"Exporting data: {file_path}")
            # TODO: Implement data export
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, 'About',
            f'{self.config.get("application.name")}\n'
            f'Version: {self.config.get("application.version")}\n\n'
            'Advanced Autonomous Vehicle Simulator\n'
            'Built with PyQt5 and OpenGL'
        )
    
    # Simulation control actions
    def start_simulation(self):
        """Start the simulation."""
        self.simulation_manager.start()
    
    def pause_simulation(self):
        """Pause the simulation."""
        self.simulation_manager.pause()
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.simulation_manager.stop()
    
    def reset_simulation(self):
        """Reset the simulation."""
        self.simulation_manager.reset()
    
    # Event handlers
    def on_simulation_started(self):
        """Handle simulation started event."""
        self.simulation_started.emit()
        self.logger.info("Simulation started")
    
    def on_simulation_stopped(self):
        """Handle simulation stopped event."""
        self.simulation_stopped.emit()
        self.logger.info("Simulation stopped")
    
    def on_simulation_paused(self):
        """Handle simulation paused event."""
        self.simulation_paused.emit()
        self.logger.info("Simulation paused")
    
    def on_simulation_resumed(self):
        """Handle simulation resumed event."""
        self.simulation_resumed.emit()
        self.logger.info("Simulation resumed")
    
    def on_simulation_control_changed(self, control_type: str, value: Any):
        """Handle simulation control changes."""
        self.logger.info(f"Simulation control changed: {control_type} = {value}")
        # TODO: Implement control change handling
    
    def on_camera_changed(self, camera_data: Dict[str, Any]):
        """Handle camera changes."""
        self.logger.info(f"Camera changed: {camera_data}")
        # TODO: Implement camera change handling
    
    def on_dock_visibility_changed(self, dock_name: str, visible: bool):
        """Handle dock widget visibility changes."""
        if dock_name in self.view_actions:
            self.view_actions[dock_name].setChecked(visible)
        self.logger.info(f"Dock widget {dock_name} visibility: {visible}")
    
    def on_target_set(self, target: List[float]):
        """Handle target position set from AI navigation panel."""
        # Update 3D viewport camera to focus on target
        self.viewport_3d.set_camera(target=target)
        
        # Update scene tree if needed
        # This could add the target as a visual marker in the scene

    def on_ai_navigation_toggled(self, enabled: bool):
        """Handle AI navigation toggle."""
        if enabled:
            # Enable AI navigation in simulation
            self.simulation_manager.ai_navigation_enabled = True
        else:
            # Disable AI navigation
            self.simulation_manager.ai_navigation_enabled = False
            # Stop vehicle
            self.simulation_manager.set_vehicle_control(0.0, 0.0, 0.0)

    def on_obstacle_added(self, position: List[float], radius: float, obstacle_type: str):
        """Handle obstacle added from AI navigation panel."""
        # Add obstacle to scene tree
        obstacle_name = f"Obstacle_{len(self.simulation_manager.obstacle_avoidance.obstacles)}"
        obstacle_data = {
            'type': 'obstacle',
            'name': obstacle_name,
            'position': position,
            'orientation': [0, 0, 0],
            'obstacle_type': obstacle_type,
            'radius': radius,
            'visible': True
        }
        
        # Add to scene tree panel
        self.scene_tree.add_object("obstacle", obstacle_name)
        
        # Update 3D viewport
        self.viewport_3d.add_object(obstacle_name, obstacle_data)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.save_window_state()
        self.simulation_manager.stop()
        event.accept()

    def show(self):
        """Show the window maximized."""
        super().show()
        self.showMaximized() 