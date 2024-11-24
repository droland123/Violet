# media/file_manager.py
import os
from mutagen import File
from pathlib import Path

class FileManager:
    def __init__(self, supported_formats):
        self.supported_formats = supported_formats
    
    def scan_directory(self, directory):
        music_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    full_path = os.path.join(root, file)
                    metadata = self.get_metadata(full_path)
                    if metadata:
                        music_files.append(metadata)
        return music_files
    
    def get_metadata(self, file_path):
        try:
            audio = File(file_path)
            if audio is None:
                return None
            
            metadata = {
                'path': file_path,
                'title': audio.get('title', [Path(file_path).stem])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'genre': audio.get('genre', ['Unknown'])[0],
                'year': audio.get('date', [0])[0],
                'duration': audio.info.length
            }
            return metadata
        except Exception:
            return None