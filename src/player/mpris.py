from pathlib import Path
from mpris_server import EventAdapter

from typing import List
from mpris_server.adapters import Metadata, PlayState, MprisAdapter
from mpris_server.base import URI, MIME_TYPES, BEGINNING, DEFAULT_RATE, DbusObj
from mpris_server.server import Server
import sys
from player.player import PyMusicTermPlayer

class HAdapter(MprisAdapter):
    def __init__(self):
        super().__init__()
        self.player = None
    
    def setup(self, player: PyMusicTermPlayer):
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
        print('Later')
        return 'Later'

    def get_stream_title(self):
        print('Later again')

    def is_mute(self) -> bool:
        return False

    def can_go_next(self) -> bool:
        return True

    def can_go_previous(self) -> bool:
        return  True

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
        song_data = Path(self.player.list_of_downloaded_songs[self.player.current_song_index]).stem.split(" - ")
        title = song_data[0]
        artist = song_data[1]
        metadata = {
        "mpris:trackid": "/track/1",
        "mpris:length": self.player.song_length,
        "mpris:artUrl": "Example",
        "xesam:url": "https://google.com",
        "xesam:title": title,
        "xesam:artist": song_data,
        "xesam:album": "",
        "xesam:albumArtist": [],
        "xesam:discNumber": 1,
        "xesam:trackNumber": 1,
        "xesam:comment": [],
        }

        return metadata
        


