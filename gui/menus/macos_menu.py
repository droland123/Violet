# gui/menus/macos_menu.py
from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
import sys

class MacOSMenuBar:
    def __init__(self, main_window):
        self.window = main_window
        self.menubar = main_window.menuBar()
        self.setup_menus()

    def setup_menus(self):
        # Application Menu (automatic on macOS)
        if sys.platform == 'darwin':
            about_action = QAction('About Music Sync', self.window)
            about_action.setMenuRole(QAction.MenuRole.AboutRole)
            
            preferences_action = QAction('Preferences...', self.window)
            preferences_action.setShortcut(QKeySequence(','))
            preferences_action.setMenuRole(QAction.MenuRole.PreferencesRole)
            preferences_action.triggered.connect(self.window.show_preferences)
            
            quit_action = QAction('Quit Music Sync', self.window)
            quit_action.setShortcut(QKeySequence.StandardKey.Quit)
            quit_action.setMenuRole(QAction.MenuRole.QuitRole)

        # File Menu
        file_menu = self.menubar.addMenu('File')
        
        new_playlist = QAction('New Playlist...', self.window)
        new_playlist.setShortcut(QKeySequence.StandardKey.New)
        file_menu.addAction(new_playlist)
        
        open_file = QAction('Open File...', self.window)
        open_file.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(open_file)

        # Edit Menu (Standard macOS position)
        edit_menu = self.menubar.addMenu('Edit')
        
        # Add standard Edit menu items
        undo = QAction('Undo', self.window)
        undo.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo)
        
        redo = QAction('Redo', self.window)
        redo.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo)
        
        edit_menu.addSeparator()
        
        cut = QAction('Cut', self.window)
        cut.setShortcut(QKeySequence.StandardKey.Cut)
        edit_menu.addAction(cut)
        
        copy = QAction('Copy', self.window)
        copy.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy)
        
        paste = QAction('Paste', self.window)
        paste.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste)
        
        edit_menu.addSeparator()
        
        select_all = QAction('Select All', self.window)
        select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        edit_menu.addAction(select_all)

        # Settings Menu (between Edit and View)
        settings_menu = self.menubar.addMenu('Settings')
        
        general_settings = QAction('General...', self.window)
        general_settings.triggered.connect(self.window.show_general_settings)
        settings_menu.addAction(general_settings)
        
        devices_settings = QAction('Devices...', self.window)
        devices_settings.triggered.connect(self.window.show_device_settings)
        settings_menu.addAction(devices_settings)
        
        sync_settings = QAction('Sync Settings...', self.window)
        sync_settings.triggered.connect(self.window.show_sync_settings)
        settings_menu.addAction(sync_settings)
        
        settings_menu.addSeparator()
        
        advanced_settings = QAction('Advanced...', self.window)
        advanced_settings.triggered.connect(self.window.show_advanced_settings)
        settings_menu.addAction(advanced_settings)

        # View Menu
        view_menu = self.menubar.addMenu('View')
        
        show_sidebar = QAction('Show Sidebar', self.window)
        show_sidebar.setCheckable(True)
        show_sidebar.setChecked(True)
        show_sidebar.setShortcut(QKeySequence('Cmd+B'))
        view_menu.addAction(show_sidebar)
        
        view_menu.addSeparator()
        
        hierarchy_menu = QMenu('Library Hierarchy', self.window)
        view_menu.addMenu(hierarchy_menu)
        
        hierarchies = [
            "Genre > Artist > Year > Album > Song",
            "Artist > Year > Album > Song",
            "Artist > Album > Song",
            "Album > Song",
            "Song"
        ]
        
        hierarchy_actions = []
        for hierarchy in hierarchies:
            action = QAction(hierarchy, self.window)
            action.setCheckable(True)
            hierarchy_actions.append(action)
            hierarchy_menu.addAction(action)
            action.triggered.connect(
                lambda checked, h=hierarchy: self.window.library_panel.set_view_hierarchy(h)
            )
        
        hierarchy_actions[0].setChecked(True)

        # Device Menu
        device_menu = self.menubar.addMenu('Device')
        
        sync_device = QAction('Sync Device', self.window)
        sync_device.setEnabled(False)
        device_menu.addAction(sync_device)
        
        eject_device = QAction('Eject Device', self.window)
        eject_device.setEnabled(False)
        device_menu.addAction(eject_device)

        # Window Menu (standard macOS menu)
        if sys.platform == 'darwin':
            window_menu = self.menubar.addMenu('Window')
            
            minimize = QAction('Minimize', self.window)
            minimize.setShortcut(QKeySequence('Cmd+M'))
            window_menu.addAction(minimize)
            
            zoom = QAction('Zoom', self.window)
            window_menu.addAction(zoom)

        # Help Menu
        help_menu = self.menubar.addMenu('Help')
        
        documentation = QAction('Music Sync Help', self.window)
        documentation.setShortcut(QKeySequence.StandardKey.HelpContents)
        documentation.triggered.connect(self.window.show_help)
        help_menu.addAction(documentation)