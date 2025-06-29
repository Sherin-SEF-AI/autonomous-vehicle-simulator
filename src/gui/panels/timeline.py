"""
Timeline panel for scenario playback and analysis.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, 
    QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer


class TimelinePanel(QWidget):
    """Panel for timeline control and scenario playback."""
    
    # Signals
    playback_changed = pyqtSignal(str, object)  # action, value
    time_changed = pyqtSignal(float)  # time in seconds
    
    def __init__(self, config_manager, data_manager):
        """
        Initialize the timeline panel.
        
        Args:
            config_manager: Configuration manager
            data_manager: Data manager
        """
        super().__init__()
        
        self.config = config_manager
        self.data_manager = data_manager
        
        self.current_time = 0.0
        self.duration = 60.0  # Default 60 seconds
        self.is_playing = False
        self.playback_speed = 1.0
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QPushButton("▶")
        self.play_button.setMaximumWidth(40)
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton("⏹")
        self.stop_button.setMaximumWidth(40)
        self.stop_button.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_button)
        
        # Step backward
        self.step_back_button = QPushButton("⏮")
        self.step_back_button.setMaximumWidth(40)
        self.step_back_button.clicked.connect(self.step_backward)
        controls_layout.addWidget(self.step_back_button)
        
        # Step forward
        self.step_forward_button = QPushButton("⏭")
        self.step_forward_button.setMaximumWidth(40)
        self.step_forward_button.clicked.connect(self.step_forward)
        controls_layout.addWidget(self.step_forward_button)
        
        controls_layout.addStretch()
        
        # Time display
        self.time_label = QLabel("00:00.0")
        self.time_label.setStyleSheet("font-family: monospace; font-size: 14px;")
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
        # Timeline slider
        timeline_layout = QHBoxLayout()
        timeline_layout.addWidget(QLabel("Time:"))
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, int(self.duration * 10))  # 0.1 second precision
        self.timeline_slider.valueChanged.connect(self.on_slider_changed)
        timeline_layout.addWidget(self.timeline_slider)
        
        layout.addLayout(timeline_layout)
        
        # Settings
        settings_layout = QHBoxLayout()
        
        # Duration
        duration_group = QGroupBox("Duration")
        duration_layout = QFormLayout(duration_group)
        
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 3600)
        self.duration_spin.setValue(self.duration)
        self.duration_spin.setSuffix(" s")
        self.duration_spin.valueChanged.connect(self.on_duration_changed)
        duration_layout.addRow("Duration:", self.duration_spin)
        
        settings_layout.addWidget(duration_group)
        
        # Playback speed
        speed_group = QGroupBox("Playback")
        speed_layout = QFormLayout(speed_group)
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 10.0)
        self.speed_spin.setValue(self.playback_speed)
        self.speed_spin.setSuffix("x")
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.valueChanged.connect(self.on_speed_changed)
        speed_layout.addRow("Speed:", self.speed_spin)
        
        settings_layout.addWidget(speed_group)
        
        # Recording controls
        recording_group = QGroupBox("Recording")
        recording_layout = QHBoxLayout(recording_group)
        
        self.record_button = QPushButton("🔴 Record")
        self.record_button.setCheckable(True)
        self.record_button.clicked.connect(self.toggle_recording)
        recording_layout.addWidget(self.record_button)
        
        self.load_button = QPushButton("📁 Load")
        self.load_button.clicked.connect(self.load_recording)
        recording_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton("💾 Save")
        self.save_button.clicked.connect(self.save_recording)
        recording_layout.addWidget(self.save_button)
        
        settings_layout.addWidget(recording_group)
        
        layout.addLayout(settings_layout)
    
    def setup_timer(self):
        """Setup the playback timer."""
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playback)
        self.playback_timer.setInterval(100)  # 10 FPS
    
    def toggle_playback(self):
        """Toggle play/pause."""
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start playback."""
        self.is_playing = True
        self.play_button.setText("⏸")
        self.playback_timer.start()
        self.playback_changed.emit("play", True)
    
    def pause_playback(self):
        """Pause playback."""
        self.is_playing = False
        self.play_button.setText("▶")
        self.playback_timer.stop()
        self.playback_changed.emit("pause", True)
    
    def stop_playback(self):
        """Stop playback and reset to beginning."""
        self.is_playing = False
        self.play_button.setText("▶")
        self.playback_timer.stop()
        self.set_time(0.0)
        self.playback_changed.emit("stop", True)
    
    def step_backward(self):
        """Step backward by 1 second."""
        new_time = max(0.0, self.current_time - 1.0)
        self.set_time(new_time)
        self.playback_changed.emit("step_backward", new_time)
    
    def step_forward(self):
        """Step forward by 1 second."""
        new_time = min(self.duration, self.current_time + 1.0)
        self.set_time(new_time)
        self.playback_changed.emit("step_forward", new_time)
    
    def set_time(self, time_seconds: float):
        """Set the current time."""
        self.current_time = max(0.0, min(self.duration, time_seconds))
        
        # Update slider
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(int(self.current_time * 10))
        self.timeline_slider.blockSignals(False)
        
        # Update time label
        minutes = int(self.current_time // 60)
        seconds = self.current_time % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:05.1f}")
        
        # Emit signal
        self.time_changed.emit(self.current_time)
    
    def on_slider_changed(self, value):
        """Handle slider value changes."""
        time_seconds = value / 10.0
        self.current_time = time_seconds
        
        # Update time label
        minutes = int(self.current_time // 60)
        seconds = self.current_time % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:05.1f}")
        
        # Emit signal
        self.time_changed.emit(self.current_time)
    
    def on_duration_changed(self, duration: float):
        """Handle duration changes."""
        self.duration = duration
        self.timeline_slider.setRange(0, int(self.duration * 10))
        self.playback_changed.emit("duration", duration)
    
    def on_speed_changed(self, speed: float):
        """Handle playback speed changes."""
        self.playback_speed = speed
        self.playback_changed.emit("speed", speed)
    
    def update_playback(self):
        """Update playback (called by timer)."""
        if self.is_playing:
            new_time = self.current_time + (0.1 * self.playback_speed)
            if new_time >= self.duration:
                self.stop_playback()
            else:
                self.set_time(new_time)
    
    def toggle_recording(self):
        """Toggle recording."""
        if self.record_button.isChecked():
            # Start recording
            self.data_manager.start_recording()
            self.record_button.setText("⏹ Stop")
            self.record_button.setStyleSheet("background-color: #ff4444; color: white;")
        else:
            # Stop recording
            self.data_manager.stop_recording()
            self.record_button.setText("🔴 Record")
            self.record_button.setStyleSheet("")
    
    def load_recording(self):
        """Load a recording."""
        # This would typically open a file dialog
        # For now, just emit a signal
        self.playback_changed.emit("load_recording", None)
    
    def save_recording(self):
        """Save the current recording."""
        if self.data_manager.is_recording:
            self.data_manager.stop_recording()
            self.record_button.setChecked(False)
            self.record_button.setText("🔴 Record")
            self.record_button.setStyleSheet("")
        
        # Save the recording
        self.data_manager.save_recording()
    
    def get_current_time(self) -> float:
        """Get the current time."""
        return self.current_time
    
    def get_duration(self) -> float:
        """Get the total duration."""
        return self.duration
    
    def get_playback_speed(self) -> float:
        """Get the playback speed."""
        return self.playback_speed
    
    def is_playback_active(self) -> bool:
        """Check if playback is active."""
        return self.is_playing 