# pymusicterm

**pymusicterm** is a terminal-based music player that allows you to play your favorite songs directly from your terminal. 

## Features

- Play local music files.
- Download music from YouTube with `pytubefix` and `ytmusicapi`.
- Terminal-based interface powered by `textual`.
- Cross-platform support (Linux, macOS, Windows).
- MPRIS server integration for Linux to control playback with external tools.

## Installation

### Prerequisites
- Python 3.12 or higher.
- `ffmpeg` (required for `pydub` and audio processing).

You can install `pymusicterm` via pip:


Clone the repository:

```bash
git clone https://github.com/yourusername/pymusicterm.git
cd pymusicterm
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python -m pymusicterm
```

Make sure all dependencies are met, including `ffmpeg`.


### Basic Commands
- **Download from YouTube:** Search for a song or paste the URL.
- **Control playback:** Use keyboard shortcuts to play, pause, skip, or adjust volume.

## Configuration

The player reads a configuration file (`pymusicterm.toml`) for custom settings in the `~/.pymusicterm` directory.


## Dependencies

`pymusicterm` relies on the following libraries:

- [`just-playback`](https://pypi.org/project/just-playback/): Audio playback management.
- [`msgspec`](https://pypi.org/project/msgspec/): High-performance serialization.
- [`pydub`](https://pypi.org/project/pydub/): Audio processing.
- [`pytubefix`](https://pypi.org/project/pytubefix/): Simplified YouTube streaming.
- [`textual`](https://pypi.org/project/textual/): Terminal user interface framework.
- [`tomli-w`](https://pypi.org/project/tomli-w/): TOML configuration management.
- [`ytmusicapi`](https://pypi.org/project/ytmusicapi/): YouTube Music API integration.
- [`loguru`](https://pypi.org/project/loguru/): Advanced logging.
- [`mpris-server`](https://pypi.org/project/mpris-server/): MPRIS integration (Linux-only).

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request with a detailed explanation of changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Enjoy your music in the terminal with **pymusicterm**!

