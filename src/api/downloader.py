import sys
from typing import Protocol
from pytubefix import YouTube, Stream
from pydub import AudioSegment
from pathlib import Path

if sys.platform == "win32":
    from .windows.notification import Notification as Notification
else:

    class Notification(Protocol):
        def update_download_progress(self, value: int, total: int) -> None: ...

        def update_progress(self, value: int, total: int) -> None: ...

        def finish_download(self) -> None: ...


class SongData(Protocol):
    title: str
    duration: str
    videoId: str

    def get_formatted_artists(self) -> str: ...


class Downloader:
    def __init__(self, download_path: str) -> None:
        self.download_path = download_path

    def download(self, song: SongData) -> str | None:
        """Download a song from a song object and return the path of the downloaded file.
        If the file already exists, it will not be downloaded again and the path will be returned.

        Args:
            song (Song): The song to download

        Returns:
            path (str): The path of the downloaded file or None if the download failed
        """
        self.notification = Notification(
            title=f"{song.title} - {song.get_formatted_artists()}",
            status="Downloading...",
            value=0,
            valueStringOverride="",
        )
        song_path = Path(
            f"{self.download_path}/{song.title} - {song.get_formatted_artists()}.mp3"
        )
        if song_path.exists():
            return str(song_path)

        yt_path = self._download_from_yt(song)
        self.notification.update_progress(2, 4)
        converted_path = self._convert_to_mp3(yt_path)
        self.notification.update_progress(3, 4)
        self._delete_file(yt_path)
        self.notification.update_progress(4, 4)
        self.notification.finish_download()
        return str(converted_path)

    def _download_from_yt(self, song: SongData) -> str:
        """Download a song from a song

        Args:
            song (SearchSongResult): The song to download

        Returns:
            path (str): The path of the downloaded file or None if the download failed
        """
        yt = YouTube(
            f"https://www.youtube.com/watch?v={song.videoId}",
            on_progress_callback=self.on_progress,
            on_complete_callback=self.finish,
        )
        return yt.streams.get_audio_only().download(
            output_path=self.download_path,
            filename=f"{song.title} - {song.get_formatted_artists()}.m4a",
        )

    def _convert_to_mp3(self, path: str) -> str:
        """Convert a m4a file to mp3

        Args:
            path (str): path to the m4a file

        Returns:
            str: path to the mp3 file
        """
        audio = AudioSegment.from_file(path)
        audio.export(path.replace(".m4a", ".mp3"), format="mp3")
        return path.replace(".m4a", ".mp3")

    def _delete_file(self, path: str) -> None:
        """Delete a file

        Args:
            path (str): path to the file
        """
        Path(path).unlink(missing_ok=True)

    def on_progress(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:  # pylint: disable=W0613
        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        self.notification.update_download_progress(bytes_received, filesize)

    def finish(self, path: str, stream: Stream) -> None:
        """Finish the download"""
        self.notification.update_progress(1, 4)
