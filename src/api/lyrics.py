from typing import Protocol
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LyricsData(Protocol):
    lyrics: str
    source: str


@dataclass
class SongData(Protocol):
    title: str
    duration: str
    videoId: str

    def get_formatted_artists(self) -> str: ...


class LyricsDownloader:
    def __init__(self, download_path: str):
        self.download_path = download_path

    def save(self, lyrics: LyricsData, song: SongData) -> Path | None:
        """Save the lyrics to a markdown file

        Args:
            lyrics (str): The lyrics to save

        Returns:
            str | None: The path of the saved file or None if the save failed
        """
        lyrics_path = Path(
            f"{self.download_path}/{song.title} - {song.get_formatted_artists()}.md"
        )
        with open(lyrics_path, "w", encoding="utf-8") as f:
            f.write(lyrics.lyrics)
        return lyrics_path
