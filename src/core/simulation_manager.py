"""
Simulation manager for the autonomous vehicle simulator.

Handles the main simulation loop, timing, and coordination between components.
"""

import time
import threading
import logging
from typing import Dict, List, Optional, Callable, Protocol, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from src.simulation.physics_engine import PhysicsEngine
from src.algorithms.path_planning import RRTPlanner, AStarPlanner, Path
from src.algorithms.obstacle_avoidance import ObstacleAvoidance, Obstacle
import math


class SimulationState(Enum):
    """Simulation states."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"


@dataclass
class SimulationStats:
    """Simulation performance statistics."""
    fps: float = 0.0
    frame_time: float = 0.0
    simulation_time: float = 0.0
    real_time: float = 0.0
    time_scale: float = 1.0
    total_frames: int = 0
    dropped_frames: int = 0


class SimulationComponent(Protocol):
    """Protocol for simulation components."""
    
    def update(self, dt: float) -> None:
        """Update component with time step."""
        ...
    
    def reset(self) -> None:
        """Reset component to initial state."""
        ...


class SimulationManager:
    """Manages the main simulation loop and coordination."""
    
    def __init__(self, config_manager):
        """
        Initialize the simulation manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Simulation state
        self.state = SimulationState.STOPPED
        self.stats = SimulationStats()
        
        # Timing
        self.time_step = self.config.get('simulation.time_step', 0.016)
        self.max_time = self.config.get('simulation.max_time', 3600)
        self.target_fps = self.config.get('performance.target_fps', 30)
        self.max_fps = self.config.get('performance.max_fps', 60)
        
        # Simulation time
        self.simulation_time = 0.0
        self.real_time = 0.0
        self.time_scale = 1.0
        
        # Threading
        self.simulation_thread = None
        self.running = False
        self.paused = False
        
        # Components
        self.components: Dict[str, SimulationComponent] = {}
        self.update_callbacks: List[Callable] = []
        self.render_callbacks: List[Callable] = []
        
        # Performance monitoring
        self.frame_times = []
        self.max_frame_history = 100
        
        # Event callbacks
        self.on_start_callbacks: List[Callable] = []
        self.on_stop_callbacks: List[Callable] = []
        self.on_pause_callbacks: List[Callable] = []
        self.on_resume_callbacks: List[Callable] = []
        self.on_step_callbacks: List[Callable] = []
        
        # Physics engine
        self.physics_engine = PhysicsEngine(gui=False)
        self.vehicle_state = self.physics_engine.get_vehicle_state()
        
        # AI/Path Planning
        self.path_planner = None
        self.obstacle_avoidance = None
        self.current_path = None
        self.current_waypoint_index = 0
        self.waypoint_tolerance = 2.0
        self.ai_navigation_enabled = False
        self.target_position = [0, 0, 0]
        
        # Initialize path planning
        self._init_path_planning()
    
    def register_component(self, name: str, component: SimulationComponent):
        """
        Register a simulation component.
        
        Args:
            name: Component name
            component: Component instance
        """
        self.components[name] = component
        self.logger.info(f"Registered component: {name}")
    
    def unregister_component(self, name: str):
        """
        Unregister a simulation component.
        
        Args:
            name: Component name
        """
        if name in self.components:
            del self.components[name]
            self.logger.info(f"Unregistered component: {name}")
    
    def add_update_callback(self, callback: Callable):
        """
        Add a callback to be called during simulation updates.
        
        Args:
            callback: Update callback function
        """
        self.update_callbacks.append(callback)
    
    def add_render_callback(self, callback: Callable):
        """
        Add a callback to be called during rendering.
        
        Args:
            callback: Render callback function
        """
        self.render_callbacks.append(callback)
    
    def add_event_callback(self, event: str, callback: Callable):
        """
        Add an event callback.
        
        Args:
            event: Event type ('start', 'stop', 'pause', 'resume', 'step')
            callback: Event callback function
        """
        if event == 'start':
            self.on_start_callbacks.append(callback)
        elif event == 'stop':
            self.on_stop_callbacks.append(callback)
        elif event == 'pause':
            self.on_pause_callbacks.append(callback)
        elif event == 'resume':
            self.on_resume_callbacks.append(callback)
        elif event == 'step':
            self.on_step_callbacks.append(callback)
    
    def start(self):
        """Start the simulation."""
        if self.state == SimulationState.RUNNING:
            return
        
        self.logger.info("Starting simulation")
        self.state = SimulationState.RUNNING
        self.running = True
        self.paused = False
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        # Call start callbacks
        for callback in self.on_start_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in start callback: {e}")
    
    def stop(self):
        """Stop the simulation."""
        if self.state == SimulationState.STOPPED:
            return
        
        self.logger.info("Stopping simulation")
        self.running = False
        self.state = SimulationState.STOPPED
        
        # Wait for thread to finish
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        
        # Call stop callbacks
        for callback in self.on_stop_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in stop callback: {e}")
    
    def pause(self):
        """Pause the simulation."""
        if self.state != SimulationState.RUNNING:
            return
        
        self.logger.info("Pausing simulation")
        self.paused = True
        self.state = SimulationState.PAUSED
        
        # Call pause callbacks
        for callback in self.on_pause_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in pause callback: {e}")
    
    def resume(self):
        """Resume the simulation."""
        if self.state != SimulationState.PAUSED:
            return
        
        self.logger.info("Resuming simulation")
        self.paused = False
        self.state = SimulationState.RUNNING
        
        # Call resume callbacks
        for callback in self.on_resume_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in resume callback: {e}")
    
    def step(self, steps: int = 1):
        """
        Step the simulation forward.
        
        Args:
            steps: Number of steps to advance
        """
        if self.state == SimulationState.RUNNING:
            return
        
        self.logger.info(f"Stepping simulation by {steps} steps")
        self.state = SimulationState.STEPPING
        
        for _ in range(steps):
            self._update_simulation()
        
        self.state = SimulationState.PAUSED
        
        # Call step callbacks
        for callback in self.on_step_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in step callback: {e}")
    
    def reset(self):
        """Reset the simulation to initial state."""
        self.logger.info("Resetting simulation")
        self.simulation_time = 0.0
        self.real_time = 0.0
        self.stats = SimulationStats()
        self.frame_times.clear()
        self.physics_engine.reset()
        self.vehicle_state = self.physics_engine.get_vehicle_state()
        
        # Reset components
        for component in self.components.values():
            component.reset()
        
        # Reset AI/Path Planning
        self.path_planner = None
        self.obstacle_avoidance = None
        self.current_path = None
        self.current_waypoint_index = 0
        self.ai_navigation_enabled = False
        self.target_position = [0, 0, 0]
        
        # Initialize path planning
        self._init_path_planning()
    
    def set_time_scale(self, scale: float):
        """
        Set the simulation time scale.
        
        Args:
            scale: Time scale factor (1.0 = real-time)
        """
        self.time_scale = max(0.0, min(10.0, scale))
        self.logger.info(f"Time scale set to {self.time_scale}")
    
    def get_simulation_time(self) -> float:
        """Get current simulation time."""
        return self.simulation_time
    
    def get_real_time(self) -> float:
        """Get elapsed real time."""
        return self.real_time
    
    def get_stats(self) -> SimulationStats:
        """Get simulation statistics."""
        return self.stats
    
    def _simulation_loop(self):
        """Main simulation loop."""
        last_time = time.time()
        frame_count = 0
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            
            # Calculate target frame time
            target_frame_time = 1.0 / self.target_fps
            
            # Skip frame if too fast
            if delta_time < target_frame_time:
                time.sleep(target_frame_time - delta_time)
                continue
            
            # Update frame timing
            frame_time = time.time() - last_time
            self.frame_times.append(frame_time)
            
            # Keep only recent frame times
            if len(self.frame_times) > self.max_frame_history:
                self.frame_times.pop(0)
            
            # Update statistics
            self.stats.frame_time = frame_time
            self.stats.fps = 1.0 / frame_time if frame_time > 0 else 0
            self.stats.simulation_time = self.simulation_time
            self.stats.real_time = self.real_time
            self.stats.time_scale = self.time_scale
            self.stats.total_frames = frame_count
            
            # Update simulation if not paused
            if not self.paused:
                self._update_simulation()
            
            # Call render callbacks
            for callback in self.render_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in render callback: {e}")
            
            last_time = current_time
            frame_count += 1
            
            # Check for maximum simulation time
            if self.simulation_time >= self.max_time:
                self.logger.info("Maximum simulation time reached")
                self.stop()
                break
    
    def _init_path_planning(self):
        """Initialize path planning components."""
        path_config = self.config.get_section('path_planning')
        
        # Create path planner based on configuration
        algorithm = path_config.get('algorithm', 'rrt')
        if algorithm == 'rrt':
            self.path_planner = RRTPlanner(path_config)
        elif algorithm == 'a_star':
            self.path_planner = AStarPlanner(path_config)
        else:
            self.path_planner = RRTPlanner(path_config)  # Default
        
        # Create obstacle avoidance
        avoidance_config = {
            'safety_margin': 2.0,
            'look_ahead_distance': 10.0,
            'max_avoidance_force': 5.0,
            'vehicle_radius': 1.0,
            'max_speed': 10.0
        }
        self.obstacle_avoidance = ObstacleAvoidance(avoidance_config)

    def set_target_position(self, target: List[float]):
        """Set the target position for AI navigation."""
        self.target_position = target
        self.ai_navigation_enabled = True
        self._plan_path_to_target()

    def _plan_path_to_target(self):
        """Plan a path to the current target."""
        if not self.path_planner:
            return
        
        # Get current vehicle position
        vehicle_state = self.get_vehicle_state()
        start_pos = (vehicle_state['position'][0], vehicle_state['position'][2])  # x, z
        goal_pos = (self.target_position[0], self.target_position[2])  # x, z
        
        # Update obstacles for path planner
        obstacles = []
        for obstacle in self.obstacle_avoidance.obstacles:
            obstacles.append({
                'type': obstacle.obstacle_type,
                'position': [obstacle.position[0], 0, obstacle.position[1]],
                'radius': obstacle.radius
            })
        self.path_planner.set_obstacles(obstacles)
        
        # Plan path
        path_result = self.path_planner.plan_path(start_pos, goal_pos)
        
        if path_result.success:
            self.current_path = path_result.waypoints
            self.current_waypoint_index = 0
            self.logger.info(f"Path planned successfully: {len(self.current_path)} waypoints")
        else:
            self.current_path = None
            self.logger.warning("Failed to plan path to target")

    def _update_ai_navigation(self):
        """Update AI navigation and waypoint following."""
        if not self.ai_navigation_enabled or not self.current_path:
            return
        
        vehicle_state = self.get_vehicle_state()
        vehicle_pos = (vehicle_state['position'][0], vehicle_state['position'][2])
        
        # Check if we reached the current waypoint
        if self.current_waypoint_index < len(self.current_path):
            current_waypoint = self.current_path[self.current_waypoint_index]
            distance_to_waypoint = math.sqrt(
                (vehicle_pos[0] - current_waypoint[0])**2 + 
                (vehicle_pos[1] - current_waypoint[1])**2
            )
            
            if distance_to_waypoint < self.waypoint_tolerance:
                self.current_waypoint_index += 1
                self.logger.info(f"Reached waypoint {self.current_waypoint_index - 1}")
        
        # Calculate desired velocity towards next waypoint
        if self.current_waypoint_index < len(self.current_path):
            next_waypoint = self.current_path[self.current_waypoint_index]
            
            # Calculate direction to waypoint
            direction = [
                next_waypoint[0] - vehicle_pos[0],
                next_waypoint[1] - vehicle_pos[1]
            ]
            
            # Normalize direction
            distance = math.sqrt(direction[0]**2 + direction[1]**2)
            if distance > 0:
                direction = [d / distance for d in direction]
                
                # Calculate desired velocity
                desired_speed = 5.0  # m/s
                desired_velocity = [d * desired_speed for d in direction]
                
                # Apply obstacle avoidance
                safe_velocity = self.obstacle_avoidance.get_safe_velocity(
                    desired_velocity, vehicle_pos
                )
                
                # Convert to vehicle controls
                self._convert_velocity_to_controls(safe_velocity, vehicle_state)
        else:
            # Reached final waypoint
            self.ai_navigation_enabled = False
            self.current_path = None
            self.logger.info("Reached final waypoint")

    def _convert_velocity_to_controls(self, velocity: List[float], vehicle_state: Dict):
        """Convert desired velocity to vehicle controls."""
        # Get current vehicle orientation
        orientation = vehicle_state['orientation']
        
        # Convert quaternion to yaw
        qw, qx, qy, qz = orientation[3], orientation[0], orientation[1], orientation[2]
        yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
        
        # Calculate desired heading
        desired_heading = math.atan2(velocity[1], velocity[0])
        
        # Calculate heading error
        heading_error = desired_heading - yaw
        
        # Normalize heading error to [-pi, pi]
        while heading_error > math.pi:
            heading_error -= 2 * math.pi
        while heading_error < -math.pi:
            heading_error += 2 * math.pi
        
        # Calculate speed
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
        
        # Convert to controls
        max_speed = 10.0
        throttle = min(speed / max_speed, 1.0)
        steering = max(-1.0, min(1.0, heading_error / (math.pi / 4)))  # Scale to [-1, 1]
        
        # Set vehicle controls
        self.set_vehicle_control(throttle, 0.0, steering)

    def add_obstacle(self, position: List[float], radius: float = 1.0, 
                    velocity: List[float] = None, obstacle_type: str = "circle"):
        """Add an obstacle for path planning and avoidance."""
        if velocity is None:
            velocity = [0.0, 0.0]
        
        obstacle = Obstacle(
            position=(position[0], position[2]),  # x, z
            radius=radius,
            velocity=(velocity[0], velocity[2]),
            obstacle_type=obstacle_type
        )
        
        self.obstacle_avoidance.add_obstacle(obstacle)
        
        # Replan path if AI navigation is active
        if self.ai_navigation_enabled:
            self._plan_path_to_target()

    def get_current_path(self) -> Optional[List[Tuple[float, float]]]:
        """Get the current planned path."""
        return self.current_path

    def get_path_planning_stats(self) -> Dict[str, Any]:
        """Get path planning statistics."""
        if not self.current_path:
            return {}
        
        return {
            'path_length': len(self.current_path),
            'current_waypoint': self.current_waypoint_index,
            'ai_navigation_enabled': self.ai_navigation_enabled,
            'target_position': self.target_position
        }

    def _update_simulation(self):
        """Update simulation state."""
        # Update simulation time
        self.simulation_time += self.time_step * self.time_scale
        self.real_time += self.time_step
        
        # Step physics engine
        throttle = getattr(self, 'throttle', 0.0)
        brake = getattr(self, 'brake', 0.0)
        steering = getattr(self, 'steering', 0.0)
        self.physics_engine.step(throttle, brake, steering)
        self.vehicle_state = self.physics_engine.get_vehicle_state()
        
        # Update AI navigation
        self._update_ai_navigation()
        
        # Update components
        for component in self.components.values():
            try:
                component.update(self.time_step)
            except Exception as e:
                self.logger.error(f"Error updating component {component.__class__.__name__}: {e}")
        
        # Call update callbacks
        for callback in self.update_callbacks:
            try:
                callback(self.time_step)
            except Exception as e:
                self.logger.error(f"Error in update callback: {e}")
    
    def get_component(self, name: str) -> Optional[SimulationComponent]:
        """
        Get a registered component.
        
        Args:
            name: Component name
            
        Returns:
            Component instance or None if not found
        """
        return self.components.get(name)
    
    def get_components(self) -> Dict[str, SimulationComponent]:
        """Get all registered components."""
        return self.components.copy()
    
    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self.state == SimulationState.RUNNING
    
    def is_paused(self) -> bool:
        """Check if simulation is paused."""
        return self.state == SimulationState.PAUSED
    
    def get_state(self) -> SimulationState:
        """Get current simulation state."""
        return self.state
    
    def get_vehicle_state(self):
        """Get the current vehicle state from the physics engine."""
        return self.vehicle_state.copy()
    
    def set_vehicle_control(self, throttle: float, brake: float, steering: float):
        """Set the vehicle control inputs for the next simulation step."""
        self.throttle = throttle
        self.brake = brake
        self.steering = steering 