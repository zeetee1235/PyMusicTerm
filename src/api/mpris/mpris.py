import sys
from typing import Literal, Protocol, override

from mpris_server import MetadataObj, Track
from mpris_server.adapters import MprisAdapter, PlayState
from mpris_server.base import MIME_TYPES, URI

from api.ytmusic import SongData


class PyMusicTermPlayer(Protocol):
    position: float
    current_song_index: int
    song_length: float
    playing: bool
    list_of_downloaded_songs: list[SongData]
    dict_of_lyrics: dict[str, str]

    def query(self, query: str, filter: str) -> list: ...
    def play_from_ytb(self, video_id: str) -> None: ...
    def play_from_list(self, id: int) -> None: ...
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


class HAdapter(MprisAdapter):
    def __init__(self) -> None:
        super().__init__()
        self.player: PyMusicTermPlayer | None = None

    def setup(self, player) -> None:
        self.player = player

    @override
    def get_uri_schemes(self) -> list[str]:
        return URI

    @override
    def get_mime_types(self) -> list[str]:
        return MIME_TYPES

    @override
    def can_quit(self) -> bool:
        return True

    @override
    def quit(self) -> sys.NoReturn:
        sys.exit()

    @override
    def get_current_position(self) -> float:
        return self.player.position

    @override
    def next(self) -> None:
        self.player.next()

    @override
    def previous(self) -> None:
        self.player.previous()

    @override
    def pause(self) -> None:
        self.player.pause_song()

    @override
    def resume(self) -> None:
        self.player.resume_song()

    @override
    def stop(self) -> None:
        self.player.stop()

    @override
    def play(self) -> None:
        self.player.playing = True

    @override
    def get_playstate(self) -> PlayState:
        if not self.player.playing:
            return PlayState.PAUSED
        return PlayState.PLAYING

    @override
    def seek(self, time, track_id=None) -> None:
        self.player.seek_to(time / 1000000)

    @override
    def is_repeating(self) -> bool:
        return False

    @override
    def is_playlist(self) -> bool:
        return self.can_go_next() or self.can_go_previous()

    @override
    def set_repeating(self, val: bool) -> None:
        self.player.loop_at_end()

    @override
    def set_loop_status(self, val: str) -> None:
        pass

    @override
    def get_rate(self) -> float:
        return 1.0

    @override
    def set_rate(self, val: float) -> None:
        pass

    @override
    def get_shuffle(self) -> bool:
        return False

    @override
    def set_shuffle(self, val: bool) -> Literal[False]:
        return False

    @override
    def is_mute(self) -> bool:
        return False

    @override
    def can_go_next(self) -> bool:
        return True

    @override
    def can_go_previous(self) -> bool:
        return True

    @override
    def can_play(self) -> bool:
        return True

    @override
    def can_pause(self) -> bool:
        return True

    @override
    def can_seek(self) -> bool:
        return True

    @override
    def can_control(self) -> bool:
        return True

    @override
    def get_current_track(self) -> Track:
        song_data: SongData = self.player.list_of_downloaded_songs[
            self.player.current_song_index
        ]
        title: str = song_data.title
        artist: list[str] = [song_data.get_formatted_artists()]
        album: str = song_data.album
        length: float = self.player.song_length

        return Track(
            title=title,
            artists=artist,
            album=album,
            length=length,
            art_url=f"https://i.ytimg.com/vi/{song_data.videoId}/maxresdefault.jpg",
        )

    @override
    def metadata(self) -> MetadataObj:
        song_data: SongData = self.player.list_of_downloaded_songs[
            self.player.current_song_index
        ]
        title: str = song_data.title
        artist: list[str] = [song_data.get_formatted_artists()]
        album: str = song_data.album
        length: float = self.player.song_length * 1000000

        return MetadataObj(
            album=album,
            title=title,
            artists=artist,
            length=length,
            auto_rating=0,
            art_url=f"https://i.ytimg.com/vi/{song_data.videoId}/maxresdefault.jpg",
            url=f"https://www.youtube.com/watch?v={song_data.videoId}",
        )
