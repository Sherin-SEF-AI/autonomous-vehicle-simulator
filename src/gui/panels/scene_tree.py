"""
Scene tree panel for managing simulation objects.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton,
    QHBoxLayout, QLabel, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class SceneTreePanel(QWidget):
    """Panel for displaying and managing simulation objects in a tree structure."""
    
    # Signals
    object_selected = pyqtSignal(str, object)
    object_deleted = pyqtSignal(str)
    object_added = pyqtSignal(str, str)  # type, name
    
    def __init__(self, config_manager):
        """
        Initialize the scene tree panel.
        
        Args:
            config_manager: Configuration manager
        """
        super().__init__()
        
        self.config = config_manager
        self.objects = {}  # name -> object mapping
        
        self.setup_ui()
        self.setup_context_menu()
        self.load_default_scene()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Scene Objects"))
        
        # Add object button
        self.add_button = QPushButton("+")
        self.add_button.setMaximumWidth(30)
        self.add_button.clicked.connect(self.show_add_menu)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Objects")
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)
    
    def setup_context_menu(self):
        """Setup the context menu."""
        self.context_menu = QMenu(self)
        
        # Add actions
        add_vehicle_action = QAction("Add Vehicle", self)
        add_vehicle_action.triggered.connect(lambda: self.add_object("vehicle", "New Vehicle"))
        self.context_menu.addAction(add_vehicle_action)
        
        add_obstacle_action = QAction("Add Obstacle", self)
        add_obstacle_action.triggered.connect(lambda: self.add_object("obstacle", "New Obstacle"))
        self.context_menu.addAction(add_obstacle_action)
        
        add_pedestrian_action = QAction("Add Pedestrian", self)
        add_pedestrian_action.triggered.connect(lambda: self.add_object("pedestrian", "New Pedestrian"))
        self.context_menu.addAction(add_pedestrian_action)
        
        self.context_menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected)
        self.context_menu.addAction(delete_action)
    
    def load_default_scene(self):
        """Load the default scene objects."""
        # Add default vehicle
        self.add_object("vehicle", "Main Vehicle", is_default=True)
        
        # Add some obstacles
        self.add_object("obstacle", "Building 1", is_default=True)
        self.add_object("obstacle", "Building 2", is_default=True)
        self.add_object("obstacle", "Tree 1", is_default=True)
        
        # Add a pedestrian
        self.add_object("pedestrian", "Pedestrian 1", is_default=True)
    
    def add_object(self, obj_type: str, name: str, is_default: bool = False):
        """
        Add an object to the scene tree.
        
        Args:
            obj_type: Type of object (vehicle, obstacle, pedestrian, etc.)
            name: Name of the object
            is_default: Whether this is a default object
        """
        # Create tree item
        item = QTreeWidgetItem(self.tree)
        item.setText(0, name)
        item.setData(0, Qt.UserRole, obj_type)
        
        # Set icon based on type
        if obj_type == "vehicle":
            item.setIcon(0, self.get_icon("🚗"))
        elif obj_type == "obstacle":
            item.setIcon(0, self.get_icon("🏢"))
        elif obj_type == "pedestrian":
            item.setIcon(0, self.get_icon("🚶"))
        else:
            item.setIcon(0, self.get_icon("📦"))
        
        # Create object data
        obj_data = {
            'type': obj_type,
            'name': name,
            'position': [0, 0, 0],
            'orientation': [0, 0, 0],
            'visible': True,
            'is_default': is_default
        }
        
        self.objects[name] = obj_data
        
        # Emit signal
        if not is_default:
            self.object_added.emit(obj_type, name)
        
        return item
    
    def delete_selected(self):
        """Delete the selected object."""
        current_item = self.tree.currentItem()
        if current_item:
            name = current_item.text(0)
            obj_data = self.objects.get(name)
            
            if obj_data and not obj_data.get('is_default', False):
                # Remove from tree
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(current_item))
                
                # Remove from objects dict
                del self.objects[name]
                
                # Emit signal
                self.object_deleted.emit(name)
    
    def on_item_clicked(self, item, column):
        """Handle item click."""
        name = item.text(0)
        obj_data = self.objects.get(name)
        if obj_data:
            self.object_selected.emit(name, obj_data)
    
    def show_context_menu(self, position):
        """Show the context menu."""
        self.context_menu.exec_(self.tree.mapToGlobal(position))
    
    def show_add_menu(self):
        """Show the add object menu."""
        self.context_menu.exec_(self.add_button.mapToGlobal(self.add_button.rect().bottomLeft()))
    
    def get_icon(self, emoji: str):
        """Get an icon from emoji (placeholder)."""
        # In a real implementation, this would return actual QIcon objects
        return QIcon()
    
    def get_objects(self):
        """Get all objects in the scene."""
        return self.objects.copy()
    
    def update_object(self, name: str, data: dict):
        """Update an object's data."""
        if name in self.objects:
            self.objects[name].update(data)
    
    def clear_scene(self):
        """Clear all objects from the scene."""
        self.tree.clear()
        self.objects.clear()
    
    def select_object(self, name: str):
        """Select an object in the tree."""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == name:
                self.tree.setCurrentItem(item)
                break 