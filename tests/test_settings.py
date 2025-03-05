import sys
from unittest.mock import MagicMock
from setting import (
    APP_DIR,
    PLAYLIST_DIR,
    LYRICS_DIR,
    LOG_DIR,
    MUSIC_DIR,
    SETTING_FILE,
    SettingManager,
    rename_console,
    fetch_files_from_folder,
    Setting,
)
import pytest
from pathlib import Path
import uuid
from util_test import Cleaner

BASE_PATH = Path(__file__).parent / "tmp"


def test_rename_console_name_error():
    with pytest.raises(TypeError):
        rename_console(90)


def test_rename_console_platform_error():
    with pytest.raises(ValueError):
        rename_console("name", 90)


def test_rename_console():
    rename_console("name", "win32")
    rename_console("name", "linux")
    assert True


def test_fetch_files_from_folder_path_error():
    with pytest.raises(TypeError):
        fetch_files_from_folder(90)


def test_fetch_files_from_folder_ending_error():
    with pytest.raises(TypeError):
        fetch_files_from_folder("path", 90)


def test_fetch_files_from_folder():
    with Cleaner(BASE_PATH):
        file_names = [str(Path(BASE_PATH) / f"{uuid.uuid4()}.txt") for _ in range(10)]
        for file_name in file_names:
            Path(file_name).touch()

        files = fetch_files_from_folder(str(BASE_PATH), "txt")
        assert len(files) == 10
        assert all([file in file_names for file in files])


def test_setting_initialization():
    setting = Setting()
    assert setting.volume == 1.0
    assert setting.loop is False
    assert setting.os == sys.platform
    assert setting.app_dir == str(APP_DIR)
    assert setting.music_dir == str(MUSIC_DIR)
    assert setting.setting_file == str(SETTING_FILE)
    assert setting.playlist_dir == str(PLAYLIST_DIR)
    assert setting.lyrics_dir == str(LYRICS_DIR)
    assert setting.log_dir == str(LOG_DIR)


def test_setting_manager_load_save():
    setting_manager = SettingManager()
    setting_manager.volume = 0.5
    setting_manager.loop = True
    setting_manager.os = "test_os"

    loaded_setting = setting_manager.load_setting()
    assert loaded_setting.volume == 0.5
    assert loaded_setting.loop is True
    assert loaded_setting.os == "test_os"

    setting_manager.volume = 1.0
    setting_manager.loop = False
    setting_manager.os = sys.platform
    setting_manager.save_setting()

    loaded_setting = setting_manager.load_setting()
    assert loaded_setting.volume == 1.0
    assert loaded_setting.loop is False
    assert loaded_setting.os == sys.platform
