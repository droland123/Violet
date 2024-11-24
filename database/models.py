# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# Association table for playlists
playlist_tracks = Table('playlist_tracks', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id')),
    Column('track_id', Integer, ForeignKey('tracks.id'))
)

class Track(Base):
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    year = Column(Integer)
    duration = Column(Float)
    play_count = Column(Integer, default=0)
    last_played = Column(DateTime)
    date_added = Column(DateTime, default=datetime.utcnow)
    fingerprint = Column(String)  # acoustid fingerprint
    loudness = Column(Float)  # LUFS value
    playlists = relationship('Playlist', secondary=playlist_tracks, back_populates='tracks')

class Playlist(Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    tracks = relationship('Track', secondary=playlist_tracks, back_populates='playlists')

def init_db(db_path):
    """Initialize the database"""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# database/__init__.py should be empty or contain:
from .models import Track, Playlist, init_db