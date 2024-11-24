# media/beets_library.py
from beets.library import Library, Item, Album
from beets import config as beetsconfig
from beets import logging as beetslogging
from beets.util import normpath
from beets.importer import ImportTask, action
from PyQt6.QtCore import QObject, pyqtSignal
import os
import threading
import datetime

class BeetsLibraryManager(QObject):
    # Signals for GUI updates
    progress_updated = pyqtSignal(int, str)  # progress %, status
    item_imported = pyqtSignal(dict)  # imported item metadata
    import_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, library_path):
        super().__init__()
        self.library_path = library_path
        self.initialize_beets()
        
    def initialize_beets(self):
        """Initialize beets configuration and library"""
        try:
            # Configure beets
            beetsconfig.clear()
            beetsconfig['library'] = normpath(os.path.join(self.library_path, 'musiclibrary.db'))
            beetsconfig['directory'] = normpath(self.library_path)
            beetsconfig['import']['copy'] = False  # Don't copy files
            beetsconfig['import']['move'] = False  # Don't move files
            beetsconfig['import']['write'] = True  # Write metadata to files
            beetsconfig['import']['log'] = 'import.log'
            
            # Initialize library
            self.lib = Library(beetsconfig['library'].as_filename())
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize beets: {str(e)}")
            raise

    def import_directory(self, directory):
        """Import a directory of music files"""
        try:
            total_items = sum(1 for _ in os.scandir(directory) if _.is_file())
            processed = 0

            for root, _, files in os.walk(directory):
                for file in files:
                    try:
                        full_path = os.path.join(root, file)
                        # Create beets item
                        item = self.import_file(full_path)
                        if item:
                            processed += 1
                            progress = int((processed / total_items) * 100)
                            self.progress_updated.emit(
                                progress,
                                f"Processing {processed}/{total_items}: {file}"
                            )
                            # Emit metadata for GUI update
                            self.item_imported.emit(self.item_to_dict(item))
                    
                    except Exception as e:
                        self.error_occurred.emit(f"Error importing {file}: {str(e)}")
                        continue

            self.lib.save()
            self.import_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Import error: {str(e)}")

    def import_file(self, path):
        """Import a single music file using beets"""
        try:
            # Create beets item
            item = Item.from_path(path)
            
            # Add to library
            item.add(self.lib)
            
            # Write changes to file
            item.try_write()
            
            return item
            
        except Exception as e:
            self.error_occurred.emit(f"Error importing file {path}: {str(e)}")
            return None

    def item_to_dict(self, item):
        """Convert beets Item to dictionary for GUI"""
        return {
            'id': item.id,
            'path': item.path,
            'title': item.title,
            'artist': item.artist,
            'album': item.album,
            'albumartist': item.albumartist,
            'genre': item.genre,
            'year': item.year,
            'track': item.track,
            'disc': item.disc,
            'composer': item.composer,
            'duration': item.length,
            'format': item.format,
            'bitrate': item.bitrate,
            'added': item.added,
            'modified': item.mtime,
            'play_count': item.play_count if hasattr(item, 'play_count') else 0
        }

    def query(self, query_string):
        """Query the library using beets query syntax"""
        try:
            items = self.lib.items(query_string)
            return [self.item_to_dict(item) for item in items]
        except Exception as e:
            self.error_occurred.emit(f"Query error: {str(e)}")
            return []

    def update_play_count(self, item_id):
        """Update play count for an item"""
        try:
            item = self.lib.get_item(item_id)
            if item:
                if not hasattr(item, 'play_count'):
                    item.play_count = 0
                item.play_count += 1
                item.try_write()
                self.lib.save()
        except Exception as e:
            self.error_occurred.emit(f"Error updating play count: {str(e)}")

    def get_albums(self):
        """Get all albums in the library"""
        try:
            return [
                {
                    'id': album.id,
                    'album': album.album,
                    'albumartist': album.albumartist,
                    'year': album.year,
                    'genre': album.genre,
                    'tracks': len(album.items())
                }
                for album in self.lib.albums()
            ]
        except Exception as e:
            self.error_occurred.emit(f"Error getting albums: {str(e)}")
            return []