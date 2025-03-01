import pytest
from unittest.mock import MagicMock
from main import PyMusicTerm, format_time
from setting import SettingManager
from textual.widgets import (
    Input,
    Button,
    OptionList,
    TabbedContent,
    Label,
    TabPane,
    Rule,
    Select,
    MarkdownViewer,
    ProgressBar,
)


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


def test_action_shuffle(app: PyMusicTerm):
    app.player.suffle = MagicMock()
    app.action_shuffle()
    app.player.suffle.assert_called_once()


@pytest.mark.asyncio
async def test_play_pause_button(app: PyMusicTerm):
    """Test pressing keys has the desired result."""
    async with app.run_test() as pilot:
        await pilot.click("#play_pause")
        assert app.player.playing is False
        await pilot.click("#play_pause")
        assert app.player.playing is False


def test_action_seek_back(app: PyMusicTerm):
    """Test if the seek back action works as expected."""
    app.player.seek = MagicMock()
    app.action_seek_back()
    app.player.seek.assert_called_once_with(-10)


def test_action_seek_forward(app: PyMusicTerm):
    """Test if the seek forward action works as expected."""
    app.player.seek = MagicMock()
    app.action_seek_forward()
    app.player.seek.assert_called_once_with(10)


def test_action_volume(app: PyMusicTerm):
    """test if the volume action works as expected."""
    app.player.volume = MagicMock()
    app.action_volume(0.1)
    app.player.volume.assert_called_once_with(0.1)
