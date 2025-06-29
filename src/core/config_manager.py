"""
Configuration manager for the autonomous vehicle simulator.

Handles loading, saving, and managing application configuration settings.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load default configuration
        self._load_default_config()
        
        # Load configuration from file if it exists
        if self.config_path.exists():
            self.load_config()
        else:
            self.save_config()
    
    def _load_default_config(self):
        """Load default configuration values."""
        self.config = {
            'application': {
                'name': 'Autonomous Vehicle Simulator',
                'version': '1.0.0',
                'theme': 'dark',
                'window_size': [1920, 1080],
                'window_position': [100, 100],
                'auto_save_interval': 300
            },
            'gui': {
                'dock_widgets': True,
                'show_toolbar': True,
                'show_statusbar': True,
                'show_menu_bar': True,
                'central_widget': '3d_viewport',
                'default_layout': 'standard',
                'panels': {
                    'sensor_data': {
                        'visible': True,
                        'position': 'right',
                        'size': [300, 400]
                    },
                    'control_panel': {
                        'visible': True,
                        'position': 'left',
                        'size': [250, 600]
                    },
                    'timeline': {
                        'visible': True,
                        'position': 'bottom',
                        'size': [800, 150]
                    },
                    'scene_tree': {
                        'visible': True,
                        'position': 'left',
                        'size': [250, 300]
                    },
                    'property_inspector': {
                        'visible': True,
                        'position': 'right',
                        'size': [300, 400]
                    }
                }
            },
            'visualization': {
                'renderer': 'opengl',
                'background_color': [0.1, 0.1, 0.15],
                'grid_enabled': True,
                'grid_size': 100,
                'grid_spacing': 5,
                'axes_enabled': True,
                'lighting_enabled': True,
                'shadows_enabled': True,
                'antialiasing': True,
                'vsync': True,
                'camera': {
                    'default_distance': 50,
                    'min_distance': 1,
                    'max_distance': 1000,
                    'fov': 45,
                    'near_plane': 0.1,
                    'far_plane': 1000
                }
            },
            'simulation': {
                'time_step': 0.016,
                'max_time': 3600,
                'physics_enabled': True,
                'collision_detection': True,
                'weather_enabled': True,
                'physics': {
                    'gravity': [0, -9.81, 0],
                    'air_resistance': 0.1,
                    'ground_friction': 0.8
                },
                'weather': {
                    'rain_intensity': 0.0,
                    'fog_density': 0.0,
                    'snow_intensity': 0.0,
                    'wind_speed': 0.0,
                    'wind_direction': 0.0
                }
            },
            'vehicle': {
                'default_type': 'sedan',
                'mass': 1500,
                'wheelbase': 2.7,
                'track_width': 1.6,
                'max_speed': 30,
                'max_acceleration': 3.0,
                'max_deceleration': 8.0,
                'steering_ratio': 16.0,
                'sensors': {
                    'lidar': {
                        'position': [0, 1.5, 0],
                        'orientation': [0, 0, 0]
                    },
                    'front_camera': {
                        'position': [0, 1.2, 2.5],
                        'orientation': [0, 0, 0]
                    },
                    'radar': {
                        'position': [0, 0.8, 2.0],
                        'orientation': [0, 0, 0]
                    },
                    'ultrasonic': {
                        'positions': {
                            'front_left': [0.8, 0.5, 2.5],
                            'front_right': [-0.8, 0.5, 2.5],
                            'rear_left': [0.8, 0.5, -2.5],
                            'rear_right': [-0.8, 0.5, -2.5]
                        }
                    }
                }
            },
            'sensors': {
                'lidar': {
                    'enabled': True,
                    'range': 100,
                    'resolution': 0.1,
                    'frequency': 10,
                    'noise_std': 0.02,
                    'max_points': 100000
                },
                'camera': {
                    'enabled': True,
                    'resolution': [1920, 1080],
                    'fps': 30,
                    'fov': 60,
                    'noise_enabled': True
                },
                'radar': {
                    'enabled': True,
                    'range': 200,
                    'frequency': 20,
                    'angular_resolution': 1.0,
                    'velocity_resolution': 0.1
                },
                'ultrasonic': {
                    'enabled': True,
                    'range': 5,
                    'frequency': 10,
                    'beam_angle': 15
                },
                'imu': {
                    'enabled': True,
                    'frequency': 100,
                    'gyro_noise': 0.01,
                    'accel_noise': 0.1
                },
                'gps': {
                    'enabled': True,
                    'frequency': 1,
                    'position_noise': 2.0,
                    'velocity_noise': 0.1
                }
            },
            'path_planning': {
                'algorithm': 'rrt',
                'grid_resolution': 0.5,
                'max_iterations': 1000,
                'goal_tolerance': 0.5,
                'rrt': {
                    'step_size': 1.0,
                    'goal_bias': 0.1
                },
                'a_star': {
                    'heuristic': 'euclidean'
                }
            },
            'recording': {
                'enabled': True,
                'auto_record': False,
                'format': 'pcd',
                'compression': True,
                'max_file_size': 100
            },
            'performance': {
                'max_fps': 60,
                'target_fps': 30,
                'vsync': True,
                'multithreading': True,
                'memory_limit': 2048
            },
            'logging': {
                'level': 'INFO',
                'file_enabled': True,
                'console_enabled': True,
                'max_file_size': 10,
                'backup_count': 5
            }
        }
    
    def load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    self.config.update(loaded_config)
                    self.logger.info(f"Configuration loaded from {self.config_path}")
                    return True
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
        return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'gui.panels.sensor_data.visible')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'gui.panels.sensor_data.visible')
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key.split('.')
        config = self.config
        
        try:
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            return True
        except Exception as e:
            self.logger.error(f"Failed to set configuration key '{key}': {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., 'gui', 'sensors')
            
        Returns:
            Configuration section as dictionary
        """
        return self.config.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]) -> bool:
        """
        Update an entire configuration section.
        
        Args:
            section: Section name
            values: New values for the section
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section].update(values)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update configuration section '{section}': {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self._load_default_config()
        self.save_config()
        self.logger.info("Configuration reset to defaults")
    
    def export_config(self, path: str) -> bool:
        """
        Export current configuration to a file.
        
        Args:
            path: Export file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration exported to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, path: str) -> bool:
        """
        Import configuration from a file.
        
        Args:
            path: Import file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                imported_config = yaml.safe_load(f)
                if imported_config:
                    self.config.update(imported_config)
                    self.save_config()
                    self.logger.info(f"Configuration imported from {path}")
                    return True
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
        return False 