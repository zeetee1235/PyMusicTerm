import io
import logging
from collections.abc import Callable
from pathlib import Path

import music_tag
from PIL import Image
from pydub import AudioSegment
from pytubefix import Stream, YouTube

from .ytmusic import SongData

logger: logging.Logger = logging.getLogger(__name__)


def image_to_byte(image: Image) -> bytes:
    # BytesIO is a file-like buffer stored in memory
    img_byte_arr = io.BytesIO()
    # image.save expects a file-like as a argument
    image.save(img_byte_arr, format=image.format)
    # Turn the BytesIO object back into a bytes object
    img_byte_arr: bytes = img_byte_arr.getvalue()
    return img_byte_arr


def _download_from_yt(
    song: SongData,
    download_path: str,
    callback: None | Callable[[Stream, bytes, int], None] = None,
) -> str | None:
    try:
        yt = YouTube(
            f"https://www.youtube.com/watch?v={song.video_id}",
            on_progress_callback=callback,
        )
        return yt.streams.get_audio_only().download(
            output_path=download_path,
            filename=f"{song.video_id}.m4a",
        )
    except Exception:
        logger.exception("Exception when downloading youtube sound.")
        return None


def _convert_to_mp3(path: str) -> str:
    if not isinstance(path, str):
        msg: str = f"path must be a string, not {type(path)}"
        raise TypeError(msg)
    extention: str = Path(path).suffix
    new_path: str = path.replace(extention, ".mp3")
    audio = AudioSegment.from_file(path)
    audio.export(new_path, format="mp3")
    return new_path


def _delete_file(path: str) -> None:
    Path(path).unlink(missing_ok=True)


class Downloader:
    def __init__(self, download_path: str) -> None:
        self.download_path: str = download_path

    def download(self, song: SongData) -> str | None:
        self.song: SongData = song

        song_path = Path(f"{self.download_path}/{song.video_id}.mp3")
        if song_path.exists():
            return str(song_path)

        yt_path: str | None = _download_from_yt(
            song,
            self.download_path,
            self.on_progress,
        )

        if yt_path is None:
            return None

        converted_path: str = _convert_to_mp3(yt_path)

        file_path = music_tag.load_file(converted_path)
        file_path["title"] = song.title
        file_path["artist"] = list(song.artist)
        file_path["artwork"] = image_to_byte(song.thumbnail)
        file_path["album"] = song.album
        file_path.save()

        _delete_file(yt_path)

        return str(converted_path)

    def on_progress(self, stream: Stream, _: bytes, bytes_remaining: int) -> None:
        filesize: int = stream.filesize
        bytes_received: int = filesize - bytes_remaining
        percent: float = (bytes_received / filesize) * 100
        logger.info(f"Downloaded {percent:.2f}% of {stream.title}")  # noqa: G004
