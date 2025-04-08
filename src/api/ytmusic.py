import requests
import ytmusicapi
from dataclasses import dataclass
from PIL import Image

from api.protocols import SongData


@dataclass
class LyricsResult:
    lyrics: str
    source: str


class YTMusic:
    def __init__(self):
        self.client = ytmusicapi.YTMusic()

    def search(self, query: str, filter: str = "songs") -> list[SongData]:
        """Search for a song on YTMusic
        Args:
            query (str): The query to search for
            filter (str, optional): The filter to use. Defaults to "songs".

        Raises:
            TypeError: If query or filter is not a string

        Returns:
            list[Song]: The list of songs found
        """
        if not isinstance(query, str):
            raise TypeError(f"query must be a string, not {type(query)}")
        if not isinstance(filter, str):
            raise TypeError(f"filter must be a string, not {type(filter)}")

        results = self.client.search(query, filter)
        r = []
        for result in results:
            title: str = result.get("title", "Unknown")
            artist: list[str] = [artist["name"] for artist in result.get("artists", [])]
            duration: str = result.get("duration", "Unknown")
            videoId: str = result.get("videoId", "Unknown")
            thumbnail = Image.open(
                requests.get(result["thumbnails"][0]["url"], stream=True).raw
            )
            x = result.get("album", None)
            if x:
                album = x.get("name")
            else:
                album = "Unknown"
            r.append(
                SongData(
                    title=title,
                    artist=artist,
                    duration=duration,
                    videoId=videoId,
                    thumbnail=thumbnail,
                    album=album,
                )
            )
        return r
