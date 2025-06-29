"""
Data manager for the autonomous vehicle simulator.

Handles sensor data recording, export, and replay functionality.
"""

import os
import json
import pickle
import logging
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import time

try:
    import numpy as np
except ImportError:
    np = None


@dataclass
class SensorData:
    """Container for sensor data."""
    timestamp: float
    sensor_type: str
    sensor_id: str
    data: Any
    metadata: Dict[str, Any]


@dataclass
class RecordingSession:
    """Recording session information."""
    session_id: str
    start_time: float
    end_time: float
    duration: float
    sensor_count: int
    data_points: int
    file_size: int
    metadata: Dict[str, Any]


class DataManager:
    """Manages sensor data recording, export, and replay."""
    
    def __init__(self, config_manager, data_dir: str = "data"):
        """
        Initialize the data manager.
        
        Args:
            config_manager: Configuration manager instance
            data_dir: Directory for storing data files
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Recording state
        self.is_recording = False
        self.current_session: Optional[RecordingSession] = None
        self.recorded_data: List[SensorData] = []
        
        # Replay state
        self.is_replaying = False
        self.replay_data: List[SensorData] = []
        self.replay_index = 0
        self.replay_speed = 1.0
        
        # Configuration
        self.auto_record = self.config.get('recording.auto_record', False)
        self.record_format = self.config.get('recording.format', 'pcd')
        self.compression = self.config.get('recording.compression', True)
        self.max_file_size = self.config.get('recording.max_file_size', 100) * 1024 * 1024  # MB to bytes
        
        # Callbacks
        self.on_data_recorded_callbacks: List[Callable] = []
        self.on_recording_started_callbacks: List[Callable] = []
        self.on_recording_stopped_callbacks: List[Callable] = []
        self.on_replay_started_callbacks: List[Callable] = []
        self.on_replay_stopped_callbacks: List[Callable] = []
        
        # Threading
        self.recording_lock = threading.Lock()
        self.replay_lock = threading.Lock()
    
    def start_recording(self, session_name: Optional[str] = None) -> bool:
        """
        Start recording sensor data.
        
        Args:
            session_name: Optional session name
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_recording:
            self.logger.warning("Recording already in progress")
            return False
        
        try:
            with self.recording_lock:
                # Create session
                session_id = session_name or f"session_{int(time.time())}"
                start_time = time.time()
                
                self.current_session = RecordingSession(
                    session_id=session_id,
                    start_time=start_time,
                    end_time=0.0,
                    duration=0.0,
                    sensor_count=0,
                    data_points=0,
                    file_size=0,
                    metadata={
                        'config': self.config.get_section('sensors'),
                        'vehicle': self.config.get_section('vehicle'),
                        'simulation': self.config.get_section('simulation')
                    }
                )
                
                self.is_recording = True
                self.recorded_data.clear()
                
                self.logger.info(f"Started recording session: {session_id}")
                
                # Call callbacks
                for callback in self.on_recording_started_callbacks:
                    try:
                        callback(self.current_session)
                    except Exception as e:
                        self.logger.error(f"Error in recording started callback: {e}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop recording sensor data.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_recording:
            self.logger.warning("No recording in progress")
            return False
        
        try:
            with self.recording_lock:
                if self.current_session:
                    self.current_session.end_time = time.time()
                    self.current_session.duration = (
                        self.current_session.end_time - self.current_session.start_time
                    )
                    self.current_session.data_points = len(self.recorded_data)
                    self.current_session.sensor_count = len(
                        set(data.sensor_id for data in self.recorded_data)
                    )
                
                self.is_recording = False
                
                self.logger.info(f"Stopped recording session: {self.current_session.session_id if self.current_session else 'Unknown'}")
                
                # Call callbacks
                for callback in self.on_recording_stopped_callbacks:
                    try:
                        callback(self.current_session)
                    except Exception as e:
                        self.logger.error(f"Error in recording stopped callback: {e}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def record_sensor_data(self, sensor_type: str, sensor_id: str, data: Any, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record sensor data.
        
        Args:
            sensor_type: Type of sensor (lidar, camera, radar, etc.)
            sensor_id: Unique sensor identifier
            data: Sensor data
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_recording:
            return False
        
        try:
            with self.recording_lock:
                sensor_data = SensorData(
                    timestamp=time.time(),
                    sensor_type=sensor_type,
                    sensor_id=sensor_id,
                    data=data,
                    metadata=metadata or {}
                )
                
                self.recorded_data.append(sensor_data)
                
                # Check file size limit
                if self._estimate_file_size() > self.max_file_size:
                    self.logger.warning("Maximum file size reached, stopping recording")
                    self.stop_recording()
                    return False
                
                # Call callbacks
                for callback in self.on_data_recorded_callbacks:
                    try:
                        callback(sensor_data)
                    except Exception as e:
                        self.logger.error(f"Error in data recorded callback: {e}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record sensor data: {e}")
            return False
    
    def save_recording(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Save recorded data to file.
        
        Args:
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            File path if successful, None otherwise
        """
        if not self.current_session or not self.recorded_data:
            self.logger.warning("No recording data to save")
            return None
        
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.fromtimestamp(self.current_session.start_time).strftime("%Y%m%d_%H%M%S")
                filename = f"{self.current_session.session_id}_{timestamp}.{self.record_format}"
            
            file_path = self.data_dir / filename
            
            # Save based on format
            if self.record_format == 'pcd':
                self._save_as_pcd(file_path)
            elif self.record_format == 'json':
                self._save_as_json(file_path)
            elif self.record_format == 'pickle':
                self._save_as_pickle(file_path)
            else:
                self.logger.error(f"Unsupported format: {self.record_format}")
                return None
            
            # Update session info
            self.current_session.file_size = file_path.stat().st_size
            
            self.logger.info(f"Recording saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save recording: {e}")
            return None
    
    def load_recording(self, file_path: Union[str, Path]) -> bool:
        """
        Load recording from file.
        
        Args:
            file_path: Path to recording file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"Recording file not found: {file_path}")
                return False
            
            # Load based on format
            if file_path.suffix == '.pcd':
                self.replay_data = self._load_from_pcd(file_path)
            elif file_path.suffix == '.json':
                self.replay_data = self._load_from_json(file_path)
            elif file_path.suffix == '.pickle':
                self.replay_data = self._load_from_pickle(file_path)
            else:
                self.logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            self.replay_index = 0
            self.logger.info(f"Loaded recording: {len(self.replay_data)} data points")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load recording: {e}")
            return False
    
    def start_replay(self) -> bool:
        """
        Start replaying loaded data.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.replay_data:
            self.logger.warning("No replay data loaded")
            return False
        
        if self.is_replaying:
            self.logger.warning("Replay already in progress")
            return False
        
        try:
            with self.replay_lock:
                self.is_replaying = True
                self.replay_index = 0
                
                self.logger.info("Started replay")
                
                # Call callbacks
                for callback in self.on_replay_started_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        self.logger.error(f"Error in replay started callback: {e}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start replay: {e}")
            return False
    
    def stop_replay(self) -> bool:
        """
        Stop replaying data.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_replaying:
            return False
        
        try:
            with self.replay_lock:
                self.is_replaying = False
                
                self.logger.info("Stopped replay")
                
                # Call callbacks
                for callback in self.on_replay_stopped_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        self.logger.error(f"Error in replay stopped callback: {e}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop replay: {e}")
            return False
    
    def get_next_replay_data(self) -> Optional[SensorData]:
        """
        Get next data point for replay.
        
        Returns:
            Next sensor data or None if replay is complete
        """
        if not self.is_replaying or self.replay_index >= len(self.replay_data):
            return None
        
        try:
            with self.replay_lock:
                data = self.replay_data[self.replay_index]
                self.replay_index += 1
                return data
        except Exception as e:
            self.logger.error(f"Error getting replay data: {e}")
            return None
    
    def set_replay_speed(self, speed: float):
        """
        Set replay speed.
        
        Args:
            speed: Replay speed multiplier
        """
        self.replay_speed = max(0.1, min(10.0, speed))
    
    def get_replay_progress(self) -> float:
        """
        Get replay progress (0.0 to 1.0).
        
        Returns:
            Replay progress
        """
        if not self.replay_data:
            return 0.0
        return self.replay_index / len(self.replay_data)
    
    def add_callback(self, event: str, callback: Callable):
        """
        Add an event callback.
        
        Args:
            event: Event type ('data_recorded', 'recording_started', 'recording_stopped', 
                              'replay_started', 'replay_stopped')
            callback: Event callback function
        """
        if event == 'data_recorded':
            self.on_data_recorded_callbacks.append(callback)
        elif event == 'recording_started':
            self.on_recording_started_callbacks.append(callback)
        elif event == 'recording_stopped':
            self.on_recording_stopped_callbacks.append(callback)
        elif event == 'replay_started':
            self.on_replay_started_callbacks.append(callback)
        elif event == 'replay_stopped':
            self.on_replay_stopped_callbacks.append(callback)
    
    def get_recording_stats(self) -> Optional[RecordingSession]:
        """Get current recording session statistics."""
        return self.current_session
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        """
        List available recordings.
        
        Returns:
            List of recording information
        """
        recordings = []
        
        for file_path in self.data_dir.glob("*.*"):
            if file_path.suffix in ['.pcd', '.json', '.pickle']:
                try:
                    stat = file_path.stat()
                    recordings.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'format': file_path.suffix[1:]
                    })
                except Exception as e:
                    self.logger.error(f"Error reading file info for {file_path}: {e}")
        
        return sorted(recordings, key=lambda x: x['modified'], reverse=True)
    
    def _estimate_file_size(self) -> int:
        """Estimate current recording file size."""
        # Simple estimation - can be improved
        return len(self.recorded_data) * 1024  # Assume 1KB per data point
    
    def _save_as_pcd(self, file_path: Path):
        """Save data in PCD format."""
        # Implementation for PCD format
        with open(file_path, 'wb') as f:
            pickle.dump({
                'session': asdict(self.current_session) if self.current_session else {},
                'data': self.recorded_data
            }, f)
    
    def _save_as_json(self, file_path: Path):
        """Save data in JSON format."""
        # Convert data to JSON-serializable format
        json_data = {
            'session': asdict(self.current_session) if self.current_session else {},
            'data': [
                {
                    'timestamp': data.timestamp,
                    'sensor_type': data.sensor_type,
                    'sensor_id': data.sensor_id,
                    'data': data.data.tolist() if hasattr(data.data, 'tolist') else data.data,
                    'metadata': data.metadata
                }
                for data in self.recorded_data
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2)
    
    def _save_as_pickle(self, file_path: Path):
        """Save data in pickle format."""
        with open(file_path, 'wb') as f:
            pickle.dump({
                'session': self.current_session,
                'data': self.recorded_data
            }, f)
    
    def _load_from_pcd(self, file_path: Path) -> List[SensorData]:
        """Load data from PCD format."""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            return data.get('data', [])
    
    def _load_from_json(self, file_path: Path) -> List[SensorData]:
        """Load data from JSON format."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        sensor_data = []
        for item in data.get('data', []):
            arr = item['data']
            if isinstance(arr, list) and np is not None:
                arr = np.array(arr)
            sensor_data.append(SensorData(
                timestamp=item['timestamp'],
                sensor_type=item['sensor_type'],
                sensor_id=item['sensor_id'],
                data=arr,
                metadata=item['metadata']
            ))
        
        return sensor_data
    
    def _load_from_pickle(self, file_path: Path) -> List[SensorData]:
        """Load data from pickle format."""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            return data.get('data', []) 