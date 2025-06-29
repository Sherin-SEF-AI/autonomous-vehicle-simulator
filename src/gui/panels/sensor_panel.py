"""
Sensor panel for displaying real-time sensor data and camera feeds.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QGroupBox, QFormLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
import numpy as np


class SensorPanel(QWidget):
    """Panel for displaying sensor data and camera feeds."""
    
    def __init__(self, config_manager, data_manager):
        """
        Initialize the sensor panel.
        
        Args:
            config_manager: Configuration manager
            data_manager: Data manager
        """
        super().__init__()
        
        self.config = config_manager
        self.data_manager = data_manager
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Camera tab
        self.camera_tab = self.create_camera_tab()
        self.tab_widget.addTab(self.camera_tab, "Camera")
        
        # LiDAR tab
        self.lidar_tab = self.create_lidar_tab()
        self.tab_widget.addTab(self.lidar_tab, "LiDAR")
        
        # Radar tab
        self.radar_tab = self.create_radar_tab()
        self.tab_widget.addTab(self.radar_tab, "Radar")
        
        # IMU/GPS tab
        self.imu_gps_tab = self.create_imu_gps_tab()
        self.tab_widget.addTab(self.imu_gps_tab, "IMU/GPS")
    
    def create_camera_tab(self):
        """Create the camera display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Camera feed
        camera_group = QGroupBox("Camera Feed")
        camera_layout = QVBoxLayout(camera_group)
        
        self.camera_label = QLabel("No camera feed available")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(300, 200)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #333;
                color: #666;
            }
        """)
        camera_layout.addWidget(self.camera_label)
        
        layout.addWidget(camera_group)
        
        # Camera info
        info_group = QGroupBox("Camera Information")
        info_layout = QFormLayout(info_group)
        
        self.camera_fps_label = QLabel("0 FPS")
        info_layout.addRow("FPS:", self.camera_fps_label)
        
        self.camera_resolution_label = QLabel("1920x1080")
        info_layout.addRow("Resolution:", self.camera_resolution_label)
        
        self.camera_fov_label = QLabel("60°")
        info_layout.addRow("Field of View:", self.camera_fov_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def create_lidar_tab(self):
        """Create the LiDAR display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # LiDAR visualization
        lidar_group = QGroupBox("LiDAR Point Cloud")
        lidar_layout = QVBoxLayout(lidar_group)
        
        self.lidar_canvas = LidarCanvas()
        lidar_layout.addWidget(self.lidar_canvas)
        
        layout.addWidget(lidar_group)
        
        # LiDAR info
        info_group = QGroupBox("LiDAR Information")
        info_layout = QFormLayout(info_group)
        
        self.lidar_points_label = QLabel("0 points")
        info_layout.addRow("Points:", self.lidar_points_label)
        
        self.lidar_range_label = QLabel("0-100m")
        info_layout.addRow("Range:", self.lidar_range_label)
        
        self.lidar_fps_label = QLabel("0 Hz")
        info_layout.addRow("Update Rate:", self.lidar_fps_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def create_radar_tab(self):
        """Create the radar display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Radar visualization
        radar_group = QGroupBox("Radar Range-Doppler")
        radar_layout = QVBoxLayout(radar_group)
        
        self.radar_canvas = RadarCanvas()
        radar_layout.addWidget(self.radar_canvas)
        
        layout.addWidget(radar_group)
        
        # Radar info
        info_group = QGroupBox("Radar Information")
        info_layout = QFormLayout(info_group)
        
        self.radar_targets_label = QLabel("0 targets")
        info_layout.addRow("Targets:", self.radar_targets_label)
        
        self.radar_range_label = QLabel("0-200m")
        info_layout.addRow("Range:", self.radar_range_label)
        
        self.radar_fps_label = QLabel("0 Hz")
        info_layout.addRow("Update Rate:", self.radar_fps_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def create_imu_gps_tab(self):
        """Create the IMU/GPS display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # IMU data
        imu_group = QGroupBox("IMU Data")
        imu_layout = QFormLayout(imu_group)
        
        self.accel_x_label = QLabel("0.00 m/s²")
        imu_layout.addRow("Acceleration X:", self.accel_x_label)
        
        self.accel_y_label = QLabel("0.00 m/s²")
        imu_layout.addRow("Acceleration Y:", self.accel_y_label)
        
        self.accel_z_label = QLabel("0.00 m/s²")
        imu_layout.addRow("Acceleration Z:", self.accel_z_label)
        
        self.gyro_x_label = QLabel("0.00 rad/s")
        imu_layout.addRow("Angular Velocity X:", self.gyro_x_label)
        
        self.gyro_y_label = QLabel("0.00 rad/s")
        imu_layout.addRow("Angular Velocity Y:", self.gyro_y_label)
        
        self.gyro_z_label = QLabel("0.00 rad/s")
        imu_layout.addRow("Angular Velocity Z:", self.gyro_z_label)
        
        layout.addWidget(imu_group)
        
        # GPS data
        gps_group = QGroupBox("GPS Data")
        gps_layout = QFormLayout(gps_group)
        
        self.gps_lat_label = QLabel("0.000000°")
        gps_layout.addRow("Latitude:", self.gps_lat_label)
        
        self.gps_lon_label = QLabel("0.000000°")
        gps_layout.addRow("Longitude:", self.gps_lon_label)
        
        self.gps_alt_label = QLabel("0.00 m")
        gps_layout.addRow("Altitude:", self.gps_alt_label)
        
        self.gps_speed_label = QLabel("0.00 m/s")
        gps_layout.addRow("Speed:", self.gps_speed_label)
        
        self.gps_heading_label = QLabel("0.00°")
        gps_layout.addRow("Heading:", self.gps_heading_label)
        
        layout.addWidget(gps_group)
        
        layout.addStretch()
        return widget
    
    def setup_timer(self):
        """Setup update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_sensor_data)
        self.update_timer.start(100)  # 10 FPS
    
    def update_sensor_data(self):
        """Update sensor data displays."""
        # Update camera feed (placeholder)
        # In a real implementation, this would display actual camera frames
        
        # Update LiDAR data (placeholder)
        # Generate some dummy LiDAR data
        if hasattr(self, 'lidar_canvas'):
            # Generate random point cloud data
            num_points = np.random.randint(1000, 5000)
            angles = np.linspace(-np.pi/2, np.pi/2, num_points)
            ranges = np.random.uniform(5, 100, num_points)
            
            points = np.column_stack([
                ranges * np.cos(angles),
                ranges * np.sin(angles),
                np.zeros(num_points)
            ])
            
            self.lidar_canvas.update_points(points)
            self.lidar_points_label.setText(f"{num_points} points")
        
        # Update radar data (placeholder)
        if hasattr(self, 'radar_canvas'):
            # Generate dummy radar data
            num_targets = np.random.randint(0, 10)
            targets = []
            for _ in range(num_targets):
                targets.append({
                    'range': np.random.uniform(10, 200),
                    'velocity': np.random.uniform(-30, 30),
                    'angle': np.random.uniform(-np.pi/4, np.pi/4)
                })
            
            self.radar_canvas.update_targets(targets)
            self.radar_targets_label.setText(f"{num_targets} targets")
        
        # Update IMU data (placeholder)
        self.accel_x_label.setText(f"{np.random.normal(0, 0.1):.2f} m/s²")
        self.accel_y_label.setText(f"{np.random.normal(-9.81, 0.1):.2f} m/s²")
        self.accel_z_label.setText(f"{np.random.normal(0, 0.1):.2f} m/s²")
        
        self.gyro_x_label.setText(f"{np.random.normal(0, 0.01):.2f} rad/s")
        self.gyro_y_label.setText(f"{np.random.normal(0, 0.01):.2f} rad/s")
        self.gyro_z_label.setText(f"{np.random.normal(0, 0.01):.2f} rad/s")
        
        # Update GPS data (placeholder)
        self.gps_lat_label.setText(f"{np.random.normal(37.7749, 0.001):.6f}°")
        self.gps_lon_label.setText(f"{np.random.normal(-122.4194, 0.001):.6f}°")
        self.gps_alt_label.setText(f"{np.random.normal(10, 1):.2f} m")
        self.gps_speed_label.setText(f"{np.random.uniform(0, 30):.2f} m/s")
        self.gps_heading_label.setText(f"{np.random.uniform(0, 360):.2f}°")


class LidarCanvas(QFrame):
    """Canvas for displaying LiDAR point cloud data."""
    
    def __init__(self):
        """Initialize the LiDAR canvas."""
        super().__init__()
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")
        
        self.points = np.array([])
        self.max_range = 100.0
    
    def update_points(self, points):
        """Update the point cloud data."""
        self.points = points
        self.update()
    
    def paintEvent(self, event):
        """Paint the LiDAR visualization."""
        if len(self.points) == 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(26, 26, 26))
        
        # Calculate scale
        width = self.width()
        height = self.height()
        scale = min(width, height) / (2 * self.max_range)
        
        # Draw grid
        painter.setPen(QColor(50, 50, 50))
        for i in range(-10, 11):
            x = width/2 + i * scale * 10
            painter.drawLine(int(x), 0, int(x), height)
            y = height/2 + i * scale * 10
            painter.drawLine(0, int(y), width, int(y))
        
        # Draw points
        for point in self.points:
            x = width/2 + point[0] * scale
            y = height/2 - point[1] * scale  # Flip Y axis
            
            # Color based on distance
            distance = np.sqrt(point[0]**2 + point[1]**2)
            intensity = max(0, 1 - distance / self.max_range)
            color = QColor(int(255 * intensity), int(255 * intensity), 255)
            
            painter.setPen(color)
            painter.drawPoint(int(x), int(y))


class RadarCanvas(QFrame):
    """Canvas for displaying radar range-doppler data."""
    
    def __init__(self):
        """Initialize the radar canvas."""
        super().__init__()
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")
        
        self.targets = []
        self.max_range = 200.0
        self.max_velocity = 50.0
    
    def update_targets(self, targets):
        """Update the radar targets."""
        self.targets = targets
        self.update()
    
    def paintEvent(self, event):
        """Paint the radar visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(26, 26, 26))
        
        width = self.width()
        height = self.height()
        
        # Draw grid
        painter.setPen(QColor(50, 50, 50))
        for i in range(5):
            x = (i + 1) * width / 5
            painter.drawLine(int(x), 0, int(x), height)
            y = (i + 1) * height / 5
            painter.drawLine(0, int(y), width, int(y))
        
        # Draw targets
        for target in self.targets:
            x = (target['range'] / self.max_range) * width
            y = height/2 + (target['velocity'] / self.max_velocity) * height/2
            
            # Color based on velocity
            velocity_abs = abs(target['velocity'])
            intensity = min(1.0, velocity_abs / self.max_velocity)
            if target['velocity'] > 0:
                color = QColor(255, int(255 * (1 - intensity)), 0)  # Red to yellow
            else:
                color = QColor(0, int(255 * (1 - intensity)), 255)  # Blue to cyan
            
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawEllipse(int(x - 3), int(y - 3), 6, 6) 