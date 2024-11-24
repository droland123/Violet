# media/music_processor.py
from PyQt6.QtCore import QObject, pyqtSignal
from mutagen import File
import os

class MusicProcessor(QObject):
    progress_updated = pyqtSignal(int, str)  # value, status
    processing_complete = pyqtSignal(list)  # processed files

    def __init__(self):
        super().__init__()
        self.supported_formats = {'.mp3', '.m4a', '.wav', '.flac', '.aac'}

    def process_directory(self, directory):
        """Process music directory with progress tracking"""
        music_files = []
        total_files = sum(1 for _, _, files in os.walk(directory) 
                         for f in files 
                         if any(f.lower().endswith(fmt) for fmt in self.supported_formats))
        
        processed_count = 0
        
        # Initial scan
        self.progress_updated.emit(0, "Scanning music directory...")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    file_path = os.path.join(root, file)
                    try:
                        # Process file
                        metadata = self.process_file(file_path)
                        if metadata:
                            music_files.append(metadata)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                    
                    # Update progress
                    processed_count += 1
                    progress = int((processed_count / total_files) * 100)
                    self.progress_updated.emit(
                        progress, 
                        f"Processing files... ({processed_count}/{total_files})"
                    )
        
        self.progress_updated.emit(100, "Processing complete")
        self.processing_complete.emit(music_files)
        return music_files

    def process_file(self, file_path):
        """Process a single music file"""
        try:
            audio = File(file_path)
            if audio is None:
                return None
            
            # Extract metadata
            metadata = {
                'path': file_path,
                'title': audio.get('title', [os.path.splitext(os.path.basename(file_path))[0]])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'genre': audio.get('genre', ['Unknown'])[0],
                'year': audio.get('date', ['Unknown'])[0],
                'duration': audio.info.length if hasattr(audio.info, 'length') else 0,
                'rating': audio.get('rating', ['0'])[0],
                'play_count': audio.get('play_count', [0])[0]
            }
            
            return metadata
        except Exception as e:
            print(f"Error processing file metadata: {e}")
            return None