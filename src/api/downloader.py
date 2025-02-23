from typing import Protocol
from pytubefix import YouTube, Stream
from pydub import AudioSegment
from pathlib import Path
from api.notification_manager import NotificationManager
from setting import have_internet


class SongData(Protocol):
    title: str
    duration: str
    videoId: str

    def get_formatted_artists(self) -> str: ...


class Downloader:
    def __init__(self, download_path: str) -> None:
        self.download_path = download_path
        self.notification = NotificationManager()

    def download(self, song: SongData) -> str | None:
        """Download a song from a song object and return the path of the downloaded file.
        If the file already exists, it will not be downloaded again and the path will be returned.

        Args:
            song (Song): The song to download

        Returns:
            path (str): The path of the downloaded file or None if the download failed
        """
        self.song = song

        song_path = Path(
            f"{self.download_path}/{song.title} - {song.get_formatted_artists()}.mp3"
        )
        if song_path.exists():
            return str(song_path)

        if not have_internet():
            self.notification.send_notification(
                "No internet connection",
                "Please connect to the internet to download songs.",
            )
            return None

        self.notification.send_notification(
            f"Downloading {song.title} - {song.get_formatted_artists()}",
            "Starting download - 1/4",
        )
        yt_path = self._download_from_yt(song)

        self.notification.send_notification(
            f"Downloading {self.song.title} - {self.song.get_formatted_artists()}",
            "Song converted to mp3 - 2/4",
        )
        converted_path = self._convert_to_mp3(yt_path)

        self.notification.send_notification(
            "Downloading {self.song.title} - {self.song.get_formatted_artists()}",
            "Deleting cache - 3/4",
        )
        self._delete_file(yt_path)

        self.notification.send_notification(
            f"Downloading {self.song.title} - {self.song.get_formatted_artists()}",
            "Download finished - 4/4",
        )
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

    def on_progress(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        self.notification.send_notification(
            f"Downloading {self.song.title} - {self.song.get_formatted_artists()}",
            f"Download {bytes_received / filesize} - 1/4",
        )
