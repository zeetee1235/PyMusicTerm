import asyncio
import contextlib
import logging
import time

from pypresence import ActivityType, AioPresence, DiscordNotFound

from api.protocols import PyMusicTermPlayer, SongData

CLIENT_ID = "1275918029565464608"
UPDATE_INTERVAL = 0.7
NO_SONG_SLEEP_INTERVAL = 5
MAX_RETRIES = 3
RETRY_DELAY = 5

logger: logging.Logger = logging.getLogger(__name__)


class RichPresenceError(Exception):
    """Custom exception for Rich Presence errors."""


def create_progress_bar(percentage: int) -> str:
    """Create a text-based progress bar."""
    percentage = max(0, min(percentage, 100))
    total_segments = 10
    completed_segments: int = round((percentage / 100) * total_segments)
    return "▰" * completed_segments + "▱" * (total_segments - completed_segments)


def format_time(seconds: float) -> str:
    """Format seconds into MM:SS string."""
    return time.strftime("%M:%S", time.gmtime(seconds))


async def rich_presence(player: PyMusicTermPlayer) -> None:
    """Main function to run the Rich Presence update loop."""
    rpc = None
    try:
        rpc = AioPresence(CLIENT_ID)
        await rpc.connect()

        while True:
            try:
                song: SongData | None = player.current_song
                if song is None:
                    logger.debug("No song is playing")
                    await asyncio.sleep(NO_SONG_SLEEP_INTERVAL)
                    continue
                try:
                    artist_name: str = song.get_formatted_artists()
                    song_name: str = song.title
                    album_name: str = song.album
                    track_length: int = player.music_player.song_length
                    track_time: int = player.music_player.position

                    current_time: str = format_time(track_time)
                    song_length: str = format_time(track_length)
                    progress_percentage = int((track_time / track_length) * 100)

                    await rpc.update(
                        activity_type=ActivityType.LISTENING,
                        state=f"{current_time} {create_progress_bar(progress_percentage)} {song_length}",
                        details=f"{song_name} - {artist_name}",
                        large_image="play" if player.playing else "pause",
                        large_text=f"Album: {album_name}",
                    )

                except KeyError as e:
                    msg: str = f"Missing key in song data: {e}"
                    raise RichPresenceError(msg) from e
                except Exception as e:
                    msg = f"Failed to update rich presence: {e}"
                    raise RichPresenceError(msg) from e

                await asyncio.sleep(UPDATE_INTERVAL)
            except RichPresenceError as e:
                logger.error(f"Rich Presence Error: {e}")
            except asyncio.CancelledError:
                with contextlib.suppress(Exception):
                    await rpc.clear()
                with contextlib.suppress(Exception):
                    await rpc.sock_writer.close()
                raise
            except Exception as e:
                logger.exception(
                    f"Unexpected error in update loop: {e}",
                )
                await asyncio.sleep(RETRY_DELAY)
    except DiscordNotFound:
        logger.warning("No discord found")
    except Exception as e:
        logger.critical(
            f"Critical error in Rich Presence main function: {e}",
        )
