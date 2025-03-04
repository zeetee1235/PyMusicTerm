import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from api.downloader import Downloader, _convert_to_mp3, _download_from_yt, _delete_file
from api.notification_manager import NotificationManager


class MockSongData:
    title = "Test Song"
    duration = "3:30"
    videoId = "C0DPdy98e4c"

    def get_formatted_artists(self) -> str:
        return "Test Artist"


BASE_PATH = Path(__file__).parent / "tmp"


@pytest.fixture
def downloader():
    return Downloader(download_path=BASE_PATH)


def delete_tmp_files():
    for file in BASE_PATH.iterdir():
        file.unlink()


def test_downloader_downloading_file(downloader):
    delete_tmp_files()
    song = MockSongData()
    song_path = Path(BASE_PATH) / f"{song.title} - {song.get_formatted_artists()}.mp3"
    result = downloader.download(song)
    assert result == str(song_path)


def test_delete_file():
    delete_tmp_files()
    path = BASE_PATH / "Test Song - Test Artist.m4a"
    Path(path).touch()  # Create the file to simulate it exists

    _delete_file(path)
    assert not Path(path).exists()


def test_song_already_downloaded(downloader):
    delete_tmp_files()
    song = MockSongData()
    song_path = Path(BASE_PATH) / f"{song.title} - {song.get_formatted_artists()}.mp3"
    song_path.touch()  # Create the file to simulate it exists
    result = downloader.download(song)
    assert result == str(song_path)


def test_download_failed_return_none():
    delete_tmp_files()
    song = MockSongData()
    song.videoId = "invalid"
    result = _download_from_yt(song, BASE_PATH)
    assert result is None


def test_downloader_failed_return_none(downloader):
    delete_tmp_files()
    song = MockSongData()
    song.videoId = "invalid"
    result = downloader.download(song)
    assert result is None


def test_download_from_yt():
    delete_tmp_files()
    song = MockSongData()
    song_path = _download_from_yt(song, BASE_PATH)
    assert Path(song_path).exists()
    assert Path(song_path).suffix == ".m4a"
    assert Path(song_path).name == f"{song.title} - {song.get_formatted_artists()}.m4a"


def test_convert_to_mp3():
    delete_tmp_files()
    song = MockSongData()
    song_path = _download_from_yt(song, BASE_PATH)
    mp3_path = _convert_to_mp3(song_path)
    assert Path(mp3_path).exists()
    assert Path(mp3_path).suffix == ".mp3"
    assert Path(mp3_path).name == f"{song.title} - {song.get_formatted_artists()}.mp3"


def test_convert_to_mp3_type_error():
    with pytest.raises(TypeError):
        _convert_to_mp3(90)  # Pass an integer instead of a string
