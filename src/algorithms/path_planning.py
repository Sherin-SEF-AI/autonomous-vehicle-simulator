"""
Path planning algorithms for autonomous vehicle navigation.

Includes RRT (Rapidly-exploring Random Trees) and A* algorithms.
"""

import numpy as np
import math
import random
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging


class PathPlanningAlgorithm(Enum):
    """Available path planning algorithms."""
    RRT = "rrt"
    A_STAR = "a_star"
    RRT_STAR = "rrt_star"


@dataclass
class Node:
    """Node in the path planning tree/graph."""
    x: float
    y: float
    parent: Optional['Node'] = None
    cost: float = 0.0
    heuristic: float = 0.0
    total_cost: float = 0.0


@dataclass
class Path:
    """Path planning result."""
    waypoints: List[Tuple[float, float]]
    cost: float
    algorithm: str
    computation_time: float
    success: bool
    metadata: Dict[str, Any]


class PathPlanner:
    """Base class for path planning algorithms."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the path planner.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Planning parameters
        self.max_iterations = config.get('max_iterations', 1000)
        self.goal_tolerance = config.get('goal_tolerance', 0.5)
        self.step_size = config.get('step_size', 1.0)
        
        # Environment bounds
        self.x_min = config.get('x_min', -100)
        self.x_max = config.get('x_max', 100)
        self.y_min = config.get('y_min', -100)
        self.y_max = config.get('y_max', 100)
        
        # Obstacles
        self.obstacles: List[Dict[str, Any]] = []
        
        # Vehicle constraints
        self.vehicle_radius = config.get('vehicle_radius', 1.0)
        self.min_turning_radius = config.get('min_turning_radius', 5.0)
    
    def set_obstacles(self, obstacles: List[Dict[str, Any]]):
        """Set the obstacle list."""
        self.obstacles = obstacles
    
    def add_obstacle(self, obstacle: Dict[str, Any]):
        """Add a single obstacle."""
        self.obstacles.append(obstacle)
    
    def clear_obstacles(self):
        """Clear all obstacles."""
        self.obstacles.clear()
    
    def is_valid_position(self, x: float, y: float) -> bool:
        """
        Check if a position is valid (within bounds and not colliding).
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position is valid
        """
        # Check bounds
        if not (self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max):
            return False
        
        # Check obstacle collisions
        for obstacle in self.obstacles:
            if self._check_obstacle_collision(x, y, obstacle):
                return False
        
        return True
    
    def _check_obstacle_collision(self, x: float, y: float, obstacle: Dict[str, Any]) -> bool:
        """Check collision with a specific obstacle."""
        obstacle_type = obstacle.get('type', 'circle')
        
        if obstacle_type == 'circle':
            ox, oy = obstacle['position'][:2]
            radius = obstacle.get('radius', 1.0)
            distance = math.sqrt((x - ox)**2 + (y - oy)**2)
            return distance < (radius + self.vehicle_radius)
        
        elif obstacle_type == 'rectangle':
            ox, oy = obstacle['position'][:2]
            width = obstacle.get('width', 2.0)
            height = obstacle.get('height', 2.0)
            
            # Check if point is inside rectangle
            if (ox - width/2 <= x <= ox + width/2 and 
                oy - height/2 <= y <= oy + height/2):
                return True
        
        return False
    
    def distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def plan_path(self, start: Tuple[float, float], goal: Tuple[float, float]) -> Path:
        """
        Plan a path from start to goal.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            
        Returns:
            Path object with waypoints and metadata
        """
        raise NotImplementedError("Subclasses must implement plan_path")


class RRTPlanner(PathPlanner):
    """Rapidly-exploring Random Trees path planner."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize RRT planner."""
        super().__init__(config)
        
        # RRT-specific parameters
        self.goal_bias = config.get('goal_bias', 0.1)
        self.max_step_size = config.get('max_step_size', 2.0)
        self.tree: List[Node] = []
    
    def plan_path(self, start: Tuple[float, float], goal: Tuple[float, float]) -> Path:
        """Plan path using RRT algorithm."""
        import time
        start_time = time.time()
        
        # Initialize tree with start node
        self.tree = [Node(start[0], start[1])]
        
        for iteration in range(self.max_iterations):
            # Generate random point
            if random.random() < self.goal_bias:
                random_point = goal
            else:
                random_point = self._generate_random_point()
            
            # Find nearest neighbor
            nearest_node = self._find_nearest_neighbor(random_point)
            
            # Extend towards random point
            new_node = self._extend_towards(nearest_node, random_point)
            
            if new_node and self.is_valid_position(new_node.x, new_node.y):
                self.tree.append(new_node)
                
                # Check if we reached the goal
                if self.distance((new_node.x, new_node.y), goal) < self.goal_tolerance:
                    # Extract path
                    path = self._extract_path(new_node)
                    computation_time = time.time() - start_time
                    
                    return Path(
                        waypoints=path,
                        cost=self._calculate_path_cost(path),
                        algorithm="RRT",
                        computation_time=computation_time,
                        success=True,
                        metadata={
                            'iterations': iteration + 1,
                            'tree_size': len(self.tree)
                        }
                    )
        
        # Failed to find path
        computation_time = time.time() - start_time
        return Path(
            waypoints=[],
            cost=float('inf'),
            algorithm="RRT",
            computation_time=computation_time,
            success=False,
            metadata={'iterations': self.max_iterations, 'tree_size': len(self.tree)}
        )
    
    def _generate_random_point(self) -> Tuple[float, float]:
        """Generate a random point within bounds."""
        x = random.uniform(self.x_min, self.x_max)
        y = random.uniform(self.y_min, self.y_max)
        return (x, y)
    
    def _find_nearest_neighbor(self, point: Tuple[float, float]) -> Node:
        """Find the nearest node in the tree to the given point."""
        nearest = None
        min_distance = float('inf')
        
        for node in self.tree:
            distance = self.distance((node.x, node.y), point)
            if distance < min_distance:
                min_distance = distance
                nearest = node
        
        return nearest
    
    def _extend_towards(self, from_node: Node, to_point: Tuple[float, float]) -> Optional[Node]:
        """Extend from a node towards a point."""
        direction = np.array([to_point[0] - from_node.x, to_point[1] - from_node.y])
        distance = np.linalg.norm(direction)
        
        if distance == 0:
            return None
        
        # Normalize and scale
        direction = direction / distance
        step_distance = min(distance, self.max_step_size)
        
        new_x = from_node.x + direction[0] * step_distance
        new_y = from_node.y + direction[1] * step_distance
        
        return Node(new_x, new_y, parent=from_node)
    
    def _extract_path(self, goal_node: Node) -> List[Tuple[float, float]]:
        """Extract path from goal node back to start."""
        path = []
        current = goal_node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        return list(reversed(path))
    
    def _calculate_path_cost(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total path cost."""
        if len(path) < 2:
            return 0.0
        
        total_cost = 0.0
        for i in range(len(path) - 1):
            total_cost += self.distance(path[i], path[i + 1])
        
        return total_cost


class AStarPlanner(PathPlanner):
    """A* path planner using grid-based search."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize A* planner."""
        super().__init__(config)
        
        # Grid parameters
        self.grid_resolution = config.get('grid_resolution', 0.5)
        self.grid_width = int((self.x_max - self.x_min) / self.grid_resolution)
        self.grid_height = int((self.y_max - self.y_min) / self.grid_resolution)
        
        # Heuristic function
        self.heuristic_type = config.get('heuristic', 'euclidean')
    
    def plan_path(self, start: Tuple[float, float], goal: Tuple[float, float]) -> Path:
        """Plan path using A* algorithm."""
        import time
        start_time = time.time()
        
        # Convert to grid coordinates
        start_grid = self._world_to_grid(start)
        goal_grid = self._world_to_grid(goal)
        
        # Initialize open and closed sets
        open_set = {start_grid}
        closed_set = set()
        
        # Node information
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self._heuristic(start_grid, goal_grid)}
        
        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            # Check if we reached the goal
            if self._heuristic(current, goal_grid) < self.goal_tolerance / self.grid_resolution:
                # Extract path
                path = self._reconstruct_path(came_from, current)
                world_path = [self._grid_to_world(p) for p in path]
                
                computation_time = time.time() - start_time
                return Path(
                    waypoints=world_path,
                    cost=self._calculate_path_cost(world_path),
                    algorithm="A*",
                    computation_time=computation_time,
                    success=True,
                    metadata={
                        'grid_size': (self.grid_width, self.grid_height),
                        'nodes_explored': len(closed_set)
                    }
                )
            
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score[current] + self._distance(current, neighbor)
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue
                
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, goal_grid)
        
        # Failed to find path
        computation_time = time.time() - start_time
        return Path(
            waypoints=[],
            cost=float('inf'),
            algorithm="A*",
            computation_time=computation_time,
            success=False,
            metadata={'grid_size': (self.grid_width, self.grid_height)}
        )
    
    def _world_to_grid(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates."""
        x = int((world_pos[0] - self.x_min) / self.grid_resolution)
        y = int((world_pos[1] - self.y_min) / self.grid_resolution)
        return (max(0, min(x, self.grid_width - 1)), max(0, min(y, self.grid_height - 1)))
    
    def _grid_to_world(self, grid_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates."""
        x = grid_pos[0] * self.grid_resolution + self.x_min
        y = grid_pos[1] * self.grid_resolution + self.y_min
        return (x, y)
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Calculate heuristic distance between two grid points."""
        if self.heuristic_type == 'manhattan':
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        else:  # euclidean
            return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
    
    def _distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Calculate distance between two grid points."""
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
    
    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighbors of a grid position."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x, new_y = pos[0] + dx, pos[1] + dy
                if (0 <= new_x < self.grid_width and 
                    0 <= new_y < self.grid_height and
                    self.is_valid_position(*self._grid_to_world((new_x, new_y)))):
                    neighbors.append((new_x, new_y))
        
        return neighbors
    
    def _reconstruct_path(self, came_from: Dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))
    
    def _calculate_path_cost(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total path cost."""
        if len(path) < 2:
            return 0.0
        
        total_cost = 0.0
        for i in range(len(path) - 1):
            total_cost += self.distance(path[i], path[i + 1])
        
        return total_cost 