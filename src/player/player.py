from pathlib import Path

import music_tag
from api.ytmusic import SearchResult, YTMusic
from api.music_player import MusicPlayer
from api.downloader import Downloader
from player.media_control import MediaControl
from setting import SettingManager, fetch_files_from_folder
from random import shuffle
from api.lyrics import LyricsDownloader
from dataclasses import dataclass


@dataclass
class SongData:
    title: str
    duration: str
    videoId: str
    thumbnail: str
    album: str
    artist: list[str]
    path: Path

    def get_formatted_artists(self) -> str:
        """Get the formatted artists of the song"""
        return ", ".join([artist for artist in self.artist])


class PyMusicTermPlayer:
    def __init__(
        self,
        setting: SettingManager,
        media_control: MediaControl,
    ) -> None:
        self.media_control = media_control
        self.setting = setting
        self.music_player = MusicPlayer(self.setting.volume)
        lyrics = LyricsDownloader(self.setting.lyrics_dir)
        self.ytm = YTMusic(lyrics)
        self.downloader = Downloader(self.setting.music_dir)
        self.list_of_downloaded_songs: list[SongData] = self.get_downloaded_songs()
        self.dict_of_song_result: dict[str, SearchResult] = {}
        self.current_song_index = 0
        self.current_song: SongData | None = None

    def get_downloaded_songs(self) -> list[SongData]:
        """Get the list of downloaded songs

        Returns:
            list[Song]: the list of downloaded songs
        """
        songs = fetch_files_from_folder(self.setting.music_dir, "mp3")
        list_of_songs = []
        for song in songs:
            song_metadata = music_tag.load_file(song)
            artist = song_metadata["artist"]
            list_of_songs.append(
                SongData(
                    title=str(song_metadata["title"]),
                    artist=artist.values,
                    duration=str(song_metadata["#length"]),
                    videoId=Path(song).stem,
                    thumbnail=song_metadata["artwork"].first.thumbnail([128, 128]),
                    album=str(song_metadata["album"]),
                    path=Path(song),
                )
            )
        return list_of_songs

    def query(self, query: str, filter: str) -> list[SearchResult]:
        """Query the YTMusic API for a song

        Args:
            query (str): the query to search for
            filter (str): the filter to use

        Returns:
            list[SearchSongResult | SearchVideoResult]: the list of the results found
        """

        result = self.ytm.search(query, filter)

        self.dict_of_song_result.clear()
        for song in result:
            self.dict_of_song_result[song.videoId] = song
        return result

    def play_from_ytb(self, video_id: str) -> None:
        """Play a song from the YTMusic API, it will download the song first then play it

        Args:
            video_id (int): the video id of the song to play
        """
        song = self.dict_of_song_result[video_id]
        path = self.downloader.download(song)
        if path is None:
            return
        # BUG: dont re-fetch the songs but add it to the list
        self.list_of_downloaded_songs = self.get_downloaded_songs()
        self.music_player.load_song(str(path))
        self.music_player.play_song()
        self.media_control.on_playback()

    def play_from_list(self, id: int) -> None:
        """Play a song from the list of downloaded songs

        Args:
            id (int): the index of the song to play

        Raises:
            TypeError: If id is not an integer
        """
        if not isinstance(id, int):
            raise TypeError(f"id must be an integer, not {type(id)}")
        self.current_song_index = id
        self.current_song = self.list_of_downloaded_songs[id]
        self.music_player.load_song(self.list_of_downloaded_songs[id].path)
        self.music_player.play_song()
        self.media_control.on_playback()

    def previous(self) -> int:
        """Play the previous song"""
        if self.current_song_index == 0:
            self.current_song_index = len(self.list_of_downloaded_songs) - 1
        else:
            self.current_song_index -= 1
        self.music_player.load_song(
            self.list_of_downloaded_songs[self.current_song_index].path
        )
        self.music_player.play_song()
        self.media_control.on_playback()
        return self.current_song_index

    def next(self) -> int:
        """Play the next song"""
        if self.current_song_index == len(self.list_of_downloaded_songs) - 1:
            self.current_song_index = 0
        else:
            self.current_song_index += 1
        self.current_song = self.list_of_downloaded_songs[self.current_song_index]
        self.music_player.load_song(
            self.list_of_downloaded_songs[self.current_song_index].path
        )
        self.music_player.play_song()
        self.media_control.on_playback()
        return self.current_song_index

    def seek(self, seconds: float | int = 10) -> None:
        """Seek forward or backward

        Args:
            time (float, optional): The time to seek in seconds. Defaults to 10.

        Raises:
            TypeError: If seconds is not an integer or a float
        """
        if not isinstance(seconds, (int, float)):
            raise TypeError(
                f"Seconds must be an integer or a float, not {type(seconds)}"
            )
        self.music_player.position += seconds

    def suffle(self) -> None:
        """Shuffle the list of downloaded songs"""
        shuffle(self.list_of_downloaded_songs)
        if self.current_song is not None:
            self.current_song_index = self.list_of_downloaded_songs.index(
                self.current_song
            )
        else:
            self.current_song_index = 0
            self.current_song = self.list_of_downloaded_songs[self.current_song_index]

    def loop_at_end(self) -> bool:
        """Loop at the end"""
        self.music_player.loop_at_end = not self.music_player.loop_at_end
        self.setting.loop = self.music_player.loop_at_end
        return self.music_player.loop_at_end

    def check_if_song_ended(self) -> None:
        """Check if the song has ended and play the next song or loop it"""
        if self.music_player.loop_at_end:
            return
        if self.music_player.position == 0 and not self.music_player.playing:
            self.next()

    def stop(self) -> None:
        self.music_player.unload_song()

    @property
    def song_length(self) -> float:
        """Get the song length"""
        return self.music_player.song_length

    @property
    def position(self) -> float:
        """Get the current position"""
        return self.music_player.position

    def volume(self, value: float) -> None:
        """Get the volume up"""
        self.music_player.volume += value
        self.media_control.on_volume()
        self.setting.volume = self.music_player.volume

    @property
    def playing(self) -> bool:
        """Get the playing status"""
        return self.music_player.playing

    def pause_song(self) -> None:
        """Pause the song"""
        self.music_player.pause_song()
        self.media_control.on_playpause()

    def resume_song(self) -> None:
        """Resume the song"""
        self.music_player.resume_song()
        self.media_control.on_playpause()
