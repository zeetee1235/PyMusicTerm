from pathlib import Path
from api.ytmusic import SearchResult, YTMusic
from api.player import MusicPlayer
from api.downloader import Downloader
from setting import SettingLoader
from api.local import fetch_lyrics_from_folder, fetch_songs_from_folder
from random import shuffle
from api.lyrics import LyricsDownloader


class PyMusicTermPlayer:
    def __init__(self, setting: SettingLoader):
        self.setting = setting
        lyrics = LyricsDownloader(self.setting.lyrics_dir)
        self.ytm = YTMusic(lyrics)
        self.player = MusicPlayer()
        self.downloader = Downloader(self.setting.music_dir)
        self.list_of_downloaded_songs: list[str] = fetch_songs_from_folder(
            self.setting.music_dir
        )
        self.list_of_lyrics: dict[str, str] = self.map_lyrics_to_song()
        self.dict_of_song_result: dict[str, SearchResult] = {}
        self.current_song_index = 0

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
        """Play a song from the list of results

        Args:
            id (int): the index of the song to play
        """
        song = self.dict_of_song_result[video_id]
        path = self.downloader.download(song)
        self.ytm.get_lyrics(song)
        self.list_of_downloaded_songs = fetch_songs_from_folder(self.setting.music_dir)
        self.list_of_lyrics = self.map_lyrics_to_song()
        self.player.load_song(str(path))
        self.player.play_song()

    def play_from_list(self, id: int) -> None:
        """Play a song from the list of downloaded songs

        Args:
            id (int): the index of the song to play
        """
        self.current_song_index = id
        self.list_of_downloaded_songs = fetch_songs_from_folder(self.setting.music_dir)
        self.list_of_lyrics = self.map_lyrics_to_song()
        self.player.load_song(self.list_of_downloaded_songs[id])
        self.player.play_song()

    def previous(self) -> None:
        """Play the previous song"""
        if self.current_song_index == 0:
            self.current_song_index = len(self.list_of_downloaded_songs) - 1
        else:
            self.current_song_index -= 1
        self.player.load_song(self.list_of_downloaded_songs[self.current_song_index])
        self.player.play_song()

    def next(self) -> None:
        """Play the next song"""
        if self.current_song_index == len(self.list_of_downloaded_songs) - 1:
            self.current_song_index = 0
        else:
            self.current_song_index += 1
        self.player.load_song(self.list_of_downloaded_songs[self.current_song_index])
        self.player.play_song()

    def seek_forward(self) -> None:
        """Seek forward"""
        self.player.position += 10

    def seek_back(self) -> None:
        """Seek backward"""
        self.player.position -= 10

    def suffle(self) -> None:
        """Shuffle the list of downloaded songs"""
        shuffle(self.list_of_downloaded_songs)

    def loop_at_end(self) -> bool:
        """Loop at the end"""
        self.player.loop_at_end = not self.player.loop_at_end
        return self.player.loop_at_end

    def update(self) -> None:
        """Update the player"""
        if self.player.loop_at_end:
            return
        if self.player.position == 0 and not self.player.playing:
            self.next()

    def map_lyrics_to_song(self) -> None:
        """Map the lyrics to the songs"""
        list_of_lyrics: dict[str, str] = {}
        for song in fetch_songs_from_folder(self.setting.music_dir):
            for lyric in fetch_lyrics_from_folder(self.setting.lyrics_dir):
                if Path(song).stem.removesuffix(".mp3") == Path(
                    lyric
                ).stem.removesuffix(".md"):
                    list_of_lyrics[song] = Path(lyric)
                else:
                    list_of_lyrics[song] = None
        return list_of_lyrics

    @property
    def song_length(self) -> float:
        """Get the song length"""
        return self.player.song_length

    @property
    def position(self) -> float:
        """Get the current position"""
        return self.player.position

    def volume_up(self) -> None:
        """Get the volume up"""
        self.player.volume += 0.1

    def volume_down(self) -> None:
        """Get the volume down"""
        self.player.volume -= 0.1

    @property
    def playing(self) -> bool:
        """Get the playing status"""
        return self.player.playing

    def pause_song(self) -> None:
        """Pause the song"""
        self.player.pause_song()

    def resume_song(self) -> None:
        """Resume the song"""
        self.player.resume_song()
