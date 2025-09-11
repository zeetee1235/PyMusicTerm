from pathlib import Path

import pytest
from util_test import Cleaner

from api.downloader import Downloader, _convert_to_mp3, _delete_file, _download_from_yt


class MockSongData:
    title = "Test Song"
    duration = "3:30"
    video_id = "C0DPdy98e4c"

    def get_formatted_artists(self) -> str:
        return "Test Artist"


BASE_PATH = Path(__file__).parent / "tmp"


@pytest.fixture
def downloader():
    return Downloader(download_path=BASE_PATH)


def test_downloader_downloading_file(downloader):
    with Cleaner(BASE_PATH):
        song = MockSongData()
        song_path = (
            Path(BASE_PATH) / f"{song.title} - {song.get_formatted_artists()}.mp3"
        )
        result = downloader.download(song)
        assert result == str(song_path)
        assert Path(result).exists()


def test_delete_file():
    with Cleaner(BASE_PATH):
        path = BASE_PATH / "Test Song - Test Artist.m4a"
        Path(path).touch()  # Create the file to simulate it exists

        _delete_file(path)
        assert not Path(path).exists()


def test_song_already_downloaded(downloader):
    with Cleaner(BASE_PATH):
        song = MockSongData()
        song_path = (
            Path(BASE_PATH) / f"{song.title} - {song.get_formatted_artists()}.mp3"
        )
        song_path.touch()  # Create the file to simulate it exists
        result = downloader.download(song)
        assert result == str(song_path)
        assert Path(result).exists()


def test_download_failed_return_none():
    with Cleaner(BASE_PATH):
        song = MockSongData()
        song.video_id = "invalid"
        result = _download_from_yt(song, BASE_PATH)
        assert result is None


def test_downloader_failed_return_none(downloader):
    with Cleaner(BASE_PATH):
        song = MockSongData()
        song.video_id = "invalid"
        result = downloader.download(song)
        assert result is None


def test_download_from_yt():
    with Cleaner(BASE_PATH):
        song = MockSongData()
        song_path = _download_from_yt(song, BASE_PATH)
        assert Path(song_path).exists()
        assert Path(song_path).suffix == ".m4a"
        assert (
            Path(song_path).name == f"{song.title} - {song.get_formatted_artists()}.m4a"
        )


def test_convert_to_mp3():
    with Cleaner(BASE_PATH):
        song = MockSongData()
        song_path = _download_from_yt(song, BASE_PATH)
        mp3_path = _convert_to_mp3(song_path)
        assert Path(mp3_path).exists()
        assert Path(mp3_path).suffix == ".mp3"
        assert (
            Path(mp3_path).name == f"{song.title} - {song.get_formatted_artists()}.mp3"
        )


def test_convert_to_mp3_type_error():
    with pytest.raises(TypeError):
        _convert_to_mp3(90)
