# config/settings.py
class Settings:
    SPOTIFY_CLIENT_ID = "YOUR_CLIENT_ID"
    SPOTIFY_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    SPOTIFY_REDIRECT_URI = "YOUR_REDIRECT_URI"
    
    DATABASE_PATH = "music_player.db"
    DEFAULT_MUSIC_DIR = "~/Music"
    
    SUPPORTED_FORMATS = ['.mp3', '.m4a', '.wav', '.flac']
    
    # GUI Settings
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 800
    UPDATE_INTERVAL = 1000  # ms
