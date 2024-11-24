# gui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QFrame, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QAction
from config.settings import Settings
from .device_panel import DevicePanel
from .library_panel import LibraryPanel
from .controls_panel import ControlsPanel
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.loading_dialog import LoadingDialog
from .menus.macos_menu import MacOSMenuBar
from media.music_processor import MusicProcessor
from config.settings_manager import settings_manager
import os

class MainWindow(QMainWindow):
    def __init__(self, player, db_manager, spotify_service):
        super().__init__()
        self.player = player
        self.db_manager = db_manager
        self.spotify_service = spotify_service
        self.music_processor = MusicProcessor()
        
        # Initialize GUI
        self.setup_ui()
        
        # Initialize menus
        self.menu_bar = MacOSMenuBar(self)
        
        # Load library after GUI is setup
        self.load_library()

    def setup_ui(self):
        self.setWindowTitle("Music Sync")
        self.setMinimumSize(Settings.WINDOW_MIN_WIDTH, Settings.WINDOW_MIN_HEIGHT)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for device and library panels
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Add device panel (left side)
        self.device_panel = DevicePanel()
        content_splitter.addWidget(self.device_panel)
        
        # Add library panel (center)
        self.library_panel = LibraryPanel(self.db_manager, self.player)
        content_splitter.addWidget(self.library_panel)
        
        # Set initial splitter sizes (1:3 ratio)
        content_splitter.setSizes([300, 900])
        
        # Add splitter to main layout
        main_layout.addWidget(content_splitter)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Add controls panel at bottom
        self.controls_panel = ControlsPanel(self.player)
        main_layout.addWidget(self.controls_panel)

    def load_library(self):
        """Load music library with progress dialog"""
        music_dir = settings_manager.get('music_directory')
        if not music_dir or not os.path.exists(music_dir):
            return
        
        # Create and show loading dialog
        self.loading_dialog = LoadingDialog(self)
        
        # Connect signals
        self.music_processor.progress_updated.connect(self.loading_dialog.update_progress)
        self.music_processor.processing_complete.connect(self.on_processing_complete)
        
        # Create thread for processing
        self.process_thread = QThread()
        self.music_processor.moveToThread(self.process_thread)
        self.process_thread.started.connect(
            lambda: self.music_processor.process_directory(music_dir)
        )
        
        # Show dialog and start processing
        self.loading_dialog.show()
        self.process_thread.start()

    def on_processing_complete(self, music_files):
        """Handle completion of music processing"""
        self.process_thread.quit()
        self.loading_dialog.close()
        
        # Update library panel with processed files
        self.library_panel.update_library(music_files)

    def show_preferences(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_general_settings(self):
        dialog = SettingsDialog(self)
        dialog.setCurrentIndex(0)
        dialog.exec()

    def show_device_settings(self):
        dialog = SettingsDialog(self)
        dialog.setCurrentIndex(1)
        dialog.exec()

    def show_sync_settings(self):
        dialog = SettingsDialog(self)
        dialog.setCurrentIndex(2)
        dialog.exec()

    def show_advanced_settings(self):
        dialog = SettingsDialog(self)
        dialog.setCurrentIndex(3)
        dialog.exec()

    def show_about_dialog(self):
        # TODO: Implement about dialog
        pass

    def show_help(self):
        # TODO: Implement help window
        pass

    def closeEvent(self, event):
        """Handle application shutdown"""
        try:
            # Stop any playing music
            if self.player:
                self.player.stop()
            
            # Save application state
            self.save_window_state()
            
            # Clean up resources
            if self.player:
                self.player.cleanup()
            
            event.accept()
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")
            event.accept()

    def save_window_state(self):
        """Save window position and size"""
        settings_manager.set('window_geometry', {
            'x': self.x(),
            'y': self.y(),
            'width': self.width(),
            'height': self.height()
        })

    def load_window_state(self):
        """Load window position and size"""
        geometry = settings_manager.get('window_geometry')
        if geometry:
            self.setGeometry(
                geometry.get('x', 100),
                geometry.get('y', 100),
                geometry.get('width', Settings.WINDOW_MIN_WIDTH),
                geometry.get('height', Settings.WINDOW_MIN_HEIGHT)
            )

    def update_title(self, title=None):
        """Update window title with current track if playing"""
        base_title = "Music Sync"
        if title:
            self.setWindowTitle(f"{title} - {base_title}")
        else:
            self.setWindowTitle(base_title)