from just_playback import Playback


class InvalidFileType(Exception):
    pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MusicPlayer(metaclass=Singleton):
    def __init__(self, default_volume: float = 0.5):
        self.playback = Playback()
        self.playback.set_volume(default_volume)
        self._loop_at_end = False

    def __str__(self) -> str:
        return f"MusicPlayer(volume={self.volume}, busy={self.busy}, ended={self.ended}, position={self.position}, song_length={self.song_length})"

    def unload_song(self) -> None:
        self.playback.stop()

    def load_song(self, path: str) -> None:
        self.playback.load_file(path)

    def play_song(self) -> None:
        self.playback.play()

    def resume_song(self) -> None:
        self.playback.resume()

    def pause_song(self) -> None:
        self.playback.pause()

    def play_pause(self) -> None:
        if self.playback.playing:
            self.pause_song()
        else:
            self.resume_song()

    @property
    def loop_at_end(self) -> bool:
        return self._loop_at_end

    @loop_at_end.setter
    def loop_at_end(self, value: bool) -> None:
        self._loop_at_end = value
        self.playback.loop_at_end(value)

    @property
    def volume(self) -> float:
        return self.playback.volume

    @volume.setter
    def volume(self, volume: float):
        self.playback.set_volume(volume)

    @property
    def playing(self) -> bool:
        return self.playback.playing

    @property
    def position(self) -> float:
        return self.playback.curr_pos

    @position.setter
    def position(self, value: float) -> None:
        self.playback.seek(value)

    @property
    def active(self) -> bool:
        return self.playback.active

    @property
    def song_length(self) -> float:
        return self.playback.duration
