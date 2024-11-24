# media/tag_handler.py
from mutagen import File
from tinytag import TinyTag
import os
import logging
from typing import Dict, Optional
from ..error_handler import log_error

class TagHandler:
    """Centralized media tag handling"""
    
    @staticmethod
    @log_error
    def read_tags(file_path: str) -> Optional[Dict]:
        """
        Read tags from a media file using multiple fallback methods.
        Returns standardized metadata dictionary.
        """
        if not os.path.exists(file_path):
            return None
            
        metadata = {
            'path': file_path,
            'title': os.path.splitext(os.path.basename(file_path))[0],
            'artist': 'Unknown',
            'album': 'Unknown',
            'genre': 'Unknown',
            'year': None,
            'duration': 0,
            'track_number': None,
        }
        
        # Try mutagen first
        try:
            audio = File(file_path, easy=True)
            if audio is not None:
                metadata.update({
                    'title': audio.get('title', [metadata['title']])[0],
                    'artist': audio.get('artist', ['Unknown'])[0],
                    'album': audio.get('album', ['Unknown'])[0],
                    'genre': audio.get('genre', ['Unknown'])[0],
                    'year': audio.get('date', [None])[0],
                    'duration': audio.info.length if hasattr(audio.info, 'length') else 0,
                    'track_number': audio.get('tracknumber', [None])[0]
                })
                return metadata
        except Exception as e:
            logging.debug(f"Mutagen failed for {file_path}: {e}")

        # Fallback to TinyTag
        try:
            tag = TinyTag.get(file_path)
            metadata.update({
                'title': tag.title or metadata['title'],
                'artist': tag.artist or 'Unknown',
                'album': tag.album or 'Unknown',
                'genre': tag.genre or 'Unknown',
                'year': tag.year,
                'duration': tag.duration or 0,
                'track_number': tag.track or None
            })
            return metadata
        except Exception as e:
            logging.debug(f"TinyTag failed for {file_path}: {e}")
            
        return metadata

    @staticmethod
    @log_error
    def update_tags(file_path: str, metadata: Dict) -> bool:
        """Update file tags with new metadata"""
        try:
            audio = File(file_path, easy=True)
            if audio is None:
                return False
                
            if hasattr(audio, 'tags'):
                for key, value in metadata.items():
                    if value is not None:
                        audio[key] = value
                audio.save()
                return True
        except Exception as e:
            logging.error(f"Failed to update tags for {file_path}: {e}")
            return False