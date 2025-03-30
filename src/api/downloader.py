from pytubefix import YouTube, Stream
from pydub import AudioSegment
from pathlib import Path
from api.notification_manager import NotificationManager
from typing import Callable
import music_tag
import requests
from .ytmusic import SearchResult


def _download_from_yt(
    song: SearchResult,
    download_path: str,
    callback: None | Callable[[Stream, bytes, int], None] = None,
) -> str | None:
    """Download a song from a song

    Args:
        song (SearchSongResult): The song to download

    Returns:
        path (str): The path of the downloaded file or None if the download failed
    """
    try:
        yt = YouTube(
            f"https://www.youtube.com/watch?v={song.videoId}",
            on_progress_callback=callback,
        )
        return yt.streams.get_audio_only().download(
            output_path=download_path,
            filename=f"{song.videoId}.m4a",
        )
    except Exception as e:
        print(e)
        return None


def _convert_to_mp3(path: str) -> str:
    """Convert an audio file to mp3

    Args:
        path (str): path to the downloanded AUDIO file

    Returns:
        str: path to the mp3 file
    """

    if not isinstance(path, str):
        raise TypeError(f"path must be a string, not {type(path)}")
    extention = Path(path).suffix
    new_path = path.replace(extention, ".mp3")
    audio = AudioSegment.from_file(path)
    audio.export(new_path, format="mp3")
    return new_path


def _delete_file(path: str) -> None:
    """Delete a file

    Args:
        path (str): path to the file
    """
    Path(path).unlink(missing_ok=True)


class Downloader:
    def __init__(self, download_path: str) -> None:
        self.download_path = download_path
        self.notification = NotificationManager()

    def download(self, song: SearchResult) -> str | None:
        """Download a song from a song object and return the path of the downloaded file.
        If the file already exists, it will not be downloaded again and the path will be returned.

        Args:
            song (Song): The song to download

        Returns:
            path (str): The path of the downloaded file or None if the download failed
        """
        self.song = song

        song_path = Path(f"{self.download_path}/{song.videoId}.mp3")
        if song_path.exists():
            return str(song_path)

        yt_path = _download_from_yt(song, self.download_path, self.on_progress)

        if yt_path is None:
            return None

        converted_path = _convert_to_mp3(yt_path)

        file_path = music_tag.load_file(converted_path)
        file_path["title"] = song.title
        file_path["artist"] = [artist for artist in song.artist]
        file_path["artwork"] = requests.get(song.thumbnail, stream=True).raw.read()
        file_path["album"] = song.album
        file_path.save()

        _delete_file(yt_path)

        return str(converted_path)

    def on_progress(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        percent = (bytes_received / filesize) * 100
        print(f"Downloaded {percent:.2f}% of {stream.title}")
