import requests
import ytmusicapi
from dataclasses import dataclass
import ytmusicapi.exceptions
from api.lyrics import LyricsDownloader
from PIL import Image, ImageFile
import requests_cache


# Set up a cache for requests
requests_cache.install_cache(
    "ytmusic_cache",
)


@dataclass
class SongData:
    title: str
    artist: list[str]
    duration: str
    videoId: str
    thumbnail: ImageFile
    album: str

    def get_formatted_artists(self) -> str:
        """Get the formatted artists of the song"""
        return ", ".join([artist for artist in self.artist])


@dataclass
class LyricsResult:
    lyrics: str
    source: str


class YTMusic:
    def __init__(self, lyrics_downloader: LyricsDownloader):
        self.client = ytmusicapi.YTMusic()
        self.lyrics_downloader = lyrics_downloader

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

    def get_lyrics(self, song: SongData) -> LyricsResult | None:
        """Get the lyrics of a song
        Args:
            video_id (str): The video id of the song
        Returns:
            str: The lyrics of the song
        """
        lyrics_id = self.client.get_watch_playlist(song.videoId)["lyrics"]
        try:
            lyrics = self.client.get_lyrics(lyrics_id)
        except ytmusicapi.exceptions.YTMusicError:
            lyrics = None

        if lyrics:
            return self.lyrics_downloader.save(
                LyricsResult(
                    lyrics=lyrics["lyrics"],
                    source=lyrics["source"],
                ),
                song,
            )
        else:
            return self.lyrics_downloader.save(
                LyricsResult(
                    lyrics="None",
                    source="None",
                ),
                song,
            )
