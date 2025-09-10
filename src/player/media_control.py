from pathlib import Path
from typing import Any, Protocol

from loguru import logger
from PIL import Image

from setting import SettingManager

setting = SettingManager()
if setting.os == "win32":
    from winrt._winrt_windows_foundation import Uri
    from winrt._winrt_windows_media_core import MediaSource
    from winrt._winrt_windows_media_playback import (
        MediaItemDisplayProperties,
        MediaPlaybackItem,
    )
    from winrt._winrt_windows_storage import StorageFile
    from winrt.windows.foundation import Uri
    from winrt.windows.media import (
        MediaPlaybackStatus,
        MediaPlaybackType,
        SystemMediaTransportControls,
        SystemMediaTransportControlsButton,
    )
    from winrt.windows.media.core import MediaSource
    from winrt.windows.media.playback import (
        MediaPlaybackItem,
        MediaPlaybackList,
        MediaPlayer,
    )
    from winrt.windows.storage import StorageFile
    from winrt.windows.storage.streams import RandomAccessStreamReference

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


class MediaControlWin32:
    def __init__(self) -> None:
        self.player: Any = None
        self.media_player: MediaPlayer | None = None
        self.smtc: SystemMediaTransportControls | None = None
        self.playlist: MediaPlaybackList | None = None

    def init(self, player: Any) -> None:
        """Attach SMTC to the PyMusicTermPlayer"""
        try:
            self.player = player
            self.media_player = MediaPlayer()
            self.media_player.auto_play = True
            self.populate_playlist()
            self.media_player.volume = 0.0
            # SMTC setup
            self.smtc = self.media_player.system_media_transport_controls
            self.smtc.shuffle_enabled = True
            self.smtc.is_play_enabled = True
            self.smtc.is_pause_enabled = True
            self.smtc.is_next_enabled = len(player.list_of_downloaded_songs) > 1
            self.smtc.is_previous_enabled = len(player.list_of_downloaded_songs) > 1
            self.smtc.is_enabled = True

            def button_pressed(sender, args) -> None:
                try:
                    logger.debug(f"SMTC button pressed: {args.button}")

                    if args.button == SystemMediaTransportControlsButton.PLAY:
                        self.play()
                    elif args.button == SystemMediaTransportControlsButton.PAUSE:
                        self.pause()
                    elif args.button == SystemMediaTransportControlsButton.NEXT:
                        self.player.next()
                        self.play()
                    elif args.button == SystemMediaTransportControlsButton.PREVIOUS:
                        self.player.previous()
                        self.play()

                except Exception as e:
                    logger.error(f"Error in SMTC button callback: {e}")

            self.smtc.add_button_pressed(button_pressed)
            logger.info("MediaControlWin32 initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MediaControlWin32: {e}")
            raise

    def populate_playlist(self) -> MediaPlaybackList:
        self.playlist = MediaPlaybackList()
        for song in self.player.list_of_downloaded_songs:
            try:
                uri: Uri = Uri(f"file:///{song.path.resolve()}")
                source: MediaSource = MediaSource.create_from_uri(uri)
                item: MediaPlaybackItem = MediaPlaybackItem(source)

                # Set ALL metadata directly on the MediaPlaybackItem
                display_props: MediaItemDisplayProperties = (
                    item.get_display_properties()
                )
                display_props.type = MediaPlaybackType.MUSIC
                display_props.music_properties.title = song.title or "Unknown Title"
                display_props.music_properties.artist = (
                    ", ".join([song.get_formatted_artists()]) or "Unknown Artist"
                )
                display_props.music_properties.album_title = ""

                try:
                    display_props.thumbnail = self.get_ras_from_pil(
                        song.thumbnail,
                        song.videoId,
                    )
                except Exception as e:
                    logger.warning(f"Failed to set thumbnail for {song.title}: {e}")

                item.apply_display_properties(display_props)

                self.playlist.items.append(item)
                logger.debug(
                    f"Added song with metadata: {song.title} by {song.get_formatted_artists()}",
                )

            except Exception as e:
                logger.error(f"Failed to add song {song.path} to playlist: {e}")
                continue
        self.media_player.source = self.playlist
        return self.playlist

    def get_ras_from_pil(
        self,
        img: Image.Image,
        videoId: str,
    ) -> RandomAccessStreamReference:
        """Convert PIL image to RandomAccessStreamReference for thumbnails"""
        covers_dir = Path(setting.cover_dir)

        tmp_file: Path = covers_dir / f"{videoId}_cover.png"
        img.save(tmp_file, format="PNG")

        storage_file: StorageFile = StorageFile.get_file_from_path_async(
            str(tmp_file.absolute()),
        ).get()
        return RandomAccessStreamReference.create_from_file(storage_file)

    def on_playback(self) -> None:
        pass

    def on_playpause(self) -> None:
        if not self.smtc or not self.player:
            return
        try:
            if hasattr(self.player, "playing") and self.player.playing:
                self.smtc.playback_status = MediaPlaybackStatus.PLAYING
            else:
                self.smtc.playback_status = MediaPlaybackStatus.PAUSED
        except Exception as e:
            logger.error(f"Error in on_playpause: {e}")

    def on_volume(self) -> None:
        if not self.smtc or not self.player:
            return
        try:
            if hasattr(self.player, "volume") and self.media_player:
                self.media_player.volume = self.player.volume
        except Exception as e:
            logger.error(f"Error in on_volume: {e}")

    def play(self) -> None:
        try:
            logger.debug("SMTC Play button pressed")
            if self.player:
                self.player.resume_song()
            self.on_playpause()
        except Exception as e:
            logger.error(f"Error in play(): {e}")

    def pause(self) -> None:
        try:
            logger.debug("SMTC Pause button pressed")
            if self.player:
                self.player.pause_song()
            self.on_playpause()
        except Exception as e:
            logger.error(f"Error in pause(): {e}")

    def set_current_song(self, index: int) -> None:
        try:
            if self.playlist and 1 <= index < len(self.playlist.items) + 1:
                self.playlist.move_to(index)
                self.play()
                logger.debug(f"SMTC playlist moved to index: {index}")
        except Exception as e:
            logger.warning(f"Could not sync playlist position: {e}")


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
