# media/duplicate_detector.py
from typing import List, Dict, Tuple
import acoustid
from sqlalchemy import and_
from database.models import Track
import os
from difflib import SequenceMatcher

class DuplicateDetector:
    def __init__(self, db_session):
        self.db_session = db_session
        self.SIMILARITY_THRESHOLD = 0.85

    def find_duplicates(self, file_path: str) -> List[Dict]:
        """Find duplicates of a given file in the library"""
        try:
            # Get fingerprint of new file
            duration, fingerprint = acoustid.fingerprint_file(file_path)
            
            # Query database for potential matches
            potential_matches = []
            
            # First check by fingerprint
            fingerprint_matches = self.db_session.query(Track).filter(
                Track.fingerprint == fingerprint,
                Track.path != file_path  # Exclude self
            ).all()
            
            if fingerprint_matches:
                for match in fingerprint_matches:
                    potential_matches.append({
                        'path': match.path,
                        'match_type': 'fingerprint',
                        'confidence': 1.0,
                        'track': match
                    })
            
            # If no exact fingerprint match, check by metadata
            filename = os.path.basename(file_path)
            basename, _ = os.path.splitext(filename)
            
            # Get all tracks
            all_tracks = self.db_session.query(Track).filter(
                Track.path != file_path
            ).all()
            
            for track in all_tracks:
                other_filename = os.path.basename(track.path)
                other_basename, _ = os.path.splitext(other_filename)
                
                # Calculate filename similarity
                filename_similarity = SequenceMatcher(
                    None, 
                    basename.lower(), 
                    other_basename.lower()
                ).ratio()
                
                if filename_similarity > self.SIMILARITY_THRESHOLD:
                    potential_matches.append({
                        'path': track.path,
                        'match_type': 'filename',
                        'confidence': filename_similarity,
                        'track': track
                    })
            
            return sorted(potential_matches, key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return []

    def analyze_duplicates(self) -> List[List[Dict]]:
        """Find all duplicate groups in the library"""
        duplicate_groups = []
        processed_paths = set()
        
        try:
            # Get all tracks
            tracks = self.db_session.query(Track).all()
            
            for track in tracks:
                if track.path in processed_paths:
                    continue
                
                duplicates = self.find_duplicates(track.path)
                if duplicates:
                    group = [{
                        'path': track.path,
                        'match_type': 'original',
                        'confidence': 1.0,
                        'track': track
                    }] + duplicates
                    
                    # Add all paths in this group to processed
                    processed_paths.update(d['path'] for d in group)
                    
                    duplicate_groups.append(group)
            
            return duplicate_groups
            
        except Exception as e:
            print(f"Error analyzing duplicates: {e}")
            return []

    @staticmethod
    def compare_audio_properties(track1: Track, track2: Track) -> Dict:
        """Compare audio properties of two tracks"""
        return {
            'duration_diff': abs(track1.duration - track2.duration),
            'loudness_diff': abs(track1.loudness - track2.loudness) if (track1.loudness and track2.loudness) else None
        }
