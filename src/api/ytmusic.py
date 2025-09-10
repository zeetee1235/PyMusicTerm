from dataclasses import dataclass

import requests
import ytmusicapi
from PIL import Image
from PIL.ImageFile import ImageFile

from api.protocols import SongData


@dataclass
class LyricsResult:
    lyrics: str
    source: str


class YTMusic:
    def __init__(self) -> None:
        self.client = ytmusicapi.YTMusic()

    def search(self, query: str, filter: str = "songs") -> list[SongData]:
        """
        Search for a song on YTMusic.

        Args:
            query (str): The query to search for
            filter (str, optional): The filter to use. Defaults to "songs".

        Raises:
            TypeError: If query or filter is not a string

        Returns:
            list[Song]: The list of songs found

        """
        if not isinstance(query, str):
            msg: str = f"query must be a string, not {type(query)}"
            raise TypeError(msg)
        if not isinstance(filter, str):
            msg = f"filter must be a string, not {type(filter)}"
            raise TypeError(msg)

        results: list[dict] = self.client.search(query, filter)
        r: list[SongData] = []
        for result in results:
            title: str = result.get("title", "Unknown")
            artist: list[str] = [artist["name"] for artist in result.get("artists", [])]
            duration: str = result.get("duration", "Unknown")
            videoId: str = result.get("videoId", "Unknown")
            thumbnail: ImageFile = Image.open(
                requests.get(result["thumbnails"][0]["url"], stream=True).raw,
            )
            x = result.get("album", None)
            album = x.get("name") if x else "Unknown"
            r.append(
                SongData(
                    title=title,
                    artist=artist,
                    duration=duration,
                    videoId=videoId,
                    thumbnail=thumbnail,
                    album=album,
                ),
            )
        return r
