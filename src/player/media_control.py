import logging
from typing import Protocol

from api.protocols import PyMusicTermPlayer
from setting import SettingManager

logger: logging.Logger = logging.getLogger(__name__)

setting = SettingManager()
if setting.os == "win32":
    from api.smtc.smtc import MediaControlWin32 as MediaControlWin
else:
    from api.mpris.mpris import DBusAdapter


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

        def init(self, player: PyMusicTermPlayer) -> None:
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

elif setting.os == "android":
    from api.android.termux import MediaControlAndroid  # noqa: F401
else:

    class MediaControlMPRIS:
        """Drop-in replacement for mpris_server based implementation"""

        def __init__(self) -> None:
            self.adapter: DBusAdapter = DBusAdapter()
            logger.info("MediaControlMPRIS initialized")

        def init(self, player: PyMusicTermPlayer) -> None:
            """Initialize with player and start background loop"""
            logger.info("Initializing MediaControlMPRIS with player")
            self.adapter.setup(player)
            self.adapter.start_background()

        def on_playback(self) -> None:
            """Handle playback events"""
            return self.adapter.on_playback()

        def on_playpause(self) -> None:
            """Handle play/pause events"""
            return self.adapter.on_playpause()

        def on_volume(self) -> None:
            """Handle volume events"""
            return self.adapter.on_volume()

        def populate_playlist(self) -> None:
            """Populate playlist (no-op for MPRIS)"""

        def set_current_song(self, _: int) -> None:
            """Set current song (no-op for MPRIS)"""
