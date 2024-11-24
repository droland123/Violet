# gui/device_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeWidget, 
                            QTreeWidgetItem, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os

class DevicePanel(QWidget):
    def __init__(self):
        super().__init__()
        # Look for icon in assets directory
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add header
        header = QLabel("Devices")
        header.setStyleSheet("QLabel { padding: 10px; font-weight: bold; }")
        layout.addWidget(header)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Add tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # Hide the header
        self.tree.setIndentation(10)
        layout.addWidget(self.tree)
        
        # Add iPod device
        self.add_device("iPod Classic")
    
    def add_device(self, name):
        device_item = QTreeWidgetItem(self.tree)
        device_item.setText(0, name)
        # Only set icon if the file exists
        if os.path.exists(self.icon_path):
            device_item.setIcon(0, QIcon(self.icon_path))
        self.tree.addTopLevelItem(device_item)