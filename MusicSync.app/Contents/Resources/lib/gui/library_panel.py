# gui/library_panel.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QFrame, QLabel, QMenu, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QAction
import os
import sys
from mutagen import File
from config.settings_manager import settings_manager
from media.directory_analyzer import DirectoryAnalyzer

class LibraryPanel(QWidget):
    def __init__(self, db_manager, player):
        super().__init__()
        self.db_manager = db_manager
        self.player = player
        self.directory_analyzer = DirectoryAnalyzer()
        self.current_sort_column = 0
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.file_paths = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add header
        header = QLabel("Library")
        header.setStyleSheet("QLabel { padding: 10px; font-weight: bold; }")
        layout.addWidget(header)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Add tree widget
        self.tree = QTreeWidget()
        # Default columns
        default_columns = ["Artist", "Album", "Title", "Duration"]
        # Optional columns from settings
        optional_columns = settings_manager.get('library_columns', [])
        all_columns = default_columns + [col for col in optional_columns if col not in default_columns]
        
        self.tree.setHeaderLabels(all_columns)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.header().sectionClicked.connect(self.header_clicked)
        self.tree.itemDoubleClicked.connect(self.play_item)
        layout.addWidget(self.tree)

    def update_library(self, music_files):
        """Update library with processed music files"""
        self.tree.clear()
        self.file_paths.clear()
        
        for metadata in music_files:
            self.add_file_to_tree(metadata)
            
        # Sort by default column
        self.tree.sortItems(0, Qt.SortOrder.AscendingOrder)

    def play_item(self, item, column):
        """Play the selected song"""
        file_path = self.file_paths.get(self._get_item_key(item))
        if file_path and os.path.exists(file_path):
            self.player.play(file_path)
            # Update window title with current song
            if self.window():
                title = item.text(2)  # Title column
                artist = item.text(0)  # Artist column
                self.window().update_title(f"{artist} - {title}")

    def show_context_menu(self, position):
        """Show context menu for tree item"""
        item = self.tree.itemAt(position)
        if item:
            file_path = self.file_paths.get(self._get_item_key(item))
            if file_path and os.path.exists(file_path):
                menu = QMenu(self)
                
                # Show in folder action
                show_in_folder = QAction("Show in Folder", self)
                show_in_folder.triggered.connect(lambda: self.show_in_folder(file_path))
                menu.addAction(show_in_folder)
                
                # Show file path action
                show_path = QAction("Copy File Path", self)
                show_path.triggered.connect(lambda: self.copy_file_path(file_path))
                menu.addAction(show_path)
                
                menu.exec(QCursor.pos())

    def _get_item_key(self, item):
        """Generate a unique key for an item based on its data"""
        return tuple(item.text(i) for i in range(item.treeWidget().columnCount()))

    def show_in_folder(self, file_path):
        """Show the file in its folder"""
        try:
            import subprocess
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", "/select,", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
        except Exception as e:
            print(f"Error showing file: {e}")

    def copy_file_path(self, file_path):
        """Copy file path to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)

    def add_file_to_tree(self, metadata):
        """Add a file to the tree using its metadata"""
        try:
            item = QTreeWidgetItem(self.tree)
            self.file_paths[self._get_item_key(item)] = metadata['path']
            
            # Set item data in correct order
            columns = [self.tree.headerItem().text(i) for i in range(self.tree.columnCount())]
            for i, column in enumerate(columns):
                if column == "Artist":
                    item.setText(i, metadata['artist'])
                elif column == "Album":
                    item.setText(i, metadata['album'])
                elif column == "Title":
                    item.setText(i, metadata['title'])
                elif column == "Duration":
                    duration = int(metadata['duration'])
                    item.setText(i, f"{duration//60}:{str(duration%60).zfill(2)}")
                elif column == "Genre":
                    item.setText(i, metadata['genre'])
                elif column == "Year":
                    item.setText(i, str(metadata['year']))
                elif column == "Rating":
                    item.setText(i, str(metadata['rating']))
                elif column == "Play Count":
                    item.setText(i, str(metadata['play_count']))
                
        except Exception as e:
            print(f"Error adding file to tree: {e}")

    def header_clicked(self, logical_index):
        """Handle column header clicks for sorting"""
        if self.current_sort_column == logical_index:
            # Toggle sort order if clicking the same column
            self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            # New column, start with ascending
            self.sort_order = Qt.SortOrder.AscendingOrder
            self.current_sort_column = logical_index
            
        self.tree.sortItems(logical_index, self.sort_order)

    def refresh_view(self):
        """Refresh the current view"""
        music_dir = settings_manager.get('music_directory')
        if music_dir and os.path.exists(music_dir):
            if hasattr(self.window(), 'load_library'):
                self.window().load_library()