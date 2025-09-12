# pymusicterm
**pymusicterm** is a terminal-based music player that allows you to play your favorite songs directly from your terminal. 

## Features
- Play offline music.
- Download music from YouTube and Youtube Music.
- Terminal-based interface.
- Cross-platform support (Linux, macOS, Windows).
- MPRIS server integration for Linux and MACOS to control playback with external tools.
- STMC integration for Windows to control playback with windows.

## Images


### Important
The song are in the `~/.pymusicterm/musics` folder with specific name, tags and covers. 

## Installation with uv
```bash	
pip install uv
git clone https://github.com/ZachVFXX/PyMusicTerm.git
cd PyMusicTerm
uv sync #or pip install the dependencies
```

### Prerequisites
- Python 3.12 (tested) or higher.
- `ffmpeg` (required for `pydub` and audio processing).
- On linux, install PyObject for mpris

### Basic Commands
- **Download from YouTube:** Search for a song or paste the URL.
- **Control playback:** Use keyboard shortcuts to play, pause, skip, or adjust volume.

## Configuration

The player reads a configuration file (`setting.toml`) for custom settings in the `~/.pymusicterm` directory.

## Dependencies

`pymusicterm` relies on the following libraries:

- [`just-playback`](https://pypi.org/project/just-playback/): Audio playback management.
- [`msgspec`](https://pypi.org/project/msgspec/): High-performance serialization.
- [`pydub`](https://pypi.org/project/pydub/): Audio processing.
- [`pytubefix`](https://pypi.org/project/pytubefix/): Simplified YouTube streaming.
- [`textual`](https://pypi.org/project/textual/): Terminal user interface framework.
- [`textual-image`](https://pypi.org/project/textual-image/): Terminal image display.
- [`ytmusicapi`](https://pypi.org/project/ytmusicapi/): YouTube Music API integration.
- [`mpris-server`](https://pypi.org/project/mpris-server/): MPRIS integration (Linux and macos only).
- [`winrt-windows project`](https://github.com/pywinrt/pywinrt): Windows Media Controller.
- [`music-tag`](https://pypi.org/project/music-tag/): Music metadata

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request with a detailed explanation of changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---