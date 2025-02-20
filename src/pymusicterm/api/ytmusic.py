import ytmusicapi
from ytmusicapi.exceptions import YTMusicError
from dataclasses import dataclass
from typing import Protocol
import ytmusicapi.exceptions
import ytmusicapi.ytmusic
from pymusicterm.api.lyrics import LyricsDownloader

class SongData(Protocol):
    title: str
    duration: str
    videoId: str

    def get_formatted_artists(self) -> str:
        """Format the list of artists to a string

        Returns:
            str: a string with the formatted artists
        """


@dataclass
class SongArtist:
    name: str
    id: str


@dataclass
class SearchResult(SongData):
    title: str
    artist: list[SongArtist]
    duration: int
    videoId: str

    def get_formatted_artists(self) -> str:
        """Get the formatted artists of the song"""
        return ", ".join([artist.name for artist in self.artist])


@dataclass
class LyricsResult:
    lyrics: str
    source: str


class YTMusic:
    def __init__(self, lyrics_downloader: LyricsDownloader):
        self.client = ytmusicapi.YTMusic()
        self.lyrics_downloader = lyrics_downloader

    def search(self, query: str, filter: str = "songs") -> list[SearchResult]:
        """Search for a song on YTMusic
        Args:
            query (str): The query to search for
            filter (str, optional): The filter to use. Defaults to "songs".
        Returns:
            list[Song]: The list of songs found
        """
        results = self.client.search(query, filter)
        return [
            SearchResult(
                title=result["title"],
                artist=[SongArtist(**artist) for artist in result["artists"]],
                duration=result["duration"],
                videoId=result["videoId"],
            )
            for result in results
        ]

    def get_lyrics(self, song: SearchResult) -> LyricsResult | None:
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
