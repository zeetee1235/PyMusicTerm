import pytest
from unittest.mock import MagicMock
from main import PyMusicTerm, format_time
from setting import SettingManager


def test_format_time():
    assert format_time(90) == "01:30"
    assert format_time(3600) == "1:00:00"
    assert format_time(3661) == "1:01:01"
    assert format_time(0) == "00:00"
    with pytest.raises(TypeError):
        format_time("90")


@pytest.fixture
def app() -> PyMusicTerm:
    setting = SettingManager()
    app = PyMusicTerm(setting)
    return app


def test_app_initialization(app: PyMusicTerm):
    assert app.setting is not None
    assert app.player is not None
    assert app.media_control is not None


def test_action_return_on_search_tab(app: PyMusicTerm):
    app.action_return_on_search_tab()
    assert app.query_one("#tabbed_content").active == "search"


def test_action_return_on_playlist_tab(app: PyMusicTerm):
    app.action_return_on_playlist_tab()
    assert app.query_one("#tabbed_content").active == "playlist"


def test_action_play_pause(app: PyMusicTerm):
    app.player.playing = False
    app.action_play()
    assert app.player.playing is True
    app.action_play()
    assert app.player.playing is False


def test_action_next(app: PyMusicTerm):
    app.player.next = MagicMock()
    app.action_next()
    app.player.next.assert_called_once()


def test_action_previous(app: PyMusicTerm):
    app.player.previous = MagicMock()
    app.action_previous()
    app.player.previous.assert_called_once()


def test_action_shuffle(app: PyMusicTerm):
    app.player.suffle = MagicMock()
    app.action_shuffle()
    app.player.suffle.assert_called_once()


def test_action_loop(app: PyMusicTerm):
    app.player.loop_at_end = MagicMock(return_value=True)
    app.action_loop()
    assert app.query_one("#loop").variant == "success"
    app.player.loop_at_end = MagicMock(return_value=False)
    app.action_loop()
    assert app.query_one("#loop").variant == "default"


def test_action_seek_back(app: PyMusicTerm):
    app.player.seek = MagicMock()
    app.action_seek_back()
    app.player.seek.assert_called_once_with(-10)


def test_action_seek_forward(app: PyMusicTerm):
    app.player.seek = MagicMock()
    app.action_seek_forward()
    app.player.seek.assert_called_once_with(10)


def test_action_volume(app: PyMusicTerm):
    app.player.volume = MagicMock()
    app.action_volume(0.1)
    app.player.volume.assert_called_once_with(0.1)
