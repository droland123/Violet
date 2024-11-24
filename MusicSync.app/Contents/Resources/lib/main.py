#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QThread
from config.settings import Settings
from config.settings_manager import settings_manager
from database.models import init_db, Track
from gui.device_panel import DevicePanel
from gui.library_panel import LibraryPanel
from gui.controls_panel import ControlsPanel
from gui.dialogs.settings_dialog import SettingsDialog
from gui.dialogs.loading_dialog import LoadingDialog
from gui.dialogs.duplicates_dialog import DuplicatesDialog
from media.player import MediaPlayer
from media.track_processor import TrackProcessor
from media.music_watcher import MusicDirectoryWatcher
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('MusicSync')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.debug("Initializing MainWindow")
        self.setup_components()
        self.setup_ui()
        self.setup_menus()
        self.load_window_state()
        self.initial_library_load()

    def setup_components(self):
        """Initialize all major components"""
        try:
            # Initialize database
            self.db_session = init_db(settings_manager.get('database_path', 'music_library.db'))
            logger.debug("Database initialized")

            # Initialize track processor
            self.track_processor = TrackProcessor(self.db_session)
            logger.debug("Track processor initialized")

            # Initialize media player
            self.player = MediaPlayer()
            logger.debug("Media player initialized")

            # Setup directory watcher
            music_dir = settings_manager.get('music_directory')
            if music_dir and os.path.exists(music_dir):
                self.watcher = MusicDirectoryWatcher(music_dir, self.on_new_music_file)
                self.watcher.start()
                logger.debug(f"Directory watcher started for {music_dir}")
            else:
                logger.warning("No valid music directory configured")

        except Exception as e:
            logger.error(f"Error setting up components: {e}", exc_info=True)
            raise

    def setup_ui(self):
        """Setup the user interface"""
        try:
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
            self.library_panel = LibraryPanel(self.db_session, self.player, self.track_processor)
            content_splitter.addWidget(self.library_panel)
            
            # Set initial splitter sizes (1:3 ratio)
            content_splitter.setSizes([300, 900])
            
            # Add splitter to main layout
            main_layout.addWidget(content_splitter)
            
            # Add controls panel at bottom
            self.controls_panel = ControlsPanel(self.player)
            main_layout.addWidget(self.controls_panel)

            logger.debug("UI setup completed")

        except Exception as e:
            logger.error(f"Error setting up UI: {e}", exc_info=True)
            raise

    def initial_library_load(self):
        """Load the music library on startup"""
        try:
            music_dir = settings_manager.get('music_directory')
            if music_dir and os.path.exists(music_dir):
                loading_dialog = LoadingDialog(self)
                loading_dialog.show()

                def progress_callback(value, status):
                    loading_dialog.update_progress(value, status)

                # Start library scanning in a thread
                scan_thread = QThread()
                self.track_processor.moveToThread(scan_thread)
                self.track_processor.progress_updated.connect(progress_callback)
                self.track_processor.processing_complete.connect(loading_dialog.close)
                scan_thread.started.connect(
                    lambda: self.track_processor.scan_directory(music_dir)
                )
                scan_thread.start()

                logger.debug("Started initial library scan")

        except Exception as e:
            logger.error(f"Error during initial library load: {e}", exc_info=True)

    def on_new_music_file(self, file_path):
        """Handle newly added music files"""
        try:
            logger.debug(f"Processing new file: {file_path}")
            track = self.track_processor.process_file(file_path)
            if track:
                self.db_session.add(track)
                self.db_session.commit()
                self.library_panel.add_track(track)
                logger.debug(f"Successfully processed: {file_path}")
            else:
                logger.warning(f"Failed to process: {file_path}")

        except Exception as e:
            logger.error(f"Error processing new file {file_path}: {e}", exc_info=True)

    def check_duplicates(self):
        """Check for duplicates in the library"""
        try:
            logger.debug("Starting duplicate analysis")
            duplicate_groups = self.track_processor.duplicate_detector.analyze_duplicates()
            if duplicate_groups:
                logger.debug(f"Found {len(duplicate_groups)} duplicate groups")
                self.show_duplicates_dialog(duplicate_groups)
            else:
                logger.debug("No duplicates found")

        except Exception as e:
            logger.error(f"Error checking duplicates: {e}", exc_info=True)

    def show_duplicates_dialog(self, duplicate_groups):
        """Show dialog with duplicate files"""
        try:
            dialog = DuplicatesDialog(duplicate_groups, self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing duplicates dialog: {e}", exc_info=True)

    def show_settings(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self)
            if dialog.exec() == SettingsDialog.Accepted:
                self.apply_settings_changes()
        except Exception as e:
            logger.error(f"Error showing settings: {e}", exc_info=True)

    def apply_settings_changes(self):
        """Apply changes made in settings"""
        try:
            # Restart directory watcher if music directory changed
            new_music_dir = settings_manager.get('music_directory')
            if hasattr(self, 'watcher') and new_music_dir != self.watcher.directory:
                self.watcher.stop()
                self.watcher = MusicDirectoryWatcher(new_music_dir, self.on_new_music_file)
                self.watcher.start()
                logger.debug(f"Directory watcher restarted for {new_music_dir}")

        except Exception as e:
            logger.error(f"Error applying settings changes: {e}", exc_info=True)

    def save_window_state(self):
        """Save window position and size"""
        try:
            settings_manager.set('window_geometry', {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            })
            logger.debug("Window state saved")
        except Exception as e:
            logger.error(f"Error saving window state: {e}", exc_info=True)

    def load_window_state(self):
        """Load window position and size"""
        try:
            geometry = settings_manager.get('window_geometry')
            if geometry:
                self.setGeometry(
                    geometry.get('x', 100),
                    geometry.get('y', 100),
                    geometry.get('width', Settings.WINDOW_MIN_WIDTH),
                    geometry.get('height', Settings.WINDOW_MIN_HEIGHT)
                )
                logger.debug("Window state restored")
        except Exception as e:
            logger.error(f"Error loading window state: {e}", exc_info=True)

    def closeEvent(self, event):
        """Handle application shutdown"""
        try:
            logger.debug("Starting application shutdown")
            
            # Stop directory watcher
            if hasattr(self, 'watcher'):
                self.watcher.stop()
                logger.debug("Directory watcher stopped")
            
            # Stop playback
            if hasattr(self, 'player'):
                self.player.stop()
                logger.debug("Playback stopped")
            
            # Save window state
            self.save_window_state()
            
            # Close database session
            if hasattr(self, 'db_session'):
                self.db_session.close()
                logger.debug("Database session closed")
            
            event.accept()
            logger.debug("Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
            event.accept()

def main():
    try:
        # Initialize application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("Music Sync")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("MusicSync")
        app.setOrganizationDomain("musicsync.app")
        
        # Check dependencies
        from dependency_manager import DependencyManager
        dm = DependencyManager()
        dm.check_dependencies()
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()