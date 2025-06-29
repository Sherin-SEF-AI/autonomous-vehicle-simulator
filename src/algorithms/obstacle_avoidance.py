"""
Obstacle avoidance algorithms for autonomous vehicle navigation.
"""

import numpy as np
import math
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import logging


@dataclass
class Obstacle:
    """Obstacle representation."""
    position: Tuple[float, float]
    radius: float
    velocity: Tuple[float, float] = (0.0, 0.0)
    obstacle_type: str = "circle"


class ObstacleAvoidance:
    """Obstacle avoidance system for autonomous vehicles."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize obstacle avoidance system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Safety parameters
        self.safety_margin = config.get('safety_margin', 2.0)
        self.look_ahead_distance = config.get('look_ahead_distance', 10.0)
        self.max_avoidance_force = config.get('max_avoidance_force', 5.0)
        
        # Vehicle parameters
        self.vehicle_radius = config.get('vehicle_radius', 1.0)
        self.max_speed = config.get('max_speed', 10.0)
        
        # Obstacles
        self.obstacles: List[Obstacle] = []
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add an obstacle to the avoidance system."""
        self.obstacles.append(obstacle)
    
    def remove_obstacle(self, obstacle: Obstacle):
        """Remove an obstacle from the avoidance system."""
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
    
    def clear_obstacles(self):
        """Clear all obstacles."""
        self.obstacles.clear()
    
    def get_avoidance_force(self, vehicle_pos: Tuple[float, float], 
                          vehicle_vel: Tuple[float, float]) -> Tuple[float, float]:
        """
        Calculate avoidance force based on nearby obstacles.
        
        Args:
            vehicle_pos: Current vehicle position (x, y)
            vehicle_vel: Current vehicle velocity (vx, vy)
            
        Returns:
            Avoidance force vector (fx, fy)
        """
        avoidance_force = np.array([0.0, 0.0])
        
        for obstacle in self.obstacles:
            # Calculate distance to obstacle
            distance = self._distance(vehicle_pos, obstacle.position)
            
            # Check if obstacle is within look-ahead distance
            if distance < self.look_ahead_distance:
                # Calculate repulsive force
                repulsive_force = self._calculate_repulsive_force(
                    vehicle_pos, obstacle, distance
                )
                avoidance_force += repulsive_force
        
        # Limit the maximum avoidance force
        force_magnitude = np.linalg.norm(avoidance_force)
        if force_magnitude > self.max_avoidance_force:
            avoidance_force = avoidance_force / force_magnitude * self.max_avoidance_force
        
        return tuple(avoidance_force)
    
    def _calculate_repulsive_force(self, vehicle_pos: Tuple[float, float], 
                                 obstacle: Obstacle, distance: float) -> np.ndarray:
        """Calculate repulsive force from a single obstacle."""
        # Direction from obstacle to vehicle
        direction = np.array([
            vehicle_pos[0] - obstacle.position[0],
            vehicle_pos[1] - obstacle.position[1]
        ])
        
        if np.linalg.norm(direction) == 0:
            return np.array([0.0, 0.0])
        
        direction = direction / np.linalg.norm(direction)
        
        # Calculate force magnitude (inverse square law)
        min_distance = obstacle.radius + self.vehicle_radius + self.safety_margin
        if distance < min_distance:
            # Strong repulsion when very close
            force_magnitude = self.max_avoidance_force
        else:
            # Inverse square law for repulsion
            force_magnitude = self.max_avoidance_force * (min_distance / distance) ** 2
        
        return direction * force_magnitude
    
    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def predict_collision(self, vehicle_pos: Tuple[float, float], 
                         vehicle_vel: Tuple[float, float], 
                         time_horizon: float = 5.0) -> List[Dict[str, Any]]:
        """
        Predict potential collisions with obstacles.
        
        Args:
            vehicle_pos: Current vehicle position
            vehicle_vel: Current vehicle velocity
            time_horizon: Time horizon for prediction (seconds)
            
        Returns:
            List of collision predictions
        """
        collisions = []
        
        for obstacle in self.obstacles:
            # Predict obstacle position
            obstacle_future_pos = (
                obstacle.position[0] + obstacle.velocity[0] * time_horizon,
                obstacle.position[1] + obstacle.velocity[1] * time_horizon
            )
            
            # Predict vehicle position
            vehicle_future_pos = (
                vehicle_pos[0] + vehicle_vel[0] * time_horizon,
                vehicle_pos[1] + vehicle_vel[1] * time_horizon
            )
            
            # Calculate future distance
            future_distance = self._distance(vehicle_future_pos, obstacle_future_pos)
            min_safe_distance = obstacle.radius + self.vehicle_radius + self.safety_margin
            
            if future_distance < min_safe_distance:
                # Calculate time to collision
                relative_vel = np.array(vehicle_vel) - np.array(obstacle.velocity)
                relative_pos = np.array(vehicle_pos) - np.array(obstacle.position)
                
                # Solve quadratic equation for collision time
                a = np.dot(relative_vel, relative_vel)
                b = 2 * np.dot(relative_vel, relative_pos)
                c = np.dot(relative_pos, relative_pos) - min_safe_distance ** 2
                
                if a > 0:
                    discriminant = b ** 2 - 4 * a * c
                    if discriminant >= 0:
                        ttc = (-b - math.sqrt(discriminant)) / (2 * a)
                        if 0 <= ttc <= time_horizon:
                            collisions.append({
                                'obstacle': obstacle,
                                'time_to_collision': ttc,
                                'future_distance': future_distance,
                                'min_safe_distance': min_safe_distance
                            })
        
        return sorted(collisions, key=lambda x: x['time_to_collision'])
    
    def get_safe_velocity(self, desired_vel: Tuple[float, float], 
                         vehicle_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Calculate safe velocity considering obstacles.
        
        Args:
            desired_vel: Desired velocity vector
            vehicle_pos: Current vehicle position
            
        Returns:
            Safe velocity vector
        """
        # Get avoidance force
        avoidance_force = self.get_avoidance_force(vehicle_pos, desired_vel)
        
        # Apply avoidance force to desired velocity
        safe_vel = np.array(desired_vel) + np.array(avoidance_force)
        
        # Limit to maximum speed
        vel_magnitude = np.linalg.norm(safe_vel)
        if vel_magnitude > self.max_speed:
            safe_vel = safe_vel / vel_magnitude * self.max_speed
        
        return tuple(safe_vel)
    
    def is_path_safe(self, path: List[Tuple[float, float]], 
                    vehicle_vel: Tuple[float, float]) -> bool:
        """
        Check if a path is safe from obstacles.
        
        Args:
            path: List of waypoints
            vehicle_vel: Vehicle velocity
            
        Returns:
            True if path is safe
        """
        for i, waypoint in enumerate(path):
            # Check if waypoint is safe
            for obstacle in self.obstacles:
                distance = self._distance(waypoint, obstacle.position)
                min_safe_distance = obstacle.radius + self.vehicle_radius + self.safety_margin
                
                if distance < min_safe_distance:
                    return False
            
            # Check for moving obstacles
            if i < len(path) - 1:
                # Predict obstacle positions along path segment
                segment_start = waypoint
                segment_end = path[i + 1]
                
                # Check multiple points along the segment
                for t in np.linspace(0, 1, 10):
                    point = (
                        segment_start[0] + t * (segment_end[0] - segment_start[0]),
                        segment_start[1] + t * (segment_end[1] - segment_start[1])
                    )
                    
                    for obstacle in self.obstacles:
                        # Predict obstacle position
                        obstacle_future_pos = (
                            obstacle.position[0] + obstacle.velocity[0] * t,
                            obstacle.position[1] + obstacle.velocity[1] * t
                        )
                        
                        distance = self._distance(point, obstacle_future_pos)
                        min_safe_distance = obstacle.radius + self.vehicle_radius + self.safety_margin
                        
                        if distance < min_safe_distance:
                            return False
        
        return True
    
    def get_obstacle_density(self, position: Tuple[float, float], 
                           radius: float = 5.0) -> float:
        """
        Calculate obstacle density around a position.
        
        Args:
            position: Center position
            radius: Search radius
            
        Returns:
            Obstacle density (obstacles per unit area)
        """
        nearby_obstacles = 0
        
        for obstacle in self.obstacles:
            distance = self._distance(position, obstacle.position)
            if distance < radius:
                nearby_obstacles += 1
        
        area = math.pi * radius ** 2
        return nearby_obstacles / area if area > 0 else 0.0 