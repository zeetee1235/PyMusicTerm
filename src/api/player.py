from just_playback import Playback


class InvalidFileType(Exception):
    pass


class MusicPlayer:
    def __init__(self, default_volume: float = 0.5):
        self.player = Playback()
        self.player.set_volume(default_volume)
        self._loop_at_end = False

    def __str__(self) -> str:
        return f"MusicPlayer(volume={self.volume}, busy={self.busy}, ended={self.ended}, position={self.position}, song_length={self.song_length})"

    def unload_song(self) -> None:
        self.player.stop()

    def load_song(self, path: str) -> None:
        self.player.load_file(path)

    def play_song(self) -> None:
        self.player.play()

    def resume_song(self) -> None:
        self.player.resume()

    def pause_song(self) -> None:
        self.player.pause()

    @property
    def loop_at_end(self) -> bool:
        return self._loop_at_end

    @loop_at_end.setter
    def loop_at_end(self, value: bool) -> None:
        self._loop_at_end = value
        self.player.loop_at_end(value)

    @property
    def volume(self) -> float:
        return self.player.volume

    @volume.setter
    def volume(self, volume: float):
        self.player.set_volume(volume)

    @property
    def playing(self) -> bool:
        return self.player.playing

    @property
    def position(self) -> float:
        return self.player.curr_pos

    @position.setter
    def position(self, value: float) -> None:
        self.player.seek(value)

    @property
    def active(self) -> bool:
        return self.player.active

    @property
    def song_length(self) -> float:
        return self.player.duration
