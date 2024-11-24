# services/spotify_service.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyService:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-public user-library-modify"
        ))