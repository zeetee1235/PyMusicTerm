import ytmusicapi
from dataclasses import dataclass


@dataclass
class SongArtist:
    name: str
    id: str


@dataclass
class SearchSongResult:
    title: str
    artist: list[SongArtist]
    album: str
    duration: int
    videoId: str
    thumbnail: str

    def get_formatted_artists(self) -> str:
        """Get the formatted artists of the song"""
        return ", ".join([artist.name for artist in self.artist])


class YTMusic:
    def __init__(self):
        self.client = ytmusicapi.YTMusic()

    def search(self, query: str, filter: str = "songs") -> list[SearchSongResult]:
        """Search for a song on YTMusic
        Args:
            query (str): The query to search for
            filter (str, optional): The filter to use. Defaults to "songs".
        Returns:
            list[Song]: The list of songs found
        """
        results = self.client.search(query, filter)
        return [
            SearchSongResult(
                title=result["title"],
                artist=[SongArtist(**artist) for artist in result["artists"]],
                album=result["album"]["name"],
                duration=result["duration"],
                videoId=result["videoId"],
                thumbnail=result["thumbnails"][0]["url"],
            )
            for result in results
        ]
