from dataclasses import dataclass
from typing import Protocol

from PIL import ImageFile

from api.music_player import MusicPlayer


@dataclass
class SongData:
    title: str
    artist: list[str]
    duration: str
    video_id: str
    thumbnail: ImageFile
    album: str
    path: None | str = None

    def get_formatted_artists(self) -> str:
        """Get the formatted artists of the song."""
        return ", ".join(list(self.artist))


class PyMusicTermPlayer(Protocol):
    position: float
    current_song_index: int
    current_song: SongData | None = None
    song_length: float
    playing: bool
    list_of_downloaded_songs: list[SongData]
    dict_of_lyrics: dict[str, str]
    music_player = MusicPlayer(1)

    def query(self, query: str, filter: str) -> list: ...  # noqa: A002
    def play_from_ytb(self, video_id: str) -> None: ...
    def play_from_list(self, id: int) -> None: ...  # noqa: A002
    def previous(self) -> None: ...
    def next(self) -> None: ...
    def seek_to(self, time: float) -> None: ...
    def seek(self, time: float = 10) -> None: ...
    def suffle(self) -> None: ...
    def loop_at_end(self) -> bool: ...
    def update(self) -> None: ...
    def stop(self) -> None: ...
    def pause_song(self) -> None: ...
    def resume_song(self) -> None: ...
