from api.ytmusic import YTMusic, SearchSongResult
from api.player import MusicPlayer
from api.downloader import Downloader
from setting import SettingLoader
from api.local import fetch_songs_from_folder
from random import shuffle


class PyMusicTermPlayer:
    def __init__(self):
        self.setting = SettingLoader().setting

        self.ytm = YTMusic()
        self.player = MusicPlayer()
        self.downloader = Downloader(self.setting.music_dir)
        self.list_of_downloaded_songs: list[str] = fetch_songs_from_folder(
            self.setting.music_dir
        )
        self.dict_of_song_result: dict[str, SearchSongResult] = {}
        self.current_song_index = 0

    def query(self, query: str) -> list[SearchSongResult]:
        """Query the YTMusic API for a song

        Args:
            query (str): the query to search for

        Returns:
            list[SearchSongResult]: the list of the results found
        """
        result = self.ytm.search(query)

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
        self.list_of_downloaded_songs = fetch_songs_from_folder(self.setting.music_dir)
        self.player.load_song(str(path))
        self.player.play_song()

    def play_from_list(self, id: int) -> None:
        """Play a song from the list of downloaded songs

        Args:
            id (int): the index of the song to play
        """
        self.current_song_index = id
        self.list_of_downloaded_songs = fetch_songs_from_folder(self.setting.music_dir)
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
