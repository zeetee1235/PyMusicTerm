import logging
from pathlib import Path

from lrcup import LRCLib
from lrcup.controller import Track

from setting import Setting

logger: logging.Logger = logging.getLogger(__name__)

setting = Setting()

lrclib = LRCLib()


def download_lyrics(
    video_id: str,
    track: str | None = None,
    album: str | None = None,
    artist: str | None = None,
    duration: int | None = None,
) -> None:
    logger.info(f"Lyrics search by {track}, {album}, {artist}, {duration}")
    try:
        result: Track = lrclib.get(
            track,
            artist,
            album,
            duration,
        )
        logger.info("Result: %s", result)
        result_path: Path = Path(setting.lyrics_dir) / f"{video_id}.md"
        if result:
            result_path.write_text(
                result.syncedLyrics if result.syncedLyrics else result.plainLyrics,
                encoding="utf-8",
            )
        else:
            result_path.touch()
    except Exception:
        logger.exception("EXCEPTION when downloading lyrics for song %s", video_id)
