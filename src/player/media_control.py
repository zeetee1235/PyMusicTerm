import sys
from typing import Protocol


if sys.platform == "win32":
    pass
else:
    from mpris_server import EventAdapter
    from mpris_server import EventAdapter, Server
    from api.mpris.mpris import HAdapter


class MediaControl(Protocol):
    def init(self) -> None: ...
    def on_playback(self) -> None: ...
    def on_playpause(self) -> None: ...
    def on_volume(self) -> None: ...


class MediaControlWin32(MediaControl):
    def __init__(self) -> None:
        print("Win32")

    def init(self, player) -> None:
        print("Win32")

    def on_playback(self) -> None:
        print("Win32")

    def on_playpause(self) -> None:
        print("Win32")

    def on_volume(self) -> None:
        print("Win32")


class MediaControlMPRIS(MediaControl):
    def __init__(self) -> None:
        self.adapter = HAdapter()
        self.mpris = Server("PyMusicTerm", adapter=self.adapter)
        self.event = EventAdapter(root=self.mpris.root, player=self.mpris.player)

    def init(self, player):
        self.adapter.setup(player)
        self.mpris.loop(background=True)

    def on_playback(self):
        return self.event.on_playback()

    def on_playpause(self):
        return self.event.on_playpause()

    def on_volume(self):
        return self.event.on_volume()
