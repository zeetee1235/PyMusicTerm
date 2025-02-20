from typing import Protocol
from pytubefix import YouTube
from pydub import AudioSegment
from pathlib import Path


class SongData(Protocol):
    title: str
    duration: str
    videoId: str

    def get_formatted_artists(self) -> str: ...


class Downloader:
    def __init__(self, download_path: str):
        self.download_path = download_path

    def download(self, song: SongData) -> str | None:
        """Download a song from a song object and return the path of the downloaded file.
        If the file already exists, it will not be downloaded again and the path will be returned.

        Args:
            song (Song): The song to download

        Returns:
            path (str): The path of the downloaded file or None if the download failed
        """

        song_path = Path(
            f"{self.download_path}/{song.title} - {song.get_formatted_artists()}.mp3"
        )
        if song_path.exists():
            return str(song_path)

        yt_path = self._download_from_yt(song)
        converted_path = self._convert_to_mp3(yt_path)
        self._delete_file(yt_path)
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
            on_progress_callback=self.download_callback,
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

    def download_callback(self, stream: str, chunk: bytes, total: int) -> None:
        """Callback for the download process

        Args:
            stream (str): The stream of the download
            chunk (bytes): The chunk of the download
            total (int): The total size of the download
        """
        print(f"Downloading {chunk}/{total}")
