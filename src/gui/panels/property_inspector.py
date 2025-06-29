"""
Property inspector panel for displaying and editing object properties.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QSpinBox, QCheckBox, QComboBox, QGroupBox,
    QScrollArea, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal


class PropertyInspectorPanel(QWidget):
    """Panel for inspecting and editing object properties."""
    
    # Signals
    property_changed = pyqtSignal(str, str, object)  # object_name, property, value
    
    def __init__(self, config_manager):
        """
        Initialize the property inspector panel.
        
        Args:
            config_manager: Configuration manager
        """
        super().__init__()
        
        self.config = config_manager
        self.current_object = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        self.header_label = QLabel("No object selected")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.header_label)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Properties widget
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        self.properties_layout.setContentsMargins(0, 0, 0, 0)
        self.properties_layout.setSpacing(10)
        
        scroll.setWidget(self.properties_widget)
        layout.addWidget(scroll)
        
        # Show default message
        self.show_no_selection()
    
    def show_no_selection(self):
        """Show message when no object is selected."""
        self.clear_properties()
        
        no_selection_label = QLabel("Select an object to view its properties")
        no_selection_label.setAlignment(Qt.AlignCenter)
        no_selection_label.setStyleSheet("color: #666; font-style: italic;")
        self.properties_layout.addWidget(no_selection_label)
    
    def clear_properties(self):
        """Clear all property widgets."""
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def inspect_object(self, object_name: str, object_data: dict):
        """
        Inspect an object and display its properties.
        
        Args:
            object_name: Name of the object
            object_data: Object data dictionary
        """
        self.current_object = object_name
        self.clear_properties()
        
        # Update header
        self.header_label.setText(f"Properties: {object_name}")
        
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        # Name
        name_edit = QLineEdit(object_name)
        name_edit.textChanged.connect(lambda text: self.on_property_changed("name", text))
        basic_layout.addRow("Name:", name_edit)
        
        # Type
        type_label = QLabel(object_data.get('type', 'Unknown'))
        basic_layout.addRow("Type:", type_label)
        
        # Visible
        visible_check = QCheckBox()
        visible_check.setChecked(object_data.get('visible', True))
        visible_check.toggled.connect(lambda checked: self.on_property_changed("visible", checked))
        basic_layout.addRow("Visible:", visible_check)
        
        self.properties_layout.addWidget(basic_group)
        
        # Transform properties
        transform_group = QGroupBox("Transform")
        transform_layout = QFormLayout(transform_group)
        
        # Position
        position = object_data.get('position', [0, 0, 0])
        
        pos_x = QDoubleSpinBox()
        pos_x.setRange(-1000, 1000)
        pos_x.setValue(position[0])
        pos_x.setSuffix(" m")
        pos_x.valueChanged.connect(lambda value: self.on_position_changed(0, value))
        transform_layout.addRow("Position X:", pos_x)
        
        pos_y = QDoubleSpinBox()
        pos_y.setRange(-1000, 1000)
        pos_y.setValue(position[1])
        pos_y.setSuffix(" m")
        pos_y.valueChanged.connect(lambda value: self.on_position_changed(1, value))
        transform_layout.addRow("Position Y:", pos_y)
        
        pos_z = QDoubleSpinBox()
        pos_z.setRange(-1000, 1000)
        pos_z.setValue(position[2])
        pos_z.setSuffix(" m")
        pos_z.valueChanged.connect(lambda value: self.on_position_changed(2, value))
        transform_layout.addRow("Position Z:", pos_z)
        
        # Orientation
        orientation = object_data.get('orientation', [0, 0, 0])
        
        rot_x = QDoubleSpinBox()
        rot_x.setRange(-180, 180)
        rot_x.setValue(orientation[0])
        rot_x.setSuffix("°")
        rot_x.valueChanged.connect(lambda value: self.on_orientation_changed(0, value))
        transform_layout.addRow("Rotation X:", rot_x)
        
        rot_y = QDoubleSpinBox()
        rot_y.setRange(-180, 180)
        rot_y.setValue(orientation[1])
        rot_y.setSuffix("°")
        rot_y.valueChanged.connect(lambda value: self.on_orientation_changed(1, value))
        transform_layout.addRow("Rotation Y:", rot_y)
        
        rot_z = QDoubleSpinBox()
        rot_z.setRange(-180, 180)
        rot_z.setValue(orientation[2])
        rot_z.setSuffix("°")
        rot_z.valueChanged.connect(lambda value: self.on_orientation_changed(2, value))
        transform_layout.addRow("Rotation Z:", rot_z)
        
        self.properties_layout.addWidget(transform_group)
        
        # Type-specific properties
        obj_type = object_data.get('type', '')
        if obj_type == 'vehicle':
            self.add_vehicle_properties(object_data)
        elif obj_type == 'obstacle':
            self.add_obstacle_properties(object_data)
        elif obj_type == 'pedestrian':
            self.add_pedestrian_properties(object_data)
        
        # Add stretch to push everything to the top
        self.properties_layout.addStretch()
    
    def add_vehicle_properties(self, object_data):
        """Add vehicle-specific properties."""
        vehicle_group = QGroupBox("Vehicle Properties")
        vehicle_layout = QFormLayout(vehicle_group)
        
        # Mass
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(500, 5000)
        mass_spin.setValue(object_data.get('mass', 1500))
        mass_spin.setSuffix(" kg")
        mass_spin.valueChanged.connect(lambda value: self.on_property_changed("mass", value))
        vehicle_layout.addRow("Mass:", mass_spin)
        
        # Max speed
        max_speed_spin = QDoubleSpinBox()
        max_speed_spin.setRange(10, 100)
        max_speed_spin.setValue(object_data.get('max_speed', 30))
        max_speed_spin.setSuffix(" m/s")
        max_speed_spin.valueChanged.connect(lambda value: self.on_property_changed("max_speed", value))
        vehicle_layout.addRow("Max Speed:", max_speed_spin)
        
        # Vehicle type
        vehicle_type_combo = QComboBox()
        vehicle_type_combo.addItems(['sedan', 'suv', 'truck', 'motorcycle'])
        vehicle_type_combo.setCurrentText(object_data.get('vehicle_type', 'sedan'))
        vehicle_type_combo.currentTextChanged.connect(
            lambda text: self.on_property_changed("vehicle_type", text)
        )
        vehicle_layout.addRow("Vehicle Type:", vehicle_type_combo)
        
        self.properties_layout.addWidget(vehicle_group)
    
    def add_obstacle_properties(self, object_data):
        """Add obstacle-specific properties."""
        obstacle_group = QGroupBox("Obstacle Properties")
        obstacle_layout = QFormLayout(obstacle_group)
        
        # Obstacle type
        obstacle_type_combo = QComboBox()
        obstacle_type_combo.addItems(['building', 'tree', 'pole', 'barrier', 'other'])
        obstacle_type_combo.setCurrentText(object_data.get('obstacle_type', 'building'))
        obstacle_type_combo.currentTextChanged.connect(
            lambda text: self.on_property_changed("obstacle_type", text)
        )
        obstacle_layout.addRow("Obstacle Type:", obstacle_type_combo)
        
        # Size
        size = object_data.get('size', [1, 1, 1])
        
        size_x = QDoubleSpinBox()
        size_x.setRange(0.1, 100)
        size_x.setValue(size[0])
        size_x.setSuffix(" m")
        size_x.valueChanged.connect(lambda value: self.on_size_changed(0, value))
        obstacle_layout.addRow("Size X:", size_x)
        
        size_y = QDoubleSpinBox()
        size_y.setRange(0.1, 100)
        size_y.setValue(size[1])
        size_y.setSuffix(" m")
        size_y.valueChanged.connect(lambda value: self.on_size_changed(1, value))
        obstacle_layout.addRow("Size Y:", size_y)
        
        size_z = QDoubleSpinBox()
        size_z.setRange(0.1, 100)
        size_z.setValue(size[2])
        size_z.setSuffix(" m")
        size_z.valueChanged.connect(lambda value: self.on_size_changed(2, value))
        obstacle_layout.addRow("Size Z:", size_z)
        
        self.properties_layout.addWidget(obstacle_group)
    
    def add_pedestrian_properties(self, object_data):
        """Add pedestrian-specific properties."""
        pedestrian_group = QGroupBox("Pedestrian Properties")
        pedestrian_layout = QFormLayout(pedestrian_group)
        
        # Walking speed
        speed_spin = QDoubleSpinBox()
        speed_spin.setRange(0, 10)
        speed_spin.setValue(object_data.get('walking_speed', 1.4))
        speed_spin.setSuffix(" m/s")
        speed_spin.valueChanged.connect(lambda value: self.on_property_changed("walking_speed", value))
        pedestrian_layout.addRow("Walking Speed:", speed_spin)
        
        # Behavior
        behavior_combo = QComboBox()
        behavior_combo.addItems(['random', 'follow_path', 'avoid_obstacles'])
        behavior_combo.setCurrentText(object_data.get('behavior', 'random'))
        behavior_combo.currentTextChanged.connect(
            lambda text: self.on_property_changed("behavior", text)
        )
        pedestrian_layout.addRow("Behavior:", behavior_combo)
        
        self.properties_layout.addWidget(pedestrian_group)
    
    def on_property_changed(self, property_name: str, value):
        """Handle property changes."""
        if self.current_object:
            self.property_changed.emit(self.current_object, property_name, value)
    
    def on_position_changed(self, axis: int, value):
        """Handle position changes."""
        if self.current_object:
            # This would need to be implemented to update the actual position
            # For now, just emit the change
            self.property_changed.emit(self.current_object, f"position_{axis}", value)
    
    def on_orientation_changed(self, axis: int, value):
        """Handle orientation changes."""
        if self.current_object:
            self.property_changed.emit(self.current_object, f"orientation_{axis}", value)
    
    def on_size_changed(self, axis: int, value):
        """Handle size changes."""
        if self.current_object:
            self.property_changed.emit(self.current_object, f"size_{axis}", value)
    
    def clear_inspection(self):
        """Clear the current inspection."""
        self.current_object = None
        self.show_no_selection() 