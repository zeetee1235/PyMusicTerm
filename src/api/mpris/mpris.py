from pathlib import Path

from typing import List, Protocol
from mpris_server.adapters import PlayState, MprisAdapter
from mpris_server.base import URI, MIME_TYPES
import sys

class PyMusicTermPlayer(Protocol):
    position: float
    current_song_index: int
    song_length: float
    playing: bool
    list_of_downloaded_songs: list[str]
    dict_of_lyrics: dict[str, str]
    def query(self, query: str, filter: str) -> list: ...
    def play_from_ytb(self, video_id: str) -> None: ...
    def play_from_list(self, id: int) -> None: ...
    def previous(self) -> None: ...
    def next(self) -> None: ...
    def seek_forward(self, time: float = 10) -> None: ...
    def suffle(self) -> None: ...
    def loop_at_end(self) -> bool: ...
    def update(self) -> None: ...
    def map_lyrics_to_song(self) -> dict[str, str]: ...
    def stop(self) -> None: ...
    def pause_song(self) -> None: ...
    def resume_song(self) -> None: ...
    


class HAdapter(MprisAdapter):
    def __init__(self):
        super().__init__()
        self.player: PyMusicTermPlayer | None = None

    def setup(self, player):
        self.player = player

    def get_uri_schemes(self) -> List[str]:
        return URI

    def get_mime_types(self) -> List[str]:
        return MIME_TYPES

    def can_quit(self) -> bool:
        return True

    def quit(self):
        sys.exit()

    def get_current_position(self):
        return self.player.position

    def next(self):
        self.player.next()

    def previous(self):
        self.player.previous()

    def pause(self):
        self.player.pause_song()

    def resume(self):
        self.player.resume_song()

    def stop(self):
        self.player.stop()

    def play(self):
        self.player.playing

    def get_playstate(self) -> PlayState:
        if not self.player.playing:
            return PlayState.PAUSED
        else:
            return PlayState.PLAYING

    def seek(self, time):
        self.player.seek_forward(time)

    def is_repeating(self) -> bool:
        return False

    def is_playlist(self) -> bool:
        return self.can_go_next() or self.can_go_previous()

    def set_repeating(self, val: bool):
        self.player.loop_at_end()

    def set_loop_status(self, val: str):
        pass

    def get_rate(self) -> float:
        return 1.0

    def set_rate(self, val: float):
        pass

    def get_shuffle(self) -> bool:
        return False

    def set_shuffle(self, val: bool):
        return False

    def get_art_url(self, track):
        print("Later")
        return "Later"

    def get_stream_title(self):
        print("Later again")

    def is_mute(self) -> bool:
        return False

    def can_go_next(self) -> bool:
        return True

    def can_go_previous(self) -> bool:
        return True

    def can_play(self) -> bool:
        return True

    def can_pause(self) -> bool:
        return True

    def can_seek(self) -> bool:
        return True

    def can_control(self) -> bool:
        return True

    def get_stream_title(self) -> str:
        return "Test title"

    def metadata(self) -> dict:
        song_data = Path(
            self.player.list_of_downloaded_songs[self.player.current_song_index]
        ).stem.split(" - ")
        title = ", ".join(song_data[:-1])
        artist = song_data[-1]
        metadata = {
            "mpris:trackid": "/track/1",
            "mpris:length": self.player.song_length if not 0 else None,
            "mpris:artUrl": "Example",
            "xesam:url": "https://google.com",
            "xesam:title": title,
            "xesam:artist": [artist],
            "xesam:album": "",
            "xesam:albumArtist": [],
            "xesam:discNumber": 1,
            "xesam:trackNumber": 1,
            "xesam:comment": [],
        }

        return metadata
