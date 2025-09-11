from typing import Protocol

from setting import SettingManager

setting = SettingManager()
if setting.os == "win32":
    from api.smtc.smtc import MediaControlWin32 as MediaControlWin

else:
    from mpris_server import EventAdapter
    from mpris_server import Server as ServerMpris

    from api.mpris.mpris import HAdapter


class MediaControl(Protocol):
    def init(self) -> None: ...
    def on_playback(self) -> None: ...
    def on_playpause(self) -> None: ...
    def on_volume(self) -> None: ...
    def populate_playlist(self) -> None: ...
    def set_current_song(self, index: int) -> None: ...


class Server(Protocol):
    root: str
    player: str


if setting.os == "win32":

    class MediaControlWin32(MediaControlWin, MediaControl):
        def __init__(self) -> None:
            super().__init__()

        def init(self, player) -> None:
            return super().init(player)

        def on_playback(self) -> None:
            return super().on_playback()

        def on_playpause(self) -> None:
            return super().on_playpause()

        def on_volume(self) -> None:
            return super().on_volume()

        def populate_playlist(self) -> None:
            return super().populate_playlist()

        def set_current_song(self, index: int) -> None:
            return super().set_current_song(index)

else:

    class MediaControlMPRIS(MediaControl):
        def __init__(self) -> None:
            self.adapter: HAdapter = HAdapter()
            self.mpris = ServerMpris(name="PyMusicTerm", adapter=self.adapter)
            self.event = EventAdapter(root=self.mpris.root, player=self.mpris.player)

        def init(self, player) -> None:
            self.adapter.setup(player)
            self.mpris.loop(background=True)

        def on_playback(self) -> None:
            return self.event.on_playback()

        def on_playpause(self) -> None:
            return self.event.on_playpause()

        def on_volume(self) -> None:
            return self.event.on_volume()

        def populate_playlist(self) -> None:
            pass

        def set_current_song(self, _: int) -> None:
            pass
