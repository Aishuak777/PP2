import os
import pygame


class MusicPlayer:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_paused_or_stopped = True
        self.track_length = 0

    def load_playlist(self):
        supported_formats = (".mp3", ".wav")
        tracks = []

        if not os.path.exists(self.music_folder):
            return tracks

        for file_name in os.listdir(self.music_folder):
            if file_name.lower().endswith(supported_formats):
                tracks.append(os.path.join(self.music_folder, file_name))

        tracks.sort()
        return tracks

    def has_tracks(self):
        return len(self.playlist) > 0

    def get_current_track_path(self):
        if not self.has_tracks():
            return None
        return self.playlist[self.current_index]

    def get_current_track_name(self):
        path = self.get_current_track_path()
        if path is None:
            return "No tracks found"
        return os.path.basename(path)

    def update_track_length(self):
        path = self.get_current_track_path()
        if path is None:
            self.track_length = 0
            return

        try:
            sound = pygame.mixer.Sound(path)
            self.track_length = sound.get_length()
        except Exception:
            self.track_length = 0

    def play(self):
        if not self.has_tracks():
            return

        path = self.get_current_track_path()

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.is_paused_or_stopped = False
            self.update_track_length()
        except Exception as e:
            print(f"Error playing track: {e}")

    def stop(self):
        pygame.mixer.music.stop()
        self.is_paused_or_stopped = True

    def next_track(self):
        if not self.has_tracks():
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        if not self.has_tracks():
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_progress(self):
        if self.is_paused_or_stopped or self.track_length <= 0:
            return 0

        pos_ms = pygame.mixer.music.get_pos()

        if pos_ms < 0:
            return 0

        pos_sec = pos_ms / 1000
        progress = min(pos_sec / self.track_length, 1.0)
        return progress

    def get_time_text(self):
        if self.track_length <= 0 or self.is_paused_or_stopped:
            return "00:00 / 00:00"

        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            current_sec = 0
        else:
            current_sec = int(pos_ms / 1000)

        total_sec = int(self.track_length)

        current_min = current_sec // 60
        current_remain = current_sec % 60

        total_min = total_sec // 60
        total_remain = total_sec % 60

        return f"{current_min:02}:{current_remain:02} / {total_min:02}:{total_remain:02}"