import logging
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


class MediaControl(Protocol):
    def init(self, player) -> None: ...
    def on_playback(self) -> None: ...
    def on_playpause(self) -> None: ...
    def on_volume(self) -> None: ...
    def populate_playlist(self) -> None: ...
    def set_current_song(self, index: int) -> None: ...


def check_termux_api() -> bool:
    """Check if termux-api is installed"""
    return shutil.which("termux-notification") is not None


class TermuxMediaNotification:
    """Media notification using termux-api commands"""

    NOTIFICATION_ID = "pymusicterm_media"

    def __init__(self):
        if not check_termux_api():
            raise RuntimeError(
                "termux-api not found. Install with: pkg install termux-api",
            )

        self.player = None
        self.current_notification = None
        logger.info("Termux media notification initialized")

    def _run_termux_command(self, command: list[str]) -> bool:
        """Run a termux-api command"""
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.error(f"Termux command failed: {result.stderr}")
                return False
            return True
        except subprocess.TimeoutExpired:
            logger.error(f"Termux command timed out: {' '.join(command)}")
            return False
        except Exception as e:
            logger.error(f"Failed to run termux command: {e}")
            return False

    def show_notification(
        self,
        title: str,
        artist: str,
        album: str,
        image_path: str = None,
        is_playing: bool = True,
    ):
        """Show or update media notification"""
        try:
            # Build termux-notification command
            cmd = [
                "termux-notification",
                "--id",
                self.NOTIFICATION_ID,
                "--title",
                title,
                "--content",
                f"{artist} • {album}",
                "--group",
                "music",
                "--ongoing",
                "--alert-once",
                "--priority",
                "max",
            ]

            # Add album art if available
            if image_path and Path(image_path).exists():
                cmd.extend(["--image-path", image_path])

            # Add media buttons
            if is_playing:
                # Previous, Pause, Next
                cmd.extend(
                    [
                        "--button1",
                        "⏮ Previous",
                        "--button1-action",
                        "termux-toast 'Previous'",
                        "--button2",
                        "⏸ Pause",
                        "--button2-action",
                        "termux-toast 'Pause'",
                        "--button3",
                        "⏭ Next",
                        "--button3-action",
                        "termux-toast 'Next'",
                    ],
                )
            else:
                # Previous, Play, Next
                cmd.extend(
                    [
                        "--button1",
                        "⏮ Previous",
                        "--button1-action",
                        "termux-toast 'Previous'",
                        "--button2",
                        "▶ Play",
                        "--button2-action",
                        "termux-toast 'Play'",
                        "--button3",
                        "⏭ Next",
                        "--button3-action",
                        "termux-toast 'Next'",
                    ],
                )

            # Add action on notification tap
            cmd.extend(
                [
                    "--action",
                    "termux-toast 'PyMusicTerm'",
                ],
            )

            # Execute command
            success = self._run_termux_command(cmd)

            if success:
                logger.info(f"Notification shown: {title} - {artist}")
            else:
                logger.error("Failed to show notification")

        except Exception as e:
            logger.error(f"Failed to show notification: {e}", exc_info=True)

    def hide_notification(self):
        """Remove the notification"""
        try:
            cmd = ["termux-notification-remove", self.NOTIFICATION_ID]
            self._run_termux_command(cmd)
            logger.info("Notification removed")
        except Exception as e:
            logger.error(f"Failed to remove notification: {e}")


class TermuxMediaNotificationWithIPC(TermuxMediaNotification):
    """Enhanced version with IPC for button handling"""

    def __init__(self):
        super().__init__()
        self.fifo_path = Path.home() / ".pymusicterm" / "control.fifo"
        self._setup_fifo()

    def _setup_fifo(self):
        """Create FIFO pipe for receiving button commands"""
        try:
            self.fifo_path.parent.mkdir(exist_ok=True)

            # Remove old FIFO if exists
            if self.fifo_path.exists():
                self.fifo_path.unlink()

            # Create new FIFO
            subprocess.run(["mkfifo", str(self.fifo_path)], check=True)
            logger.info(f"FIFO created at {self.fifo_path}")

        except Exception as e:
            logger.error(f"Failed to create FIFO: {e}")
            self.fifo_path = None

    def show_notification(
        self,
        title: str,
        artist: str,
        album: str,
        image_path: str = None,
        is_playing: bool = True,
    ):
        """Show notification with working button actions via FIFO"""
        try:
            if not self.fifo_path:
                super().show_notification(title, artist, album, image_path, is_playing)
                return

            cmd = [
                "termux-notification",
                "--id",
                self.NOTIFICATION_ID,
                "--title",
                title,
                "--content",
                f"{artist} • {album}",
                "--group",
                "music",
                "--ongoing",
                "--alert-once",
                "--priority",
                "max",
            ]

            if image_path and Path(image_path).exists():
                cmd.extend(["--image-path", image_path])

            # Button actions write to FIFO
            fifo_str = str(self.fifo_path)

            if is_playing:
                cmd.extend(
                    [
                        "--button1",
                        "⏮",
                        "--button1-action",
                        f"echo 'previous' > {fifo_str}",
                        "--button2",
                        "⏸",
                        "--button2-action",
                        f"echo 'pause' > {fifo_str}",
                        "--button3",
                        "⏭",
                        "--button3-action",
                        f"echo 'next' > {fifo_str}",
                    ],
                )
            else:
                cmd.extend(
                    [
                        "--button1",
                        "⏮",
                        "--button1-action",
                        f"echo 'previous' > {fifo_str}",
                        "--button2",
                        "▶",
                        "--button2-action",
                        f"echo 'play' > {fifo_str}",
                        "--button3",
                        "⏭",
                        "--button3-action",
                        f"echo 'next' > {fifo_str}",
                    ],
                )

            self._run_termux_command(cmd)
            logger.info(f"Notification with IPC shown: {title}")

        except Exception as e:
            logger.error(f"Failed to show notification with IPC: {e}")

    def listen_for_commands(self):
        """Listen for button press commands (blocking)"""
        if not self.fifo_path:
            return

        try:
            while True:
                with open(self.fifo_path) as fifo:
                    command = fifo.read().strip()
                    if command and self.player:
                        self._handle_command(command)
        except Exception as e:
            logger.error(f"FIFO listener error: {e}")

    def _handle_command(self, command: str):
        """Handle commands from notification buttons"""
        logger.info(f"Received command: {command}")

        if command == "play":
            self.player.resume_song()
        elif command == "pause":
            self.player.pause_song()
        elif command == "next":
            self.player.next()
        elif command == "previous":
            self.player.previous()


class MediaControlAndroid(MediaControl):
    """Termux media notification control - drop-in replacement"""

    def __init__(self):
        try:
            # Use IPC version for working buttons
            self.notification = TermuxMediaNotificationWithIPC()
            logger.info("Termux media notification initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Termux notifications: {e}")
            self.notification = None

    def init(self, player) -> None:
        """Initialize with player instance"""
        if self.notification:
            self.notification.player = player
            self.on_playback()

            # Start button listener in background thread
            import threading

            listener_thread = threading.Thread(
                target=self.notification.listen_for_commands,
                daemon=True,
            )
            listener_thread.start()

    def on_playback(self) -> None:
        """Called when track changes"""
        if not self.notification or not self.notification.player:
            return

        try:
            player = self.notification.player
            song = player.list_of_downloaded_songs[player.current_song_index]

            # Find album art
            cover_path = song.path.parent / f"{song.video_id}_cover.png"
            if not cover_path.exists():
                cover_path = None

            self.notification.show_notification(
                title=song.title,
                artist=song.get_formatted_artists(),
                album=song.album,
                image_path=str(cover_path) if cover_path else None,
                is_playing=player.playing,
            )
        except Exception as e:
            logger.error(f"Failed to update notification: {e}")

    def on_playpause(self) -> None:
        """Called when play/pause state changes"""
        self.on_playback()

    def on_volume(self) -> None:
        """Called when volume changes"""

    def populate_playlist(self) -> None:
        """Populate playlist (not needed)"""

    def set_current_song(self, index: int) -> None:
        """Set current song"""
        self.on_playback()
