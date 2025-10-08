import logging
import re
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
    logger.info(f"Lyrics search by {track}, {album}, {artist}, {duration}")  # noqa: G004
    try:
        result: Track = lrclib.get(
            track,
            artist,
            album,
            duration,
        )
        logger.info("Result: %s", result)
        result_path: Path = Path(setting.lyrics_dir) / f"{video_id}.lrc"
        if result:
            result_path.write_text(
                result.syncedLyrics if result.syncedLyrics else result.plainLyrics,
                encoding="utf-8",
            )
        else:
            result_path.touch()
    except Exception:
        logger.exception("EXCEPTION when downloading lyrics for song %s", video_id)


def time_to_seconds(t: str) -> float:
    parts: list[str] = t.split(":")
    parts: list[float] = [float(p) for p in re.split(r"[:.]", t) if p != ""]

    # Handle formats: [mm:ss.xx], [hh:mm:ss.xx], [ss.xx]
    if len(parts) == 4:  # h:m:s.ms
        h, m, s, ms = parts
        return h * 3600 + m * 60 + s + ms / 100
    if len(parts) == 3:  # m:s.ms
        m, s, ms = parts
        return m * 60 + s + ms / 100
    if len(parts) == 2:  # s.ms
        s, ms = parts
        return s + ms / 100
    return parts[0]


def parse_lyrics(lyrics: str) -> list[tuple[int, str]]:
    pattern = r"\[(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)]\s*(.*)"
    parsed = re.findall(pattern, lyrics)
    return [(time_to_seconds(t), text.strip()) for t, text in parsed]
