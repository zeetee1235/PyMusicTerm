from dataclasses import dataclass
from pathlib import Path
from msgspec import toml
import os
import http.client as httplib
import sys

HOME = Path.home()
APP_DIR = Path(HOME / ".pymusicterm")
MUSIC_DIR = Path(APP_DIR / "musics")
SETTING_FILE = Path(APP_DIR / "setting.toml")
PLAYLIST_DIR = Path(APP_DIR / "playlists")
LYRICS_DIR = Path(APP_DIR / "lyrics")
LOG_DIR = Path(APP_DIR / "logs")


def fetch_files_from_folder(folder_path: str, ending: str = "mp3") -> list[str | None]:
    """Fetch all the files from a folder
    Args:
        folder_path (str): The path of the folder
        ending (str): The ending of the files to fetch. Defaults to "mp3"
    Returns:
        list[str]: The list of file found
    """
    if not isinstance(folder_path, str):
        raise TypeError(f"folder_path must be a string, not {type(folder_path)}")
    if not isinstance(ending, str):
        raise TypeError(f"ending must be a string, not {type(ending)}")
    return [str(file) for file in Path(folder_path).glob(f"*.{ending}")]


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


@dataclass
class Setting:
    """All the settings of the app"""

    volume: float = 1.0
    loop: bool = False
    os: str = sys.platform
    app_dir: str = str(APP_DIR)
    music_dir: str = str(MUSIC_DIR)
    setting_file: str = str(SETTING_FILE)
    playlist_dir: str = str(PLAYLIST_DIR)
    lyrics_dir: str = str(LYRICS_DIR)
    log_dir: str = str(LOG_DIR)


class SettingManager:
    """Manages the settings of the app."""

    def __init__(self):
        self._setting = None
        self.check_and_create_paths()
        self._setting = self.load_setting()

    @property
    def os(self) -> str:
        return self._setting.os

    @os.setter
    def os(self, value: str) -> None:
        self._setting.os = value
        self.save_setting()

    @property
    def volume(self) -> float:
        return self._setting.volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._setting.volume = round(value, 3)
        self.save_setting()

    @property
    def loop(self) -> bool:
        return self._setting.loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._setting.loop = value
        self.save_setting()

    @property
    def app_dir(self) -> str:
        return self._setting.app_dir

    @property
    def music_dir(self) -> str:
        return self._setting.music_dir

    @property
    def setting_file(self) -> str:
        return self._setting.setting_file

    @property
    def playlist_dir(self) -> str:
        return self._setting.playlist_dir

    @property
    def lyrics_dir(self) -> str:
        return self._setting.lyrics_dir

    @property
    def log_dir(self) -> str:
        return self._setting.log_dir

    def load_setting(self) -> Setting:
        """Load settings from the setting.toml file."""
        if not SETTING_FILE.exists():
            self._setting = Setting()
            self.save_setting()

        try:
            with open(SETTING_FILE, "rb") as f:
                return toml.decode(f.read(), type=Setting)
        except Exception as e:
            priapp_dirnt(f"Error loading settings: {e}")
            return Setting()

    def save_setting(self) -> None:
        """Save the current settings to the setting.toml file."""
        try:
            with open(SETTING_FILE, "wb") as f:
                encoded = toml.encode(self._setting)
                f.write(encoded)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def check_and_create_paths(self) -> None:
        """Check and create necessary directories and files."""
        APP_DIR.mkdir(exist_ok=True)
        MUSIC_DIR.mkdir(exist_ok=True)
        PLAYLIST_DIR.mkdir(exist_ok=True)
        LYRICS_DIR.mkdir(exist_ok=True)
        LOG_DIR.mkdir(exist_ok=True)


@dataclass
class KeyBinding:
    """All the keybindings of the app"""

    volume_up: str = "k"
    volume_down: str = "j"
    seek_back: str = "q"
    seek_forward: str = "d"
    play_pause: str = "s"


def rename_console(name: str, platform: str = sys.platform) -> None:
    """Rename the console

    Args:
        name (str): The new name of the console (for linux and windows)
    """
    if not isinstance(name, str):
        raise TypeError(f"name must be a string, not {type(name)}")
    if platform not in ("win32", "linux"):
        raise ValueError(f"platform must be 'win32' or 'linux', not {platform}")
    if platform == "win32":
        os.system(f"title {name}")
    else:
        print(f"\33]0;{name}\a", end="", flush=True)


'''def have_internet() -> bool:
    """Check if the user has internet connection"""
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        with conn.request("HEAD", "/"):
            return True
    except Exception:
        return False
'''
