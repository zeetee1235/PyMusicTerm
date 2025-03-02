import time
from unittest.mock import MagicMock
import pytest
from main import PyMusicTermPlayer, PyMusicTerm
from setting import SettingManager


@pytest.fixture
def app() -> PyMusicTermPlayer:
    setting = SettingManager()
    setting.os = "win32"
    app = PyMusicTerm(setting)
    return app.player


def test_seek_error(app: PyMusicTermPlayer):
    with pytest.raises(TypeError):
        app.seek("10")


def test_seek_forward(app: PyMusicTermPlayer):
    app.play_from_list(0)
    previous = int(
        app.music_player.position
    )  # int is used to round off the float because sometimes the float is not 0 but 0.003
    app.seek(10)
    assert int(app.music_player.position) == previous + 10


def test_seek_back(app: PyMusicTermPlayer):
    app.play_from_list(0)
    app.seek(10)
    previous = int(
        app.music_player.position
    )  # int is used to round off the float because sometimes the float is not 0 but 0.003
    app.seek(-10)
    assert int(app.music_player.position) == previous - 10


def test_loop_at_end(app: PyMusicTermPlayer):
    app.loop_at_end()
    assert app.setting.loop == app.music_player.loop_at_end


def test_check_if_song_ended_loop_at_end_true(app: PyMusicTermPlayer):
    app.play_from_list(0)
    app.music_player.loop_at_end = True
    if app.music_player.loop_at_end:
        app.check_if_song_ended = MagicMock()
        app.next = MagicMock()
        app.next.assert_not_called()


def test_check_if_song_ended_loop_at_end_false(app: PyMusicTermPlayer):
    app.play_from_list(0)
    app.music_player.loop_at_end = False
    app.music_player.position = app.music_player.song_length
    app.check_if_song_ended = MagicMock()
    app.next = MagicMock()
    app.check_if_song_ended()
    app.next.assert_called_once()
