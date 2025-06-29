"""
AI Navigation panel for autonomous vehicle path planning and control.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, 
    QDoubleSpinBox, QCheckBox, QFormLayout, QTextEdit, QProgressBar,
    QComboBox, QSpinBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont


class AINavigationPanel(QWidget):
    """AI Navigation panel for path planning and autonomous control."""
    
    # Signals
    target_set = pyqtSignal(list)  # [x, y, z]
    ai_navigation_toggled = pyqtSignal(bool)
    obstacle_added = pyqtSignal(list, float, str)  # position, radius, type
    
    def __init__(self, config_manager, simulation_manager):
        """
        Initialize the AI navigation panel.
        
        Args:
            config_manager: Configuration manager
            simulation_manager: Simulation manager
        """
        super().__init__()
        
        self.config = config_manager
        self.simulation_manager = simulation_manager
        
        self.setup_ui()
        self.setup_connections()
        self.setup_update_timer()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Navigation tab
        self.navigation_tab = self.create_navigation_tab()
        self.tab_widget.addTab(self.navigation_tab, "Navigation")
        
        # Path Planning tab
        self.path_planning_tab = self.create_path_planning_tab()
        self.tab_widget.addTab(self.path_planning_tab, "Path Planning")
        
        # Obstacles tab
        self.obstacles_tab = self.create_obstacles_tab()
        self.tab_widget.addTab(self.obstacles_tab, "Obstacles")
        
        # Statistics tab
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "Statistics")
    
    def create_navigation_tab(self):
        """Create the navigation control tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI Navigation Control
        nav_group = QGroupBox("AI Navigation Control")
        nav_layout = QVBoxLayout(nav_group)
        
        self.ai_enabled = QCheckBox("Enable AI Navigation")
        self.ai_enabled.setChecked(False)
        nav_layout.addWidget(self.ai_enabled)
        
        self.emergency_stop = QPushButton("🛑 Emergency Stop")
        self.emergency_stop.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; font-weight: bold; }")
        nav_layout.addWidget(self.emergency_stop)
        
        layout.addWidget(nav_group)
        
        # Target Position
        target_group = QGroupBox("Target Position")
        target_layout = QFormLayout(target_group)
        
        self.target_x = QDoubleSpinBox()
        self.target_x.setRange(-1000, 1000)
        self.target_x.setValue(0)
        self.target_x.setSuffix(" m")
        target_layout.addRow("X:", self.target_x)
        
        self.target_y = QDoubleSpinBox()
        self.target_y.setRange(-1000, 1000)
        self.target_y.setValue(0)
        self.target_y.setSuffix(" m")
        target_layout.addRow("Y:", self.target_y)
        
        self.target_z = QDoubleSpinBox()
        self.target_z.setRange(-1000, 1000)
        self.target_z.setValue(0)
        self.target_z.setSuffix(" m")
        target_layout.addRow("Z:", self.target_z)
        
        # Target buttons
        target_buttons = QHBoxLayout()
        
        self.set_target_button = QPushButton("Set Target")
        target_buttons.addWidget(self.set_target_button)
        
        self.clear_target_button = QPushButton("Clear Target")
        target_buttons.addWidget(self.clear_target_button)
        
        target_layout.addRow("", target_buttons)
        
        layout.addWidget(target_group)
        
        # Quick Targets
        quick_group = QGroupBox("Quick Targets")
        quick_layout = QVBoxLayout(quick_group)
        
        quick_buttons = QHBoxLayout()
        
        self.target_forward = QPushButton("Forward (50m)")
        quick_buttons.addWidget(self.target_forward)
        
        self.target_left = QPushButton("Left (30m)")
        quick_buttons.addWidget(self.target_left)
        
        quick_layout.addLayout(quick_buttons)
        
        quick_buttons2 = QHBoxLayout()
        
        self.target_right = QPushButton("Right (30m)")
        quick_buttons2.addWidget(self.target_right)
        
        self.target_back = QPushButton("Back (50m)")
        quick_buttons2.addWidget(self.target_back)
        
        quick_layout.addLayout(quick_buttons2)
        
        layout.addWidget(quick_group)
        
        layout.addStretch()
        return widget
    
    def create_path_planning_tab(self):
        """Create the path planning configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Algorithm Selection
        algo_group = QGroupBox("Path Planning Algorithm")
        algo_layout = QFormLayout(algo_group)
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(['RRT', 'A*'])
        algo_layout.addRow("Algorithm:", self.algorithm_combo)
        
        layout.addWidget(algo_group)
        
        # RRT Parameters
        rrt_group = QGroupBox("RRT Parameters")
        rrt_layout = QFormLayout(rrt_group)
        
        self.rrt_max_iterations = QSpinBox()
        self.rrt_max_iterations.setRange(100, 10000)
        self.rrt_max_iterations.setValue(1000)
        rrt_layout.addRow("Max Iterations:", self.rrt_max_iterations)
        
        self.rrt_step_size = QDoubleSpinBox()
        self.rrt_step_size.setRange(0.1, 10.0)
        self.rrt_step_size.setValue(1.0)
        self.rrt_step_size.setSuffix(" m")
        rrt_layout.addRow("Step Size:", self.rrt_step_size)
        
        self.rrt_goal_bias = QDoubleSpinBox()
        self.rrt_goal_bias.setRange(0.0, 1.0)
        self.rrt_goal_bias.setValue(0.1)
        self.rrt_goal_bias.setSingleStep(0.01)
        rrt_layout.addRow("Goal Bias:", self.rrt_goal_bias)
        
        layout.addWidget(rrt_group)
        
        # A* Parameters
        astar_group = QGroupBox("A* Parameters")
        astar_layout = QFormLayout(astar_group)
        
        self.astar_grid_resolution = QDoubleSpinBox()
        self.astar_grid_resolution.setRange(0.1, 2.0)
        self.astar_grid_resolution.setValue(0.5)
        self.astar_grid_resolution.setSuffix(" m")
        astar_layout.addRow("Grid Resolution:", self.astar_grid_resolution)
        
        self.astar_heuristic = QComboBox()
        self.astar_heuristic.addItems(['euclidean', 'manhattan'])
        astar_layout.addRow("Heuristic:", self.astar_heuristic)
        
        layout.addWidget(astar_group)
        
        # Path Planning Control
        control_group = QGroupBox("Path Planning Control")
        control_layout = QVBoxLayout(control_group)
        
        self.plan_path_button = QPushButton("Plan Path")
        control_layout.addWidget(self.plan_path_button)
        
        self.clear_path_button = QPushButton("Clear Path")
        control_layout.addWidget(self.clear_path_button)
        
        layout.addWidget(control_group)
        
        layout.addStretch()
        return widget
    
    def create_obstacles_tab(self):
        """Create the obstacles management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add Obstacle
        add_group = QGroupBox("Add Obstacle")
        add_layout = QFormLayout(add_group)
        
        self.obstacle_x = QDoubleSpinBox()
        self.obstacle_x.setRange(-1000, 1000)
        self.obstacle_x.setValue(0)
        self.obstacle_x.setSuffix(" m")
        add_layout.addRow("X:", self.obstacle_x)
        
        self.obstacle_y = QDoubleSpinBox()
        self.obstacle_y.setRange(-1000, 1000)
        self.obstacle_y.setValue(0)
        self.obstacle_y.setSuffix(" m")
        add_layout.addRow("Y:", self.obstacle_y)
        
        self.obstacle_z = QDoubleSpinBox()
        self.obstacle_z.setRange(-1000, 1000)
        self.obstacle_z.setValue(0)
        self.obstacle_z.setSuffix(" m")
        add_layout.addRow("Z:", self.obstacle_z)
        
        self.obstacle_radius = QDoubleSpinBox()
        self.obstacle_radius.setRange(0.1, 50.0)
        self.obstacle_radius.setValue(1.0)
        self.obstacle_radius.setSuffix(" m")
        add_layout.addRow("Radius:", self.obstacle_radius)
        
        self.obstacle_type = QComboBox()
        self.obstacle_type.addItems(['circle', 'rectangle'])
        add_layout.addRow("Type:", self.obstacle_type)
        
        # Obstacle buttons
        obstacle_buttons = QHBoxLayout()
        
        self.add_obstacle_button = QPushButton("Add Obstacle")
        obstacle_buttons.addWidget(self.add_obstacle_button)
        
        self.clear_obstacles_button = QPushButton("Clear All")
        obstacle_buttons.addWidget(self.clear_obstacles_button)
        
        add_layout.addRow("", obstacle_buttons)
        
        layout.addWidget(add_group)
        
        # Quick Obstacles
        quick_group = QGroupBox("Quick Obstacles")
        quick_layout = QVBoxLayout(quick_group)
        
        quick_obs_buttons = QHBoxLayout()
        
        self.obs_forward = QPushButton("Front (20m)")
        quick_obs_buttons.addWidget(self.obs_forward)
        
        self.obs_left = QPushButton("Left (15m)")
        quick_obs_buttons.addWidget(self.obs_left)
        
        quick_layout.addLayout(quick_obs_buttons)
        
        quick_obs_buttons2 = QHBoxLayout()
        
        self.obs_right = QPushButton("Right (15m)")
        quick_obs_buttons2.addWidget(self.obs_right)
        
        self.obs_random = QPushButton("Random")
        quick_obs_buttons2.addWidget(self.obs_random)
        
        quick_layout.addLayout(quick_obs_buttons2)
        
        layout.addWidget(quick_group)
        
        layout.addStretch()
        return widget
    
    def create_stats_tab(self):
        """Create the statistics display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Path Planning Stats
        stats_group = QGroupBox("Path Planning Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.path_length_label = QLabel("0")
        stats_layout.addRow("Path Length:", self.path_length_label)
        
        self.current_waypoint_label = QLabel("0")
        stats_layout.addRow("Current Waypoint:", self.current_waypoint_label)
        
        self.ai_enabled_label = QLabel("Disabled")
        stats_layout.addRow("AI Navigation:", self.ai_enabled_label)
        
        self.target_pos_label = QLabel("None")
        stats_layout.addRow("Target Position:", self.target_pos_label)
        
        layout.addWidget(stats_group)
        
        # Performance Stats
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.planning_time_label = QLabel("0.0 ms")
        perf_layout.addRow("Planning Time:", self.planning_time_label)
        
        self.path_cost_label = QLabel("0.0 m")
        perf_layout.addRow("Path Cost:", self.path_cost_label)
        
        self.obstacle_count_label = QLabel("0")
        perf_layout.addRow("Obstacles:", self.obstacle_count_label)
        
        layout.addWidget(perf_group)
        
        # Status Display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        return widget
    
    def setup_connections(self):
        """Setup signal connections."""
        # Navigation controls
        self.ai_enabled.toggled.connect(self.on_ai_navigation_toggled)
        self.emergency_stop.clicked.connect(self.on_emergency_stop)
        
        # Target controls
        self.set_target_button.clicked.connect(self.on_set_target)
        self.clear_target_button.clicked.connect(self.on_clear_target)
        
        # Quick targets
        self.target_forward.clicked.connect(lambda: self.set_quick_target(50, 0, 0))
        self.target_left.clicked.connect(lambda: self.set_quick_target(0, 0, -30))
        self.target_right.clicked.connect(lambda: self.set_quick_target(0, 0, 30))
        self.target_back.clicked.connect(lambda: self.set_quick_target(-50, 0, 0))
        
        # Path planning
        self.plan_path_button.clicked.connect(self.on_plan_path)
        self.clear_path_button.clicked.connect(self.on_clear_path)
        
        # Obstacles
        self.add_obstacle_button.clicked.connect(self.on_add_obstacle)
        self.clear_obstacles_button.clicked.connect(self.on_clear_obstacles)
        
        # Quick obstacles
        self.obs_forward.clicked.connect(lambda: self.add_quick_obstacle(20, 0, 0))
        self.obs_left.clicked.connect(lambda: self.add_quick_obstacle(0, 0, -15))
        self.obs_right.clicked.connect(lambda: self.add_quick_obstacle(0, 0, 15))
        self.obs_random.clicked.connect(self.on_add_random_obstacle)
    
    def setup_update_timer(self):
        """Setup timer for updating statistics."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(100)  # Update every 100ms
    
    def on_ai_navigation_toggled(self, enabled: bool):
        """Handle AI navigation toggle."""
        self.ai_navigation_toggled.emit(enabled)
        self.update_status(f"AI Navigation {'enabled' if enabled else 'disabled'}")
    
    def on_emergency_stop(self):
        """Handle emergency stop."""
        self.simulation_manager.set_vehicle_control(0.0, 1.0, 0.0)
        self.ai_enabled.setChecked(False)
        self.update_status("Emergency stop activated")
    
    def on_set_target(self):
        """Set the target position."""
        target = [self.target_x.value(), self.target_y.value(), self.target_z.value()]
        self.target_set.emit(target)
        self.simulation_manager.set_target_position(target)
        self.update_status(f"Target set to ({target[0]:.1f}, {target[1]:.1f}, {target[2]:.1f})")
    
    def on_clear_target(self):
        """Clear the current target."""
        self.simulation_manager.ai_navigation_enabled = False
        self.simulation_manager.current_path = None
        self.ai_enabled.setChecked(False)
        self.update_status("Target cleared")
    
    def set_quick_target(self, x: float, y: float, z: float):
        """Set a quick target position."""
        self.target_x.setValue(x)
        self.target_y.setValue(y)
        self.target_z.setValue(z)
        self.on_set_target()
    
    def on_plan_path(self):
        """Manually trigger path planning."""
        if self.simulation_manager.target_position != [0, 0, 0]:
            self.simulation_manager._plan_path_to_target()
            self.update_status("Path planning triggered")
        else:
            self.update_status("No target set for path planning")
    
    def on_clear_path(self):
        """Clear the current path."""
        self.simulation_manager.current_path = None
        self.simulation_manager.current_waypoint_index = 0
        self.update_status("Path cleared")
    
    def on_add_obstacle(self):
        """Add an obstacle at the specified position."""
        position = [self.obstacle_x.value(), self.obstacle_y.value(), self.obstacle_z.value()]
        radius = self.obstacle_radius.value()
        obstacle_type = self.obstacle_type.currentText()
        
        self.obstacle_added.emit(position, radius, obstacle_type)
        self.simulation_manager.add_obstacle(position, radius, None, obstacle_type)
        self.update_status(f"Obstacle added at ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f})")
    
    def on_clear_obstacles(self):
        """Clear all obstacles."""
        self.simulation_manager.obstacle_avoidance.clear_obstacles()
        self.update_status("All obstacles cleared")
    
    def add_quick_obstacle(self, x: float, y: float, z: float):
        """Add a quick obstacle at the specified position."""
        self.obstacle_x.setValue(x)
        self.obstacle_y.setValue(y)
        self.obstacle_z.setValue(z)
        self.on_add_obstacle()
    
    def on_add_random_obstacle(self):
        """Add a random obstacle."""
        import random
        x = random.uniform(-50, 50)
        z = random.uniform(-50, 50)
        radius = random.uniform(0.5, 3.0)
        
        self.obstacle_x.setValue(x)
        self.obstacle_y.setValue(0)
        self.obstacle_z.setValue(z)
        self.obstacle_radius.setValue(radius)
        self.on_add_obstacle()
    
    def update_statistics(self):
        """Update the statistics display."""
        # Path planning stats
        stats = self.simulation_manager.get_path_planning_stats()
        
        if stats:
            self.path_length_label.setText(str(stats.get('path_length', 0)))
            self.current_waypoint_label.setText(str(stats.get('current_waypoint', 0)))
            
            ai_enabled = stats.get('ai_navigation_enabled', False)
            self.ai_enabled_label.setText("Enabled" if ai_enabled else "Disabled")
            
            target = stats.get('target_position', [0, 0, 0])
            self.target_pos_label.setText(f"({target[0]:.1f}, {target[1]:.1f}, {target[2]:.1f})")
        else:
            self.path_length_label.setText("0")
            self.current_waypoint_label.setText("0")
            self.ai_enabled_label.setText("Disabled")
            self.target_pos_label.setText("None")
        
        # Obstacle count
        obstacle_count = len(self.simulation_manager.obstacle_avoidance.obstacles)
        self.obstacle_count_label.setText(str(obstacle_count))
    
    def update_status(self, message: str):
        """Update the status display."""
        self.status_text.append(f"[{self.simulation_manager.get_simulation_time():.1f}s] {message}")
        
        # Keep only last 10 lines
        lines = self.status_text.toPlainText().split('\n')
        if len(lines) > 10:
            self.status_text.setPlainText('\n'.join(lines[-10:])) 