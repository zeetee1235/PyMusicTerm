from typing import Protocol

from setting import SettingManager

setting = SettingManager()
if setting.os == "win32":
    pass
else:
    from mpris_server import EventAdapter
    from mpris_server import Server as ServerMpris
    from api.mpris.mpris import HAdapter


class MediaControl(Protocol):
    def init(self) -> None: ...
    def on_playback(self) -> None: ...
    def on_playpause(self) -> None: ...
    def on_volume(self) -> None: ...


class Server(Protocol):
    root: str
    player: str


class MediaControlWin32(MediaControl):
    def __init__(self) -> None: ...

    def init(self, player) -> None: ...

    def on_playback(self) -> None: ...

    def on_playpause(self) -> None: ...

    def on_volume(self) -> None: ...


class MediaControlMPRIS(MediaControl):
    def __init__(self) -> None:
        self.adapter = HAdapter()
        self.mpris = ServerMpris(name="PyMusicTerm", adapter=self.adapter)
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
