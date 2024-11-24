# media/player.py
import vlc
import os

class MediaPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_media = None
        self._is_playing = False
        self.current_file = None

    def play(self, file_path=None):
        """Play media file. If no file is provided, resume current file."""
        try:
            if file_path:
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    return False
                
                media = self.instance.media_new(file_path)
                self.player.set_media(media)
                self.current_media = media
                self.current_file = file_path

            result = self.player.play()
            self._is_playing = result == 0  # 0 indicates success
            return self._is_playing
        except Exception as e:
            print(f"Error playing media: {str(e)}")
            self._is_playing = False
            return False

    def pause(self):
        """Pause playback."""
        try:
            self.player.pause()
            self._is_playing = False
        except Exception as e:
            print(f"Error pausing media: {str(e)}")

    def stop(self):
        """Stop playback."""
        try:
            self.player.stop()
            self._is_playing = False
        except Exception as e:
            print(f"Error stopping media: {str(e)}")

    def is_playing(self):
        """Check if media is currently playing."""
        try:
            # Update internal state based on actual player state
            self._is_playing = bool(self.player.is_playing())
            return self._is_playing
        except Exception as e:
            print(f"Error checking play state: {str(e)}")
            return False

    def get_position(self):
        """Get current playback position as a float between 0.0 and 1.0."""
        try:
            if self.current_media:
                return self.player.get_position()
            return 0.0
        except Exception as e:
            print(f"Error getting position: {str(e)}")
            return 0.0

    def set_position(self, position):
        """Set playback position (float between 0.0 and 1.0)."""
        try:
            if self.current_media:
                self.player.set_position(max(0.0, min(1.0, position)))
        except Exception as e:
            print(f"Error setting position: {str(e)}")

    def get_time(self):
        """Get current time in milliseconds."""
        try:
            return self.player.get_time()
        except Exception as e:
            print(f"Error getting time: {str(e)}")
            return 0

    def get_length(self):
        """Get media length in milliseconds."""
        try:
            return self.player.get_length()
        except Exception as e:
            print(f"Error getting length: {str(e)}")
            return 0

    def set_volume(self, volume):
        """Set volume (0-100)."""
        try:
            self.player.audio_set_volume(max(0, min(100, int(volume))))
        except Exception as e:
            print(f"Error setting volume: {str(e)}")

    def get_volume(self):
        """Get current volume (0-100)."""
        try:
            return self.player.audio_get_volume()
        except Exception as e:
            print(f"Error getting volume: {str(e)}")
            return 0

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.player:
                self.stop()
                self.player.release()
            if self.instance:
                self.instance.release()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
