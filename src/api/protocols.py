from dataclasses import dataclass

from PIL import ImageFile


@dataclass
class SongData:
    title: str
    artist: list[str]
    duration: str
    videoId: str
    thumbnail: ImageFile
    album: str
    path: None | str = None

    def get_formatted_artists(self) -> str:
        """Get the formatted artists of the song."""
        return ", ".join(list(self.artist))
