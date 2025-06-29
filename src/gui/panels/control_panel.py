"""
Control panel for simulation parameters and vehicle controls.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSlider, 
    QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QCheckBox,
    QTabWidget, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ControlPanel(QWidget):
    """Control panel for simulation parameters and vehicle controls."""
    
    # Signals
    simulation_control_changed = pyqtSignal(str, object)
    vehicle_control_changed = pyqtSignal(str, object)
    sensor_control_changed = pyqtSignal(str, object)
    
    def __init__(self, config_manager, simulation_manager):
        """
        Initialize the control panel.
        
        Args:
            config_manager: Configuration manager
            simulation_manager: Simulation manager
        """
        super().__init__()
        
        self.config = config_manager
        self.simulation_manager = simulation_manager
        
        self.setup_ui()
        self.load_config()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Simulation tab
        self.simulation_tab = self.create_simulation_tab()
        self.tab_widget.addTab(self.simulation_tab, "Simulation")
        
        # Vehicle tab
        self.vehicle_tab = self.create_vehicle_tab()
        self.tab_widget.addTab(self.vehicle_tab, "Vehicle")
        
        # Sensors tab
        self.sensors_tab = self.create_sensors_tab()
        self.tab_widget.addTab(self.sensors_tab, "Sensors")
        
        # Environment tab
        self.environment_tab = self.create_environment_tab()
        self.tab_widget.addTab(self.environment_tab, "Environment")
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
    
    def create_simulation_tab(self):
        """Create the simulation control tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Time controls
        time_group = QGroupBox("Time Control")
        time_layout = QFormLayout(time_group)
        
        self.time_scale_slider = QSlider(Qt.Horizontal)
        self.time_scale_slider.setRange(1, 1000)
        self.time_scale_slider.setValue(100)
        time_layout.addRow("Time Scale:", self.time_scale_slider)
        
        self.time_scale_label = QLabel("100%")
        time_layout.addRow("", self.time_scale_label)
        
        layout.addWidget(time_group)
        
        # Physics controls
        physics_group = QGroupBox("Physics")
        physics_layout = QFormLayout(physics_group)
        
        self.gravity_x = QDoubleSpinBox()
        self.gravity_x.setRange(-20, 20)
        self.gravity_x.setValue(0)
        self.gravity_x.setSuffix(" m/s²")
        physics_layout.addRow("Gravity X:", self.gravity_x)
        
        self.gravity_y = QDoubleSpinBox()
        self.gravity_y.setRange(-20, 20)
        self.gravity_y.setValue(-9.81)
        self.gravity_y.setSuffix(" m/s²")
        physics_layout.addRow("Gravity Y:", self.gravity_y)
        
        self.gravity_z = QDoubleSpinBox()
        self.gravity_z.setRange(-20, 20)
        self.gravity_z.setValue(0)
        self.gravity_z.setSuffix(" m/s²")
        physics_layout.addRow("Gravity Z:", self.gravity_z)
        
        self.air_resistance = QDoubleSpinBox()
        self.air_resistance.setRange(0, 1)
        self.air_resistance.setValue(0.1)
        self.air_resistance.setSingleStep(0.01)
        physics_layout.addRow("Air Resistance:", self.air_resistance)
        
        self.ground_friction = QDoubleSpinBox()
        self.ground_friction.setRange(0, 1)
        self.ground_friction.setValue(0.8)
        self.ground_friction.setSingleStep(0.01)
        physics_layout.addRow("Ground Friction:", self.ground_friction)
        
        layout.addWidget(physics_group)
        
        # Simulation controls
        sim_group = QGroupBox("Simulation")
        sim_layout = QVBoxLayout(sim_group)
        
        self.physics_enabled = QCheckBox("Enable Physics")
        self.physics_enabled.setChecked(True)
        sim_layout.addWidget(self.physics_enabled)
        
        self.collision_detection = QCheckBox("Collision Detection")
        self.collision_detection.setChecked(True)
        sim_layout.addWidget(self.collision_detection)
        
        self.weather_enabled = QCheckBox("Weather Effects")
        self.weather_enabled.setChecked(True)
        sim_layout.addWidget(self.weather_enabled)
        
        layout.addWidget(sim_group)
        
        layout.addStretch()
        return widget
    
    def create_vehicle_tab(self):
        """Create the vehicle control tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Vehicle type
        vehicle_group = QGroupBox("Vehicle")
        vehicle_layout = QFormLayout(vehicle_group)
        
        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(['sedan', 'suv', 'truck', 'motorcycle'])
        vehicle_layout.addRow("Type:", self.vehicle_type)
        
        self.vehicle_mass = QDoubleSpinBox()
        self.vehicle_mass.setRange(500, 5000)
        self.vehicle_mass.setValue(1500)
        self.vehicle_mass.setSuffix(" kg")
        vehicle_layout.addRow("Mass:", self.vehicle_mass)
        
        self.wheelbase = QDoubleSpinBox()
        self.wheelbase.setRange(1, 10)
        self.wheelbase.setValue(2.7)
        self.wheelbase.setSuffix(" m")
        vehicle_layout.addRow("Wheelbase:", self.wheelbase)
        
        self.track_width = QDoubleSpinBox()
        self.track_width.setRange(1, 3)
        self.track_width.setValue(1.6)
        self.track_width.setSuffix(" m")
        vehicle_layout.addRow("Track Width:", self.track_width)
        
        layout.addWidget(vehicle_group)
        
        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.max_speed = QDoubleSpinBox()
        self.max_speed.setRange(10, 100)
        self.max_speed.setValue(30)
        self.max_speed.setSuffix(" m/s")
        perf_layout.addRow("Max Speed:", self.max_speed)
        
        self.max_acceleration = QDoubleSpinBox()
        self.max_acceleration.setRange(1, 10)
        self.max_acceleration.setValue(3.0)
        self.max_acceleration.setSuffix(" m/s²")
        perf_layout.addRow("Max Acceleration:", self.max_acceleration)
        
        self.max_deceleration = QDoubleSpinBox()
        self.max_deceleration.setRange(1, 15)
        self.max_deceleration.setValue(8.0)
        self.max_deceleration.setSuffix(" m/s²")
        perf_layout.addRow("Max Deceleration:", self.max_deceleration)
        
        self.steering_ratio = QDoubleSpinBox()
        self.steering_ratio.setRange(10, 25)
        self.steering_ratio.setValue(16.0)
        perf_layout.addRow("Steering Ratio:", self.steering_ratio)
        
        layout.addWidget(perf_group)
        
        # Controls
        control_group = QGroupBox("Manual Control")
        control_layout = QVBoxLayout(control_group)
        
        # Throttle
        throttle_layout = QHBoxLayout()
        throttle_layout.addWidget(QLabel("Throttle:"))
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setRange(0, 100)
        self.throttle_slider.setValue(0)
        throttle_layout.addWidget(self.throttle_slider)
        self.throttle_label = QLabel("0%")
        throttle_layout.addWidget(self.throttle_label)
        control_layout.addLayout(throttle_layout)
        
        # Brake
        brake_layout = QHBoxLayout()
        brake_layout.addWidget(QLabel("Brake:"))
        self.brake_slider = QSlider(Qt.Horizontal)
        self.brake_slider.setRange(0, 100)
        self.brake_slider.setValue(0)
        brake_layout.addWidget(self.brake_slider)
        self.brake_label = QLabel("0%")
        brake_layout.addWidget(self.brake_label)
        control_layout.addLayout(brake_layout)
        
        # Steering
        steering_layout = QHBoxLayout()
        steering_layout.addWidget(QLabel("Steering:"))
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setRange(-100, 100)
        self.steering_slider.setValue(0)
        steering_layout.addWidget(self.steering_slider)
        self.steering_label = QLabel("0°")
        steering_layout.addWidget(self.steering_label)
        control_layout.addLayout(steering_layout)
        
        layout.addWidget(control_group)
        
        layout.addStretch()
        return widget
    
    def create_sensors_tab(self):
        """Create the sensors control tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # LiDAR
        lidar_group = QGroupBox("LiDAR")
        lidar_layout = QFormLayout(lidar_group)
        
        self.lidar_enabled = QCheckBox("Enable LiDAR")
        self.lidar_enabled.setChecked(True)
        lidar_layout.addRow("", self.lidar_enabled)
        
        self.lidar_range = QDoubleSpinBox()
        self.lidar_range.setRange(10, 200)
        self.lidar_range.setValue(100)
        self.lidar_range.setSuffix(" m")
        lidar_layout.addRow("Range:", self.lidar_range)
        
        self.lidar_resolution = QDoubleSpinBox()
        self.lidar_resolution.setRange(0.01, 1.0)
        self.lidar_resolution.setValue(0.1)
        self.lidar_resolution.setSuffix("°")
        lidar_layout.addRow("Resolution:", self.lidar_resolution)
        
        self.lidar_frequency = QSpinBox()
        self.lidar_frequency.setRange(1, 50)
        self.lidar_frequency.setValue(10)
        self.lidar_frequency.setSuffix(" Hz")
        lidar_layout.addRow("Frequency:", self.lidar_frequency)
        
        layout.addWidget(lidar_group)
        
        # Camera
        camera_group = QGroupBox("Camera")
        camera_layout = QFormLayout(camera_group)
        
        self.camera_enabled = QCheckBox("Enable Camera")
        self.camera_enabled.setChecked(True)
        camera_layout.addRow("", self.camera_enabled)
        
        self.camera_fps = QSpinBox()
        self.camera_fps.setRange(1, 60)
        self.camera_fps.setValue(30)
        self.camera_fps.setSuffix(" FPS")
        camera_layout.addRow("FPS:", self.camera_fps)
        
        self.camera_fov = QDoubleSpinBox()
        self.camera_fov.setRange(30, 120)
        self.camera_fov.setValue(60)
        self.camera_fov.setSuffix("°")
        camera_layout.addRow("Field of View:", self.camera_fov)
        
        layout.addWidget(camera_group)
        
        # Radar
        radar_group = QGroupBox("Radar")
        radar_layout = QFormLayout(radar_group)
        
        self.radar_enabled = QCheckBox("Enable Radar")
        self.radar_enabled.setChecked(True)
        radar_layout.addRow("", self.radar_enabled)
        
        self.radar_range = QDoubleSpinBox()
        self.radar_range.setRange(50, 500)
        self.radar_range.setValue(200)
        self.radar_range.setSuffix(" m")
        radar_layout.addRow("Range:", self.radar_range)
        
        self.radar_frequency = QSpinBox()
        self.radar_frequency.setRange(1, 100)
        self.radar_frequency.setValue(20)
        self.radar_frequency.setSuffix(" Hz")
        radar_layout.addRow("Frequency:", self.radar_frequency)
        
        layout.addWidget(radar_group)
        
        layout.addStretch()
        return widget
    
    def create_environment_tab(self):
        """Create the environment control tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Weather
        weather_group = QGroupBox("Weather")
        weather_layout = QFormLayout(weather_group)
        
        self.rain_intensity = QSlider(Qt.Horizontal)
        self.rain_intensity.setRange(0, 100)
        self.rain_intensity.setValue(0)
        weather_layout.addRow("Rain Intensity:", self.rain_intensity)
        
        self.rain_label = QLabel("0%")
        weather_layout.addRow("", self.rain_label)
        
        self.fog_density = QSlider(Qt.Horizontal)
        self.fog_density.setRange(0, 100)
        self.fog_density.setValue(0)
        weather_layout.addRow("Fog Density:", self.fog_density)
        
        self.fog_label = QLabel("0%")
        weather_layout.addRow("", self.fog_label)
        
        self.snow_intensity = QSlider(Qt.Horizontal)
        self.snow_intensity.setRange(0, 100)
        self.snow_intensity.setValue(0)
        weather_layout.addRow("Snow Intensity:", self.snow_intensity)
        
        self.snow_label = QLabel("0%")
        weather_layout.addRow("", self.snow_label)
        
        layout.addWidget(weather_group)
        
        # Wind
        wind_group = QGroupBox("Wind")
        wind_layout = QFormLayout(wind_group)
        
        self.wind_speed = QDoubleSpinBox()
        self.wind_speed.setRange(0, 50)
        self.wind_speed.setValue(0)
        self.wind_speed.setSuffix(" m/s")
        wind_layout.addRow("Speed:", self.wind_speed)
        
        self.wind_direction = QDoubleSpinBox()
        self.wind_direction.setRange(0, 360)
        self.wind_direction.setValue(0)
        self.wind_direction.setSuffix("°")
        wind_layout.addRow("Direction:", self.wind_direction)
        
        layout.addWidget(wind_group)
        
        layout.addStretch()
        return widget
    
    def load_config(self):
        """Load configuration values."""
        # Load simulation settings
        physics_config = self.config.get_section('simulation.physics')
        self.gravity_x.setValue(physics_config.get('gravity', [0, -9.81, 0])[0])
        self.gravity_y.setValue(physics_config.get('gravity', [0, -9.81, 0])[1])
        self.gravity_z.setValue(physics_config.get('gravity', [0, -9.81, 0])[2])
        self.air_resistance.setValue(physics_config.get('air_resistance', 0.1))
        self.ground_friction.setValue(physics_config.get('ground_friction', 0.8))
        
        # Load vehicle settings
        vehicle_config = self.config.get_section('vehicle')
        self.vehicle_mass.setValue(vehicle_config.get('mass', 1500))
        self.wheelbase.setValue(vehicle_config.get('wheelbase', 2.7))
        self.track_width.setValue(vehicle_config.get('track_width', 1.6))
        self.max_speed.setValue(vehicle_config.get('max_speed', 30))
        self.max_acceleration.setValue(vehicle_config.get('max_acceleration', 3.0))
        self.max_deceleration.setValue(vehicle_config.get('max_deceleration', 8.0))
        self.steering_ratio.setValue(vehicle_config.get('steering_ratio', 16.0))
        
        # Load sensor settings
        sensors_config = self.config.get_section('sensors')
        lidar_config = sensors_config.get('lidar', {})
        self.lidar_enabled.setChecked(lidar_config.get('enabled', True))
        self.lidar_range.setValue(lidar_config.get('range', 100))
        self.lidar_resolution.setValue(lidar_config.get('resolution', 0.1))
        self.lidar_frequency.setValue(lidar_config.get('frequency', 10))
        
        camera_config = sensors_config.get('camera', {})
        self.camera_enabled.setChecked(camera_config.get('enabled', True))
        self.camera_fps.setValue(camera_config.get('fps', 30))
        self.camera_fov.setValue(camera_config.get('fov', 60))
        
        radar_config = sensors_config.get('radar', {})
        self.radar_enabled.setChecked(radar_config.get('enabled', True))
        self.radar_range.setValue(radar_config.get('range', 200))
        self.radar_frequency.setValue(radar_config.get('frequency', 20))
        
        # Load environment settings
        weather_config = self.config.get_section('simulation.weather')
        self.rain_intensity.setValue(int(weather_config.get('rain_intensity', 0.0) * 100))
        self.fog_density.setValue(int(weather_config.get('fog_density', 0.0) * 100))
        self.snow_intensity.setValue(int(weather_config.get('snow_intensity', 0.0) * 100))
        self.wind_speed.setValue(weather_config.get('wind_speed', 0.0))
        self.wind_direction.setValue(weather_config.get('wind_direction', 0.0))
    
    def setup_connections(self):
        """Setup signal connections."""
        # Time scale
        self.time_scale_slider.valueChanged.connect(self.on_time_scale_changed)
        
        # Physics controls
        self.gravity_x.valueChanged.connect(self.on_physics_changed)
        self.gravity_y.valueChanged.connect(self.on_physics_changed)
        self.gravity_z.valueChanged.connect(self.on_physics_changed)
        self.air_resistance.valueChanged.connect(self.on_physics_changed)
        self.ground_friction.valueChanged.connect(self.on_physics_changed)
        
        # Vehicle controls
        self.vehicle_mass.valueChanged.connect(self.on_vehicle_changed)
        self.wheelbase.valueChanged.connect(self.on_vehicle_changed)
        self.track_width.valueChanged.connect(self.on_vehicle_changed)
        self.max_speed.valueChanged.connect(self.on_vehicle_changed)
        self.max_acceleration.valueChanged.connect(self.on_vehicle_changed)
        self.max_deceleration.valueChanged.connect(self.on_vehicle_changed)
        self.steering_ratio.valueChanged.connect(self.on_vehicle_changed)
        
        # Manual controls
        self.throttle_slider.valueChanged.connect(self.on_manual_control_changed)
        self.brake_slider.valueChanged.connect(self.on_manual_control_changed)
        self.steering_slider.valueChanged.connect(self.on_manual_control_changed)
        # Connect vehicle control to simulation manager
        self.vehicle_control_changed.connect(self._on_vehicle_control_changed)
        
        # Sensor controls
        self.lidar_enabled.toggled.connect(self.on_sensor_changed)
        self.lidar_range.valueChanged.connect(self.on_sensor_changed)
        self.lidar_resolution.valueChanged.connect(self.on_sensor_changed)
        self.lidar_frequency.valueChanged.connect(self.on_sensor_changed)
        
        self.camera_enabled.toggled.connect(self.on_sensor_changed)
        self.camera_fps.valueChanged.connect(self.on_sensor_changed)
        self.camera_fov.valueChanged.connect(self.on_sensor_changed)
        
        self.radar_enabled.toggled.connect(self.on_sensor_changed)
        self.radar_range.valueChanged.connect(self.on_sensor_changed)
        self.radar_frequency.valueChanged.connect(self.on_sensor_changed)
        
        # Environment controls
        self.rain_intensity.valueChanged.connect(self.on_environment_changed)
        self.fog_density.valueChanged.connect(self.on_environment_changed)
        self.snow_intensity.valueChanged.connect(self.on_environment_changed)
        self.wind_speed.valueChanged.connect(self.on_environment_changed)
        self.wind_direction.valueChanged.connect(self.on_environment_changed)
    
    def on_time_scale_changed(self, value):
        """Handle time scale changes."""
        scale = value / 100.0
        self.time_scale_label.setText(f"{value}%")
        self.simulation_manager.set_time_scale(scale)
        self.simulation_control_changed.emit('time_scale', scale)
    
    def on_physics_changed(self):
        """Handle physics parameter changes."""
        physics_data = {
            'gravity': [self.gravity_x.value(), self.gravity_y.value(), self.gravity_z.value()],
            'air_resistance': self.air_resistance.value(),
            'ground_friction': self.ground_friction.value()
        }
        self.simulation_control_changed.emit('physics', physics_data)
    
    def on_vehicle_changed(self):
        """Handle vehicle parameter changes."""
        vehicle_data = {
            'mass': self.vehicle_mass.value(),
            'wheelbase': self.wheelbase.value(),
            'track_width': self.track_width.value(),
            'max_speed': self.max_speed.value(),
            'max_acceleration': self.max_acceleration.value(),
            'max_deceleration': self.max_deceleration.value(),
            'steering_ratio': self.steering_ratio.value()
        }
        self.vehicle_control_changed.emit('vehicle', vehicle_data)
    
    def on_manual_control_changed(self):
        """Handle manual control changes."""
        # Update labels
        self.throttle_label.setText(f"{self.throttle_slider.value()}%")
        self.brake_label.setText(f"{self.brake_slider.value()}%")
        self.steering_label.setText(f"{self.steering_slider.value()}°")
        
        # Emit control data
        control_data = {
            'throttle': self.throttle_slider.value() / 100.0,
            'brake': self.brake_slider.value() / 100.0,
            'steering': self.steering_slider.value() / 100.0
        }
        self.vehicle_control_changed.emit('manual_control', control_data)
    
    def on_sensor_changed(self):
        """Handle sensor parameter changes."""
        sensor_data = {
            'lidar': {
                'enabled': self.lidar_enabled.isChecked(),
                'range': self.lidar_range.value(),
                'resolution': self.lidar_resolution.value(),
                'frequency': self.lidar_frequency.value()
            },
            'camera': {
                'enabled': self.camera_enabled.isChecked(),
                'fps': self.camera_fps.value(),
                'fov': self.camera_fov.value()
            },
            'radar': {
                'enabled': self.radar_enabled.isChecked(),
                'range': self.radar_range.value(),
                'frequency': self.radar_frequency.value()
            }
        }
        self.sensor_control_changed.emit('sensors', sensor_data)
    
    def on_environment_changed(self):
        """Handle environment parameter changes."""
        # Update labels
        self.rain_label.setText(f"{self.rain_intensity.value()}%")
        self.fog_label.setText(f"{self.fog_density.value()}%")
        self.snow_label.setText(f"{self.snow_intensity.value()}%")
        
        # Emit environment data
        environment_data = {
            'rain_intensity': self.rain_intensity.value() / 100.0,
            'fog_density': self.fog_density.value() / 100.0,
            'snow_intensity': self.snow_intensity.value() / 100.0,
            'wind_speed': self.wind_speed.value(),
            'wind_direction': self.wind_direction.value()
        }
        self.simulation_control_changed.emit('environment', environment_data)
    
    def _on_vehicle_control_changed(self, control_type, control_data):
        """Internal slot to forward manual control to simulation manager."""
        if control_type == 'manual_control':
            throttle = control_data.get('throttle', 0.0)
            brake = control_data.get('brake', 0.0)
            steering = control_data.get('steering', 0.0)
            self.simulation_manager.set_vehicle_control(throttle, brake, steering) 