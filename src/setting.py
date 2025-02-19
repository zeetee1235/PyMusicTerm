from dataclasses import dataclass
from pathlib import Path
from msgspec import toml
import os

HOME = Path.home()
APP_DIR = Path(HOME / ".pymusicterm")
MUSIC_DIR = Path(APP_DIR / "musics")
SETTING_FILE = Path(APP_DIR / "setting.toml")
PLAYLIST_DIR = Path(APP_DIR / "playlists")
LYRICS_DIR = Path(APP_DIR / "lyrics")
LOG_DIR = Path(APP_DIR / "logs")


@dataclass
class Setting:
    """All the settings of the app"""

    volume: float = 1.0
    loop: bool = False
    app_dir: str = str(APP_DIR)
    music_dir: str = str(MUSIC_DIR)
    setting_file: str = str(SETTING_FILE)
    playlist_dir: str = str(PLAYLIST_DIR)
    lyrics_dir: str = str(LYRICS_DIR)
    log_dir: str = str(LOG_DIR)


@dataclass
class KeyBinding:
    """All the keybindings of the app"""

    volume_up: str = "k"
    volume_down: str = "j"
    seek_back: str = "q"
    seek_forward: str = "d"
    play_pause: str = "s"


class SettingLoader(Setting):
    def __init__(self):
        self.check_path()
        self._setting = self.load_setting()

    def check_path(self) -> None:
        """Check all the path and create it if needed"""
        if not APP_DIR.exists():
            APP_DIR.mkdir()

        if not MUSIC_DIR.exists():
            MUSIC_DIR.mkdir()

        if not SETTING_FILE.exists():
            self.save_setting(Setting())

        if not PLAYLIST_DIR.exists():
            PLAYLIST_DIR.mkdir()

        if not LYRICS_DIR.exists():
            LYRICS_DIR.mkdir()

        if not LOG_DIR.exists():
            LOG_DIR.mkdir()

    @property
    def setting(self) -> Setting:
        return self._setting

    @setting.setter
    def setting(self, setting: Setting) -> None:
        self._setting = setting
        self.save_setting(setting)

    def load_setting(self) -> Setting:
        """Load the setting.toml file from the app diretory path and decode it

        Returns:
            Setting: The setting object with all the data
        """
        with open(SETTING_FILE, "rb") as f:
            setting = toml.decode(f.read(), type=Setting)
        return setting

    def save_setting(self, setting: Setting) -> None:
        """Save the settings on the setting.toml file

        Args:
            setting (Setting): The setting object you want to save on disk
        """
        with open(SETTING_FILE, "wb") as f:
            encoded = toml.encode(setting)
            f.write(encoded)


def rename_console(name: str) -> None:
    """Rename the console

    Args:
        name (str): The new name of the console
    """
    if os.name == "nt":
        os.system(f"title {name}")
    else:
        print(f"\33]0;{name}\a", end="", flush=True)


if __name__ == "__main__":
    load_setting = SettingLoader()
    print(load_setting.setting)
    load_setting.setting = Setting(volume=0.5, loop=True)
    print(load_setting.setting.volume)
