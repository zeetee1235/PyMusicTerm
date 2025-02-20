from pymusicterm.api.ytmusic import SongData
from pymusicterm.player.player import PyMusicTermPlayer
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import (
    Input,
    Button,
    OptionList,
    TabbedContent,
    Label,
    TabPane,
    Rule,
    Select,
    Footer,
    MarkdownViewer,
    ProgressBar,
    Switch,
)
from textual.widgets.option_list import Option
from textual.containers import Horizontal, Vertical
from textual import on
from textual.reactive import reactive
from pathlib import Path
from datetime import timedelta
from textual import work
from textual.worker import get_current_worker
from loguru import logger
import sys

if sys.platform == "win32":
    from pymusicterm.player.media_control import MediaControlWin32 as MediaControl
else:
    from pymusicterm.player.media_control import MediaControlMPRIS as MediaControl
from pymusicterm.setting import SettingManager, rename_console


def format_time(time: float) -> str:
    """Format the time to a string"""
    return str(timedelta(seconds=int(time))).removeprefix("0:")


class PyMusicTerm(App):
    BINDINGS = [
        ("q", "seek_back", "Seek backward"),
        ("s", "play", "Play/Pause"),
        ("d", "seek_forward", "Seek forward"),
        ("r", "shuffle", "Shuffle"),
        ("l", "loop", "Loop at the end"),
        ("&", "return_on_search_tab", "Go to the search tab"),
        ("é", "return_on_playlist_tab", "Go to the playlist tab"),
        ("k", "volume(0.1)", "Volume up"),
        ("j", "volume(-0.1)", "Volume down"),
    ]

    def __init__(self) -> None:
        super().__init__(css_path="pymusicterm.tcss")

        self.setting = SettingManager()
        rename_console("PyMusicTerm")
        logger.remove()
        logger.add(
            Path(self.setting.log_dir + "/pymusicterm.log"),
            format="{time} {level} {message}",
            level="INFO",
        )
        self.timer: Widget | None = None
        self.media_control = MediaControl()
        self.player = PyMusicTermPlayer(self.setting, self.media_control)
        self.media_control.init(self.player)

    def compose(self) -> ComposeResult:
        yield Footer()
        with TabbedContent(classes="search_tabs", id="tabbed_content"):
            with TabPane("Search", id="search"):
                with Vertical():
                    yield Input(placeholder="Search for a song", id="search_input")
                    yield Select(
                        id="search_sort",
                        options=[
                            ("Songs (default: Stream Youtube Music)", "songs"),
                            ("Video (Stream Youtube Video)", "videos"),
                        ],
                        allow_blank=False,
                    )
                    yield OptionList(id="search_results")
            with TabPane("Playlist", id="playlist"):
                with Vertical():
                    yield Input(placeholder="Search for a song", id="playlist_input")
                    yield OptionList(id="playlist_results")
            with TabPane("Lyrics", id="lyrics"):
                with Vertical():
                    yield Input(placeholder="Search for a song", id="lyrics_input")
                    yield MarkdownViewer(
                        markdown="No lyrics now",
                        id="lyrics_results",
                        show_table_of_contents=False,
                    )
        yield Rule()
        with Horizontal(classes="status_controls"):
            yield Label(
                "--:--", id="label_current_song_position", classes="control_label"
            )
            yield ProgressBar(
                total=100, show_eta=False, show_percentage=False, id="player_status"
            )
            yield Label("--:--", id="label_song_length", classes="control_label")
        with Horizontal(classes="player_controls"):
            yield Button("Previous", id="previous")
            yield Button("Play", id="play_pause")
            yield Button("Next", id="next")
        with Horizontal(classes="player_controls"):
            yield Button("Shuffle", id="shuffle")
            yield Button("Loop", id="loop")

    @on(TabbedContent.TabActivated)
    def action_select_playlist_tab(self, event: TabbedContent.TabActivated) -> None:
        """Action when the tab is activated. If the tab is playlist, clear the options and add the songs to the playlist.

        Args:
            event (TabbedContent.TabActivated): The event that triggered the action
        """
        playlist_results: OptionList = self.query_one("#playlist_results")
        if event.tab.id.endswith("playlist"):
            playlist_results.clear_options()
            for i, song in enumerate(self.player.list_of_downloaded_songs):
                playlist_results.add_option(
                    Option(
                        f"{i + 1}. {Path(song).stem}",
                        id=i,
                    )
                )
            return

    def update_time(self) -> None:
        """Update the time label of the player, and update the player"""
        progress_bar: ProgressBar = self.query_one("#player_status")
        label_current_song_position: Label = self.query_one(
            "#label_current_song_position"
        )
        label_song_length: Label = self.query_one("#label_song_length")
        length_float = self.player.song_length
        current_float = self.player.position
        label_current_song_position.update(format_time(current_float))
        label_song_length.update(format_time(length_float))
        percentage = current_float / length_float
        progress_bar.update(
            progress=percentage * 100,
        )
        self.player.update()
        lyrics_results: MarkdownViewer = self.query_one("#lyrics_results")
        if not self.player.playing:
            return
        current_lyric = self.player.dict_of_lyrics[
            self.player.list_of_downloaded_songs[self.player.current_song_index]
        ]
        logger.warning(current_lyric)
        logger.warning(self.player.dict_of_lyrics)
        logger.warning(
            self.player.list_of_downloaded_songs[self.player.current_song_index]
        )
        with open(current_lyric, "r", encoding="utf-8") as f:
            lyrics_results.document.update(f.read())

    def action_return_on_search_tab(self):
        """Set the search tab as the active tab"""
        tab: TabbedContent = self.query_one("#tabbed_content")
        tab.active = "search"

    def action_return_on_playlist_tab(self):
        """Set the playlist tab as the active tab"""
        tab: TabbedContent = self.query_one("#tabbed_content")
        tab.active = "playlist"

    @on(OptionList.OptionSelected, "#playlist_results")
    def select_playlist_result(self, event: OptionList.OptionSelected) -> None:
        """Select a song from the playlist results and play it"""
        id = int(event.option.id)
        self.player.play_from_list(id)
        self.toggle_button()

    @on(OptionList.OptionSelected, "#search_results")
    def select_result(self, event: OptionList.OptionSelected) -> None:
        """Select a song from the search results and play it"""
        video_id = str(event.option.id)
        self.player.play_from_ytb(video_id)
        self.toggle_button()

    @on(Button.Pressed, "#previous")
    def action_previous(self) -> None:
        """Play the previous song"""
        self.player.previous()

    @on(Button.Pressed, "#play_pause")
    def action_play(self) -> None:
        """Play or pause the song"""
        if self.player.playing:
            self.player.pause_song()
        else:
            self.player.resume_song()
        self.toggle_button()

    def toggle_button(self) -> None:
        """Toggle the play button label and start the timer if it's not running"""
        button: Button = self.query_one("#play_pause")
        if self.player.playing:
            button.label = "Pause"
        else:
            button.label = "Play"
        if self.timer is None:
            self.timer = self.set_interval(1, self.update_time, name="update_time")

    @on(Button.Pressed, "#next")
    def action_next(self) -> None:
        """Play the next song"""
        self.player.next()

    @on(Button.Pressed, "#shuffle")
    def action_shuffle(self) -> None:
        """Shuffle the list of downloaded songs"""
        self.player.suffle()

    @on(Button.Pressed, "#loop")
    def action_loop(self) -> None:
        """Toggle the loop button"""
        loop_button: Button = self.query_one("#loop")
        is_looping = self.player.loop_at_end()
        if is_looping:
            loop_button.variant = "success"
        else:
            loop_button.variant = "default"

    @on(Input.Submitted, "#search_input")
    def search(self) -> None:
        """Search for a song on YTMusic and display the results"""
        search_input: Input = self.query_one("#search_input")
        if search_input.value == "":
            return
        search_input.loading = True
        self.search_ytb_thread(search_input.value)

    @work(exclusive=True, thread=True)
    def search_ytb_thread(self, query: str) -> None:
        """Start a thread to search for a song on YTMusic

        Args:
            query (str): The search query
        """
        worker = get_current_worker()
        filter: Select = self.query_one("#search_sort")
        results = self.player.query(query, filter.value)
        if not worker.is_cancelled:
            self.call_from_thread(self.update_search_results, results)

    def update_search_results(self, results: list[SongData]) -> None:
        """Update the search results

        Args:
            results (list): The list of results from youtube music
        """
        search_results: OptionList = self.query_one("#search_results")
        search_input: Input = self.query_one("#search_input")
        search_results.clear_options()
        for i, result in enumerate(results):
            search_results.add_option(
                Option(
                    f"{i + 1}. {result.title} - {result.get_formatted_artists()}",
                    result.videoId,
                )
            )
        search_input.loading = False

    def action_seek_back(self) -> None:
        """Seek backward 10 seconds"""
        self.player.seek(-10)

    def action_seek_forward(self) -> None:
        """Seek forward 10 seconds"""
        self.player.seek(10)

    def action_volume(self, value: float) -> None:
        """Increase the volume"""
        self.player.volume(value)


def main():
    app = PyMusicTerm()
    app.run()


if __name__ == "__main__":
    main()
