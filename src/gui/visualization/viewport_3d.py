"""
3D viewport with OpenGL rendering for the simulation environment.
"""

from PyQt5.QtWidgets import QOpenGLWidget, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
import numpy as np
import math
from PyQt5 import QtCore

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False


class Viewport3D(QOpenGLWidget):
    """3D viewport with OpenGL rendering."""
    
    # Signals
    camera_changed = pyqtSignal(dict)
    object_selected = pyqtSignal(str, object)
    
    def __init__(self, config_manager, simulation_manager):
        """
        Initialize the 3D viewport.
        
        Args:
            config_manager: Configuration manager
            simulation_manager: Simulation manager
        """
        super().__init__()
        
        self.config = config_manager
        self.simulation_manager = simulation_manager
        
        # Camera settings
        self.camera_distance = 50.0
        self.camera_azimuth = 45.0
        self.camera_elevation = 30.0
        self.camera_target = [0, 0, 0]
        
        # Mouse interaction
        self.mouse_pressed = False
        self.last_mouse_pos = None
        
        # Scene objects
        self.objects = {}
        
        # Rendering settings
        self.show_grid = True
        self.show_axes = True
        self.show_wireframe = False
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_scene)
        self.update_timer.start(33)  # ~30 FPS
        
        # Set focus policy for keyboard events
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
    
    def initializeGL(self):
        """Initialize OpenGL context."""
        if not OPENGL_AVAILABLE:
            return
        
        from OpenGL.GL import glClearColor, glEnable, glDepthFunc, GL_DEPTH_TEST, GL_LESS, GL_LIGHTING, GL_LIGHT0, GL_COLOR_MATERIAL, glLightfv, GL_POSITION, GL_AMBIENT, GL_DIFFUSE, glHint, GL_LINE_SMOOTH, GL_POLYGON_SMOOTH, GL_LINE_SMOOTH_HINT, GL_POLYGON_SMOOTH_HINT, GL_NICEST
        
        # Set background color
        bg_color = self.config.get('visualization.background_color', [0.1, 0.1, 0.15])
        glClearColor(bg_color[0], bg_color[1], bg_color[2], 1.0)
        
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable lighting
        if self.config.get('visualization.lighting_enabled', True):
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            
            # Set up light
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        # Enable antialiasing
        if self.config.get('visualization.antialiasing', True):
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_POLYGON_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    
    def resizeGL(self, width, height):
        """Handle viewport resize."""
        if not OPENGL_AVAILABLE:
            return
        
        from OpenGL.GL import glViewport, glMatrixMode, glLoadIdentity, GL_PROJECTION, GL_MODELVIEW
        from OpenGL.GLU import gluPerspective
        
        glViewport(0, 0, width, height)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Set up perspective projection
        fov = self.config.get('visualization.camera.fov', 45)
        aspect = width / height if height > 0 else 1.0
        near_plane = self.config.get('visualization.camera.near_plane', 0.1)
        far_plane = self.config.get('visualization.camera.far_plane', 1000)
        
        gluPerspective(fov, aspect, near_plane, far_plane)
        
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Render the 3D scene."""
        if not OPENGL_AVAILABLE:
            self.render_fallback()
            return
        
        from OpenGL.GL import glClear, glLoadIdentity, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
        
        # Ensure both are integers for bitwise OR
        mask = int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT)
        glClear(mask)
        glLoadIdentity()
        
        # Set up camera
        self.setup_camera()
        
        # Draw grid
        if self.show_grid:
            self.draw_grid()
        
        # Draw coordinate axes
        if self.show_axes:
            self.draw_axes()
        
        # Draw scene objects
        self.draw_scene_objects()
        
        # Draw vehicle
        self.draw_vehicle()
        
        # Draw obstacles
        self.draw_obstacles()
        
        # Draw pedestrians
        self.draw_pedestrians()
    
    def render_fallback(self):
        """Render fallback when OpenGL is not available."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(26, 26, 26))
        
        # Draw fallback message
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(
            self.rect(), 
            QtCore.Qt.AlignCenter, 
            "3D Viewport\nOpenGL not available\n\n"
            "Install PyOpenGL to enable 3D rendering:\n"
            "pip install PyOpenGL"
        )
    
    def setup_camera(self):
        """Set up the camera view."""
        # Convert spherical coordinates to Cartesian
        azimuth_rad = np.radians(self.camera_azimuth)
        elevation_rad = np.radians(self.camera_elevation)
        
        x = self.camera_target[0] + self.camera_distance * np.cos(elevation_rad) * np.cos(azimuth_rad)
        y = self.camera_target[1] + self.camera_distance * np.sin(elevation_rad)
        z = self.camera_target[2] + self.camera_distance * np.cos(elevation_rad) * np.sin(azimuth_rad)
        
        # Look at target
        gluLookAt(
            x, y, z,  # Eye position
            self.camera_target[0], self.camera_target[1], self.camera_target[2],  # Target
            0, 1, 0  # Up vector
        )
    
    def draw_grid(self):
        """Draw the ground grid."""
        from OpenGL.GL import glDisable, glColor3f, glLineWidth, glBegin, glVertex3f, glEnd, glEnable, GL_LIGHTING, GL_LINES
        
        grid_size = self.config.get('visualization.grid_size', 100)
        grid_spacing = self.config.get('visualization.grid_spacing', 5)
        
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glLineWidth(1.0)
        
        glBegin(GL_LINES)
        
        # Draw grid lines
        for i in range(-grid_size, grid_size + 1, grid_spacing):
            # X lines
            glVertex3f(i, 0, -grid_size)
            glVertex3f(i, 0, grid_size)
            # Z lines
            glVertex3f(-grid_size, 0, i)
            glVertex3f(grid_size, 0, i)
        
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def draw_axes(self):
        """Draw coordinate axes."""
        from OpenGL.GL import glDisable, glLineWidth, glColor3f, glBegin, glVertex3f, glEnd, glEnable, GL_LIGHTING, GL_LINES
        
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        
        # X axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(10, 0, 0)
        glEnd()
        
        # Y axis (green)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 10, 0)
        glEnd()
        
        # Z axis (blue)
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 10)
        glEnd()
        
        glEnable(GL_LIGHTING)
    
    def draw_scene_objects(self):
        """Draw all scene objects."""
        for obj_name, obj_data in self.objects.items():
            if obj_data.get('visible', True):
                self.draw_object(obj_name, obj_data)
    
    def draw_object(self, obj_name: str, obj_data: dict):
        """Draw a single object."""
        from OpenGL.GL import glPushMatrix, glTranslatef, glRotatef, glPopMatrix
        obj_type = obj_data.get('type', 'unknown')
        position = obj_data.get('position', [0, 0, 0])
        orientation = obj_data.get('orientation', [0, 0, 0])
        
        glPushMatrix()
        
        # Apply transformations
        glTranslatef(position[0], position[1], position[2])
        glRotatef(orientation[0], 1, 0, 0)  # Roll
        glRotatef(orientation[1], 0, 1, 0)  # Pitch
        glRotatef(orientation[2], 0, 0, 1)  # Yaw
        
        # Draw based on type
        if obj_type == 'vehicle':
            self.draw_vehicle_mesh(obj_data)
        elif obj_type == 'obstacle':
            self.draw_obstacle_mesh(obj_data)
        elif obj_type == 'pedestrian':
            self.draw_pedestrian_mesh(obj_data)
        
        glPopMatrix()
    
    def draw_vehicle_mesh(self, obj_data: dict):
        """Draw a vehicle mesh."""
        from OpenGL.GL import glColor3f, glBegin, glVertex3f, glEnd, GL_QUADS
        
        # Simple vehicle representation
        glColor3f(0.2, 0.6, 1.0)  # Blue
        
        # Draw vehicle body (box)
        length = 4.5
        width = 2.0
        height = 1.5
        
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-length/2, 0, -width/2)
        glVertex3f(-length/2, 0, width/2)
        glVertex3f(-length/2, height, width/2)
        glVertex3f(-length/2, height, -width/2)
        
        # Back face
        glVertex3f(length/2, 0, -width/2)
        glVertex3f(length/2, 0, width/2)
        glVertex3f(length/2, height, width/2)
        glVertex3f(length/2, height, -width/2)
        
        # Left face
        glVertex3f(-length/2, 0, -width/2)
        glVertex3f(length/2, 0, -width/2)
        glVertex3f(length/2, height, -width/2)
        glVertex3f(-length/2, height, -width/2)
        
        # Right face
        glVertex3f(-length/2, 0, width/2)
        glVertex3f(length/2, 0, width/2)
        glVertex3f(length/2, height, width/2)
        glVertex3f(-length/2, height, width/2)
        
        # Top face
        glVertex3f(-length/2, height, -width/2)
        glVertex3f(length/2, height, -width/2)
        glVertex3f(length/2, height, width/2)
        glVertex3f(-length/2, height, width/2)
        glEnd()
    
    def draw_obstacle_mesh(self, obj_data: dict):
        """Draw an obstacle mesh."""
        from OpenGL.GL import glColor3f, glBegin, glVertex3f, glEnd, GL_QUADS
        
        obstacle_type = obj_data.get('obstacle_type', 'building')
        size = obj_data.get('size', [1, 1, 1])
        
        if obstacle_type == 'building':
            glColor3f(0.7, 0.7, 0.7)  # Gray
        elif obstacle_type == 'tree':
            glColor3f(0.2, 0.8, 0.2)  # Green
        else:
            glColor3f(0.8, 0.8, 0.8)  # Light gray
        
        # Draw as a box
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-size[0]/2, 0, -size[2]/2)
        glVertex3f(-size[0]/2, 0, size[2]/2)
        glVertex3f(-size[0]/2, size[1], size[2]/2)
        glVertex3f(-size[0]/2, size[1], -size[2]/2)
        
        # Back face
        glVertex3f(size[0]/2, 0, -size[2]/2)
        glVertex3f(size[0]/2, 0, size[2]/2)
        glVertex3f(size[0]/2, size[1], size[2]/2)
        glVertex3f(size[0]/2, size[1], -size[2]/2)
        
        # Left face
        glVertex3f(-size[0]/2, 0, -size[2]/2)
        glVertex3f(size[0]/2, 0, -size[2]/2)
        glVertex3f(size[0]/2, size[1], -size[2]/2)
        glVertex3f(-size[0]/2, size[1], -size[2]/2)
        
        # Right face
        glVertex3f(-size[0]/2, 0, size[2]/2)
        glVertex3f(size[0]/2, 0, size[2]/2)
        glVertex3f(size[0]/2, size[1], size[2]/2)
        glVertex3f(-size[0]/2, size[1], size[2]/2)
        
        # Top face
        glVertex3f(-size[0]/2, size[1], -size[2]/2)
        glVertex3f(size[0]/2, size[1], -size[2]/2)
        glVertex3f(size[0]/2, size[1], size[2]/2)
        glVertex3f(-size[0]/2, size[1], size[2]/2)
        glEnd()
    
    def draw_pedestrian_mesh(self, obj_data: dict):
        """Draw a pedestrian mesh."""
        from OpenGL.GL import glColor3f, glBegin, glVertex3f, glEnd, GL_QUADS
        
        glColor3f(1.0, 0.8, 0.6)  # Skin color
        
        # Simple human representation (cylinder)
        height = 1.8
        radius = 0.3
        
        # Draw body (cylinder approximation)
        glBegin(GL_QUADS)
        for i in range(8):
            angle1 = i * 2 * np.pi / 8
            angle2 = (i + 1) * 2 * np.pi / 8
            
            x1 = radius * np.cos(angle1)
            z1 = radius * np.sin(angle1)
            x2 = radius * np.cos(angle2)
            z2 = radius * np.sin(angle2)
            
            # Side face
            glVertex3f(x1, 0, z1)
            glVertex3f(x2, 0, z2)
            glVertex3f(x2, height, z2)
            glVertex3f(x1, height, z1)
        glEnd()
    
    def draw_vehicle(self):
        """Draw the main vehicle using real-time state from the simulation manager."""
        from OpenGL.GL import glPushMatrix, glTranslatef, glRotatef, glPopMatrix
        
        vehicle_state = self.simulation_manager.get_vehicle_state()
        pos = vehicle_state['position']
        orn = vehicle_state['orientation']
        # Convert quaternion to Euler angles for OpenGL
        qw, qx, qy, qz = orn[3], orn[0], orn[1], orn[2]
        # Yaw, Pitch, Roll
        ysqr = qy * qy
        t0 = +2.0 * (qw * qz + qx * qy)
        t1 = +1.0 - 2.0 * (qy * qy + qz * qz)
        yaw = math.atan2(t0, t1)
        t2 = +2.0 * (qw * qy - qz * qx)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.asin(t2)
        t3 = +2.0 * (qw * qx + qy * qz)
        t4 = +1.0 - 2.0 * (qx * qx + qy * qy)
        roll = math.atan2(t3, t4)
        # Draw vehicle at real position and orientation
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        glRotatef(np.degrees(roll), 1, 0, 0)
        glRotatef(np.degrees(pitch), 0, 1, 0)
        glRotatef(np.degrees(yaw), 0, 0, 1)
        self.draw_vehicle_mesh({})
        glPopMatrix()
        
        # Draw planned path
        self.draw_planned_path()
        
        # Draw obstacles
        self.draw_obstacles()
    
    def draw_planned_path(self):
        """Draw the planned path from the simulation manager."""
        from OpenGL.GL import glDisable, glColor3f, glLineWidth, glBegin, glVertex3f, glEnd, glEnable, GL_LIGHTING, GL_LINES
        
        path = self.simulation_manager.get_current_path()
        if not path:
            return
        
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
        
        # Draw path lines
        glColor3f(0.0, 1.0, 0.0)  # Green for path
        glBegin(GL_LINES)
        
        for i in range(len(path) - 1):
            # Convert 2D path points to 3D (y=0)
            start_point = path[i]
            end_point = path[i + 1]
            
            glVertex3f(start_point[0], 0.1, start_point[1])  # Slightly above ground
            glVertex3f(end_point[0], 0.1, end_point[1])
        
        glEnd()
        
        # Draw waypoints
        glColor3f(1.0, 1.0, 0.0)  # Yellow for waypoints
        for i, waypoint in enumerate(path):
            # Draw waypoint as a small sphere (approximated with lines)
            x, z = waypoint[0], waypoint[1]
            radius = 0.5
            
            # Highlight current waypoint
            if i == self.simulation_manager.current_waypoint_index:
                glColor3f(1.0, 0.0, 0.0)  # Red for current waypoint
                radius = 1.0
            else:
                glColor3f(1.0, 1.0, 0.0)  # Yellow for other waypoints
            
            # Draw waypoint circle
            glBegin(GL_LINES)
            for angle in range(0, 360, 10):
                angle_rad = math.radians(angle)
                next_angle_rad = math.radians(angle + 10)
                
                x1 = x + radius * math.cos(angle_rad)
                z1 = z + radius * math.sin(angle_rad)
                x2 = x + radius * math.cos(next_angle_rad)
                z2 = z + radius * math.sin(next_angle_rad)
                
                glVertex3f(x1, 0.1, z1)
                glVertex3f(x2, 0.1, z2)
            glEnd()
        
        glEnable(GL_LIGHTING)
    
    def draw_obstacles(self):
        """Draw obstacles from the obstacle avoidance system."""
        from OpenGL.GL import glPushMatrix, glTranslatef, glColor3f, glBegin, glVertex3f, glEnd, GL_QUADS
        
        for obstacle in self.simulation_manager.obstacle_avoidance.obstacles:
            glPushMatrix()
            
            # Convert 2D obstacle position to 3D
            x, z = obstacle.position
            glTranslatef(x, 0, z)
            
            # Draw obstacle based on type
            if obstacle.obstacle_type == "circle":
                glColor3f(1.0, 0.0, 0.0)  # Red for obstacles
                
                # Draw as a cylinder (approximated with quads)
                radius = obstacle.radius
                height = 2.0
                
                # Draw cylinder sides
                glBegin(GL_QUADS)
                for angle in range(0, 360, 10):
                    angle_rad = math.radians(angle)
                    next_angle_rad = math.radians(angle + 10)
                    
                    x1 = radius * math.cos(angle_rad)
                    z1 = radius * math.sin(angle_rad)
                    x2 = radius * math.cos(next_angle_rad)
                    z2 = radius * math.sin(next_angle_rad)
                    
                    # Side face
                    glVertex3f(x1, 0, z1)
                    glVertex3f(x2, 0, z2)
                    glVertex3f(x2, height, z2)
                    glVertex3f(x1, height, z1)
                glEnd()
                
                # Draw top and bottom circles
                glBegin(GL_QUADS)
                for angle in range(0, 360, 10):
                    angle_rad = math.radians(angle)
                    next_angle_rad = math.radians(angle + 10)
                    
                    x1 = radius * math.cos(angle_rad)
                    z1 = radius * math.sin(angle_rad)
                    x2 = radius * math.cos(next_angle_rad)
                    z2 = radius * math.sin(next_angle_rad)
                    
                    # Top face
                    glVertex3f(0, height, 0)
                    glVertex3f(x1, height, z1)
                    glVertex3f(x2, height, z2)
                    glVertex3f(0, height, 0)
                    
                    # Bottom face
                    glVertex3f(0, 0, 0)
                    glVertex3f(x1, 0, z1)
                    glVertex3f(x2, 0, z2)
                    glVertex3f(0, 0, 0)
                glEnd()
            
            elif obstacle.obstacle_type == "rectangle":
                glColor3f(0.8, 0.4, 0.0)  # Orange for rectangular obstacles
                
                # Draw as a box
                width = obstacle.radius * 2
                height = 2.0
                
                glBegin(GL_QUADS)
                # Front face
                glVertex3f(-width/2, 0, -width/2)
                glVertex3f(-width/2, 0, width/2)
                glVertex3f(-width/2, height, width/2)
                glVertex3f(-width/2, height, -width/2)
                
                # Back face
                glVertex3f(width/2, 0, -width/2)
                glVertex3f(width/2, 0, width/2)
                glVertex3f(width/2, height, width/2)
                glVertex3f(width/2, height, -width/2)
                
                # Left face
                glVertex3f(-width/2, 0, -width/2)
                glVertex3f(width/2, 0, -width/2)
                glVertex3f(width/2, height, -width/2)
                glVertex3f(-width/2, height, -width/2)
                
                # Right face
                glVertex3f(-width/2, 0, width/2)
                glVertex3f(width/2, 0, width/2)
                glVertex3f(width/2, height, width/2)
                glVertex3f(-width/2, height, width/2)
                
                # Top face
                glVertex3f(-width/2, height, -width/2)
                glVertex3f(width/2, height, -width/2)
                glVertex3f(width/2, height, width/2)
                glVertex3f(-width/2, height, width/2)
                glEnd()
            
            glPopMatrix()
    
    def draw_pedestrians(self):
        """Draw pedestrians in the scene."""
        # This would draw all pedestrians
        pass
    
    def update_scene(self):
        """Update the scene (called by timer)."""
        # Update camera info
        camera_info = {
            'distance': self.camera_distance,
            'azimuth': self.camera_azimuth,
            'elevation': self.camera_elevation,
            'target': self.camera_target.copy()
        }
        self.camera_changed.emit(camera_info)
        
        # Request redraw
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        self.mouse_pressed = True
        self.last_mouse_pos = event.pos()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        self.mouse_pressed = False
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.mouse_pressed and self.last_mouse_pos:
            # Calculate mouse movement
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            # Rotate camera
            if event.buttons() & QtCore.Qt.LeftButton:
                self.camera_azimuth += dx * 0.5
                self.camera_elevation += dy * 0.5
                self.camera_elevation = max(-89, min(89, self.camera_elevation))
            
            # Zoom camera
            elif event.buttons() & QtCore.Qt.RightButton:
                self.camera_distance += dy * 0.5
                self.camera_distance = max(1, min(500, self.camera_distance))
            
            self.last_mouse_pos = event.pos()
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.camera_distance *= zoom_factor
        self.camera_distance = max(1, min(500, self.camera_distance))
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        key = event.key()
        
        if key == QtCore.Qt.Key_R:
            # Reset view
            self.camera_azimuth = 45.0
            self.camera_elevation = 30.0
            self.camera_distance = 50.0
            self.camera_target = [0, 0, 0]
        elif key == QtCore.Qt.Key_G:
            # Toggle grid
            self.show_grid = not self.show_grid
        elif key == QtCore.Qt.Key_A:
            # Toggle axes
            self.show_axes = not self.show_axes
        elif key == QtCore.Qt.Key_W:
            # Toggle wireframe
            self.show_wireframe = not self.show_wireframe
            from OpenGL.GL import glPolygonMode, GL_FRONT_AND_BACK, GL_LINE, GL_FILL
            if self.show_wireframe:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def add_object(self, name: str, obj_data: dict):
        """Add an object to the scene."""
        self.objects[name] = obj_data
    
    def remove_object(self, name: str):
        """Remove an object from the scene."""
        if name in self.objects:
            del self.objects[name]
    
    def update_object(self, name: str, obj_data: dict):
        """Update an object in the scene."""
        if name in self.objects:
            self.objects[name].update(obj_data)
    
    def clear_scene(self):
        """Clear all objects from the scene."""
        self.objects.clear()
    
    def get_camera_info(self) -> dict:
        """Get current camera information."""
        return {
            'distance': self.camera_distance,
            'azimuth': self.camera_azimuth,
            'elevation': self.camera_elevation,
            'target': self.camera_target.copy()
        }
    
    def set_camera(self, distance: float = None, azimuth: float = None, 
                   elevation: float = None, target: list = None):
        """Set camera parameters."""
        if distance is not None:
            self.camera_distance = distance
        if azimuth is not None:
            self.camera_azimuth = azimuth
        if elevation is not None:
            self.camera_elevation = elevation
        if target is not None:
            self.camera_target = target 