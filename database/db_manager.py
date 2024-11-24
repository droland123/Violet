# database/db_manager.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..error_handler import handle_database_error, DatabaseError

Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_path: str):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    @handle_database_error
    def add_track(self, metadata: Dict[str, Any]) -> Track:
        """Add or update a track in the database"""
        track = self.session.query(Track).filter_by(path=metadata['path']).first()
        
        if track is None:
            track = Track()
        
        # Update track attributes
        for key, value in metadata.items():
            if hasattr(track, key):
                setattr(track, key, value)
        
        self.session.add(track)
        self.session.commit()
        return track

    @handle_database_error
    def get_track(self, track_id: int) -> Optional[Track]:
        """Get track by ID"""
        return self.session.query(Track).get(track_id)

    @handle_database_error
    def get_tracks_by_artist(self, artist: str) -> List[Track]:
        """Get all tracks by artist"""
        return self.session.query(Track).filter_by(artist=artist).all()

    @handle_database_error
    def get_tracks_by_album(self, album: str) -> List[Track]:
        """Get all tracks in album"""
        return self.session.query(Track).filter_by(album=album).all()

    @handle_database_error
    def update_play_count(self, track_id: int):
        """Increment play count for track"""
        track = self.get_track(track_id)
        if track:
            track.play_count += 1
            track.last_played = datetime.now()
            self.session.commit()

    @handle_database_error
    def create_playlist(self, name: str) -> Playlist:
        """Create a new playlist"""
        playlist = Playlist(name=name)
        self.session.add(playlist)
        self.session.commit()
        return playlist

    @handle_database_error
    def add_to_playlist(self, playlist_id: int, track_id: int):
        """Add track to playlist"""
        playlist = self.session.query(Playlist).get(playlist_id)
        track = self.session.query(Track).get(track_id)
        if playlist and track:
            playlist.tracks.append(track)
            self.session.commit()

    def cleanup(self):
        """Clean up database connection"""
        self.session.close()

# Create a global database manager instance
db_manager = None

def init_db(db_path: str):
    """Initialize the database manager"""
    global db_manager
    db_manager = DatabaseManager(db_path)
    return db_manager