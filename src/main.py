from player.player import PyMusicTermPlayer
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
    LoadingIndicator,
)
from textual.widgets.option_list import Option
from textual.containers import Horizontal, Vertical
from textual import on
from pathlib import Path
from datetime import timedelta
from textual import work
from textual.worker import get_current_worker


class PyMusicTerm(App):
    BINDINGS = [
        ("q", "seek_back", "Seek backward"),
        ("s", "play", "Play/Pause"),
        ("d", "seek_forward", "Seek forward"),
        ("r", "shuffle", "Shuffle"),
        ("l", "loop", "Loop at the end"),
        ("a", "return_on_search_tab", "Go to the search tab"),
        ("e", "return_on_playlist_tab", "Go to the playlist tab"),
    ]

    def __init__(self) -> None:
        super().__init__(css_path="pymusicterm.tcss")

        self.player = PyMusicTermPlayer()
        self.timer: Widget | None = None

    def compose(self) -> ComposeResult:
        with TabbedContent(classes="search_tabs", id="tabbed_content"):
            with TabPane("Search", id="search"):
                with Vertical():
                    yield Input(placeholder="Search for a song", id="search_input")
                    yield OptionList(id="search_results")
            with TabPane("Playlist", id="playlist"):
                with Vertical():
                    yield Input(placeholder="Search for a song", id="playlist_input")
                    yield OptionList(id="playlist_results")
        yield Rule()
        with Horizontal(classes="status_controls"):
            yield Label(id="player_status")
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
                        f"{Path(song).stem}",
                        id=i,
                    )
                )
            return

    def update_time(self) -> None:
        """Update the time label of the player, and update the player"""
        status: Label = self.query_one("#player_status")
        length = self.player.player.song_length()
        current = self.player.player.position
        current = str(timedelta(seconds=int(current)))
        length = str(timedelta(seconds=int(length)))
        status.update(f"{current}/{length}")
        self.player.update()

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
        if self.player.player.playing:
            self.player.player.pause_song()
        else:
            self.player.player.resume_song()
        self.toggle_button()

    def toggle_button(self) -> None:
        """Toggle the play button label and start the timer if it's not running"""
        button: Button = self.query_one("#play_pause")
        if self.player.player.playing:
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
        results = self.player.query(query)
        if not worker.is_cancelled:
            self.call_from_thread(self.update_search_results, results)

    def update_search_results(self, results: list) -> None:
        """Update the search results

        Args:
            results (list): The list of results from youtube music
        """
        search_results: OptionList = self.query_one("#search_results")
        search_input: Input = self.query_one("#search_input")
        search_results.clear_options()
        for result in results:
            search_results.add_option(
                Option(
                    f"{result.title} - {result.get_formatted_artists()} - {result.album} | {result.duration}",
                    result.videoId,
                )
            )
        search_input.loading = False

    def action_seek_back(self) -> None:
        """Seek backward 10 seconds"""
        self.player.seek_back()

    def action_seek_forward(self) -> None:
        """Seek forward 10 seconds"""
        self.player.seek_forward()


def main():
    app = PyMusicTerm()
    app.run()


if __name__ == "__main__":
    main()
