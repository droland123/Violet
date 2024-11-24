# gui/dialogs/settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, 
    QVBoxLayout, 
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QFormLayout,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
import os
from typing import Optional
from media.directory_analyzer import DirectoryAnalyzer
from config.settings_manager import settings_manager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(600, 400)
        self.directory_analyzer = DirectoryAnalyzer()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.general_tab = GeneralSettingsTab(self.directory_analyzer)
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(DeviceSettingsTab(), "Devices")
        self.tab_widget.addTab(SyncSettingsTab(), "Sync")
        self.tab_widget.addTab(AdvancedSettingsTab(), "Advanced")
        
        main_layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
        # Connect buttons
        ok_button.clicked.connect(self.accept_and_save)
        apply_button.clicked.connect(self.apply_settings)
        cancel_button.clicked.connect(self.reject)

    def accept_and_save(self):
        self.apply_settings()
        self.accept()

    def apply_settings(self):
        # Save settings from all tabs
        self.general_tab.save_settings()
        # Add saving for other tabs as needed
        self.show_save_confirmation()

    def show_save_confirmation(self):
        QMessageBox.information(self, "Settings Saved", 
                              "Settings have been successfully saved.")

    def setCurrentIndex(self, index: int):
        self.tab_widget.setCurrentIndex(index)


class GeneralSettingsTab(QWidget):
    def __init__(self, directory_analyzer):
        super().__init__()
        self.directory_analyzer = directory_analyzer
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Music folder section
        folder_group = QWidget()
        folder_layout = QVBoxLayout(folder_group)
        
        # Music folder location with label
        self.folder_label = QLabel("No music folder selected")
        self.folder_label.setWordWrap(True)
        folder_layout.addWidget(self.folder_label)
        
        folder_input_layout = QHBoxLayout()
        self.music_folder = QLineEdit()
        self.music_folder.setPlaceholderText("Select your music folder...")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_music_folder)
        folder_input_layout.addWidget(self.music_folder)
        folder_input_layout.addWidget(browse_button)
        folder_layout.addLayout(folder_input_layout)
        
        # Analysis progress
        self.analysis_progress = QProgressBar()
        self.analysis_progress.hide()
        folder_layout.addWidget(self.analysis_progress)
        
        layout.addRow("Music Folder:", folder_group)
        
        # Library columns section
        columns_group = QWidget()
        columns_layout = QVBoxLayout(columns_group)
        
        columns_label = QLabel("Show additional columns:")
        columns_layout.addWidget(columns_label)
        
        self.column_checkboxes = {}
        for column in ["Genre", "Year", "Rating", "Play Count"]:
            checkbox = QCheckBox(column)
            checkbox.setChecked(column in settings_manager.get('library_columns', []))
            self.column_checkboxes[column] = checkbox
            columns_layout.addWidget(checkbox)
        
        layout.addRow("Library Columns:", columns_group)
        
        # View options
        view_group = QWidget()
        view_layout = QVBoxLayout(view_group)
        
        self.default_view = QComboBox()
        self.update_view_options()  # Initialize with default options
        view_layout.addWidget(self.default_view)
        
        # Detected structure label
        self.structure_label = QLabel("Select a music folder to analyze its structure")
        self.structure_label.setWordWrap(True)
        view_layout.addWidget(self.structure_label)
        
        layout.addRow("Library View:", view_group)
        
        # Auto-organization options
        self.auto_organize = QCheckBox("Automatically organize files based on detected structure")
        self.auto_organize.setEnabled(False)  # Disabled until folder is selected
        layout.addRow("", self.auto_organize)
        
        # Watch folder option
        self.watch_folder = QCheckBox("Watch music folder for changes")
        self.watch_folder.setEnabled(False)  # Disabled until folder is selected
        layout.addRow("", self.watch_folder)

    def load_settings(self):
        """Load saved settings"""
        # Load music directory
        music_dir = settings_manager.get('music_directory')
        if music_dir and os.path.exists(music_dir):
            self.music_folder.setText(music_dir)
            self.folder_label.setText(music_dir)
            self.analyze_folder(music_dir)
        
        # Load other settings
        self.auto_organize.setChecked(settings_manager.get('auto_organize', False))
        self.watch_folder.setChecked(settings_manager.get('watch_folder', False))
        
        # Set view hierarchy
        current_hierarchy = settings_manager.get('view_hierarchy')
        if current_hierarchy:
            index = self.default_view.findText(current_hierarchy)
            if index >= 0:
                self.default_view.setCurrentIndex(index)

        # Load column settings
        for column, checkbox in self.column_checkboxes.items():
            checkbox.setChecked(column in settings_manager.get('library_columns', []))

    def save_settings(self):
        """Save current settings"""
        settings_manager.set('music_directory', self.music_folder.text())
        settings_manager.set('auto_organize', self.auto_organize.isChecked())
        settings_manager.set('watch_folder', self.watch_folder.isChecked())
        settings_manager.set('view_hierarchy', self.default_view.currentText())
        
        # Save column settings
        current_columns = []
        for column, checkbox in self.column_checkboxes.items():
            if checkbox.isChecked():
                current_columns.append(column)
        settings_manager.set('library_columns', current_columns)

    def browse_music_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Music Folder",
            self.music_folder.text() or os.path.expanduser("~/Music"),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.music_folder.setText(folder)
            self.folder_label.setText(folder)
            self.analyze_folder(folder)

    def analyze_folder(self, folder: str):
        """Analyze the selected music folder if it exists"""
        if not folder or not os.path.exists(folder):
            self.structure_label.setText("Please select a valid music folder")
            self.auto_organize.setEnabled(False)
            self.watch_folder.setEnabled(False)
            self.update_view_options()
            return

        # Show progress bar
        self.analysis_progress.setRange(0, 0)  # Indeterminate progress
        self.analysis_progress.show()
        
        try:
            # Analyze directory structure
            hierarchy = self.directory_analyzer.analyze_directory(folder)
            self.structure_label.setText(f"Detected Structure: {hierarchy}")
            self.auto_organize.setEnabled(True)
            self.watch_folder.setEnabled(True)
            
            # Update view options
            self.update_view_options(folder)
            
            # Update library if possible
            if self.parent() and hasattr(self.parent(), 'parent'):
                main_window = self.parent().parent()
                if hasattr(main_window, 'library_panel'):
                    main_window.library_panel.load_music_directory(folder)
            
        except Exception as e:
            self.structure_label.setText(f"Error analyzing folder: {str(e)}")
            self.auto_organize.setEnabled(False)
            self.watch_folder.setEnabled(False)
        finally:
            self.analysis_progress.hide()

    def update_view_options(self, folder: Optional[str] = None):
        """Update view options based on folder analysis or use defaults"""
        self.default_view.clear()
        
        if folder and os.path.exists(folder):
            try:
                options = self.directory_analyzer.get_hierarchy_options(folder)
                self.default_view.addItems(options)
            except Exception:
                self._add_default_options()
        else:
            self._add_default_options()

    def _add_default_options(self):
        """Add default view options when no folder is selected or analysis fails"""
        default_options = [
            "Artist > Album > Song",
            "Album > Song",
            "Song"
        ]
        self.default_view.addItems(default_options)


class DeviceSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Device detection
        self.auto_detect = QCheckBox("Automatically detect devices")
        layout.addRow("", self.auto_detect)
        
        # Device types
        self.device_support = QCheckBox("Support iPod Classic")
        layout.addRow("Supported Devices:", self.device_support)
        
        # Device sync behavior
        self.auto_eject = QCheckBox("Auto-eject when sync complete")
        layout.addRow("", self.auto_eject)
        
        # Device warnings
        self.show_warnings = QCheckBox("Show warnings before device operations")
        layout.addRow("", self.show_warnings)


class SyncSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Sync behavior
        self.sync_playlists = QCheckBox("Sync Playlists")
        layout.addRow("", self.sync_playlists)
        
        self.sync_ratings = QCheckBox("Sync Ratings")
        layout.addRow("", self.sync_ratings)
        
        self.sync_play_counts = QCheckBox("Sync Play Counts")
        layout.addRow("", self.sync_play_counts)
        
        # Conflict resolution
        self.conflict_resolution = QComboBox()
        self.conflict_resolution.addItems([
            "Keep Device Version",
            "Keep Library Version",
            "Ask Each Time"
        ])
        layout.addRow("On Conflict:", self.conflict_resolution)
        
        # Space management
        self.manage_space = QCheckBox("Automatically manage device space")
        layout.addRow("", self.manage_space)


class AdvancedSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Debug logging
        self.enable_logging = QCheckBox("Enable debug logging")
        layout.addRow("", self.enable_logging)
        
        # Database management
        self.vacuum_db = QPushButton("Optimize Database")
        layout.addRow("Database:", self.vacuum_db)
        
        # Cache settings
        self.cache_size = QSpinBox()
        self.cache_size.setRange(100, 10000)
        self.cache_size.setSuffix(" MB")
        layout.addRow("Cache Size:", self.cache_size)
        
        # Clear cache button
        self.clear_cache = QPushButton("Clear Cache")
        layout.addRow("", self.clear_cache)