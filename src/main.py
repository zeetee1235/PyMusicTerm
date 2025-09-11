import asyncio
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import requests_cache
from loguru import logger
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    MarkdownViewer,
    ProgressBar,
    Rule,
    Select,
    TabbedContent,
    TabPane,
)
from textual_image.widget import Image as WidgetImage

from api.protocols import SongData
from player.player import PyMusicTermPlayer
from player.util import format_time
from setting import SettingManager, rename_console

if TYPE_CHECKING:
    from textual.widget import Widget

    from player.media_control import MediaControlMPRIS, MediaControlWin32

# TODO @Zachvfx: rendre plus maintenable le code existnant en refactorisant
# TODO : renomer les fonctions pour qu'elles soient plus explicites, et pareil pour les id et classes des widgets
# TODO : ajouter des tests unitaires
# TODO : améliorer le queuing systeme
# TODO : ajouter des raccourcis clavier modifiables
# TODO : AJOUTER Type validation (raise error) --- 50%
# TODO : ajouter des logs messages


class PyMusicTerm(App):
    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        ("q", "seek_back", "Seek backward"),
        ("s", "play", "Play/Pause"),
        ("space", "play", "Play/Pause"),
        ("d", "seek_forward", "Seek forward"),
        ("r", "shuffle", "Shuffle"),
        ("l", "loop", "Loop at the end"),
        ("a", "previous", "Previous song"),
        ("e", "next", "Next song"),
        ("&", "return_on_search_tab", "Go to the search tab"),
        ("é", "return_on_playlist_tab", "Go to the playlist tab"),
        ('"', "return_on_lyrics_tab", "Go to the lyrics tab"),
        ("j", "volume(-0.01)", "Volume down"),
        ("k", "volume(0.01)", "Volume up"),
    ]

    def __init__(self, setting: SettingManager) -> None:
        super().__init__(css_path="pymusicterm.tcss", watch_css=True)
        self.setting: SettingManager = setting
        rename_console("PyMusicTerm")

        logger.remove()
        logger.add(
            Path(self.setting.log_dir + "/pymusicterm.log"),
            format="{time} {level} {message}",
            level="INFO",
            rotation="500 MB",
        )
        self.timer: Widget | None = None

        if self.setting.os == "win32":
            from player.media_control import MediaControlWin32 as MediaControl
        else:
            from player.media_control import MediaControlMPRIS as MediaControl
        requests_cache.install_cache(
            f"{self.setting.cache_dir}/cache",
            expire_after=timedelta(hours=1),
        )

        self.media_control: MediaControlMPRIS | MediaControlWin32 = MediaControl()
        self.player = PyMusicTermPlayer(self.setting, self.media_control)
        self.media_control.init(self.player)

    def compose(self) -> ComposeResult:
        with TabbedContent(classes="search_tabs", id="tabbed_content"):
            with TabPane("Search", id="search"):  # noqa: SIM117
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
                    yield ListView(id="search_results")
            with TabPane("Playlist", id="playlist"):  # noqa: SIM117
                with Vertical():
                    yield Input(placeholder="Search for a song", id="playlist_input")
                    yield ListView(id="playlist_results")
            with TabPane("Lyrics", id="lyrics"):  # noqa: SIM117
                with Vertical():
                    yield Input(placeholder="Search for a song", id="lyrics_input")
                    yield MarkdownViewer(
                        markdown="No lyrics now",
                        id="lyrics_results",
                        show_table_of_contents=False,
                    )
        yield Rule()
        with Vertical(classes="info_controls"):
            with Center():
                yield Label(
                    "Unknown Title",
                    id="label_current_song_title",
                    markup=False,
                )
            with Center():
                yield Label(
                    "Unknown Artist",
                    id="label_current_song_artist",
                    markup=False,
                )
        with Horizontal(classes="status_controls"):
            yield Label(
                "--:--",
                id="label_current_song_position",
                classes="control_label",
            )
            yield ProgressBar(
                total=100,
                show_eta=False,
                show_percentage=False,
                id="player_status",
            )
            yield Label("--:--", id="label_song_length", classes="control_label")
        with Horizontal(classes="player_controls"):
            yield Button("󰼨", id="previous")
            yield Button("󰐊", id="play_pause")
            yield Button("󰼧", id="next")
        with Horizontal(classes="player_controls"):
            yield Button("󰒟", id="shuffle")
            yield Button("󰛤", id="loop")

    @on(TabbedContent.TabActivated)
    async def action_select_playlist_tab(
        self,
        event: TabbedContent.TabActivated | None,
    ) -> None:
        """
        Action when the tab is activated. If the tab is playlist, clear the options and add the songs to the playlist.
        """
        playlist_results: ListView = self.query_one("#playlist_results")
        if event is None or event.tab.id.endswith("playlist"):
            children_id: list[str] = [
                child.id.removeprefix("id-") for child in playlist_results.children
            ]
            for song in self.player.list_of_downloaded_songs:
                if song.video_id not in children_id:
                    await playlist_results.append(await self._create_song_item(song))

    async def update_time(self) -> None:
        """Update the time label of the player, and update the player."""
        button: Button = self.query_one("#play_pause")
        if self.player.playing:
            button.label = "󰏤"
        else:
            button.label = "󰐊"
        progress_bar: ProgressBar = self.query_one("#player_status")
        label_current_song_position: Label = self.query_one(
            "#label_current_song_position",
        )
        label_song_length: Label = self.query_one("#label_song_length")
        length_float: float = self.player.song_length
        current_float: float = self.player.position
        label_current_song_position.update(format_time(current_float))
        label_song_length.update(format_time(length_float))
        if self.player.playing:
            label_current_song_title: Label = self.query_one(
                "#label_current_song_title",
            )
            label_current_song_artist: Label = self.query_one(
                "#label_current_song_artist",
            )
            label_current_song_title.update(
                self.player.list_of_downloaded_songs[
                    self.player.current_song_index
                ].title,
            )
            label_current_song_artist.update(
                self.player.list_of_downloaded_songs[
                    self.player.current_song_index
                ].get_formatted_artists(),
            )
        try:
            percentage: float = current_float / length_float
        except ZeroDivisionError:
            percentage = 0.01
        progress_bar.update(
            progress=percentage * 100,
        )
        if self.player.check_if_song_ended():
            await self.action_next()

    async def action_return_on_search_tab(self) -> None:
        """Set the search tab as the active tab."""
        tab: TabbedContent = self.query_one("#tabbed_content")
        tab.active = "search"

    async def action_return_on_playlist_tab(self) -> None:
        """Set the playlist tab as the active tab."""
        tab: TabbedContent = self.query_one("#tabbed_content")
        tab.active = "playlist"

    async def action_return_on_lyrics_tab(self) -> None:
        """Set the lyrics tab as the active tab."""
        tab: TabbedContent = self.query_one("#tabbed_content")
        tab.active = "lyrics"

    @on(ListView.Selected, "#playlist_results")
    async def select_playlist_result(self, event: ListView.Selected) -> None:
        """Select a song from the playlist results and play it."""
        id_: str = event.item.id.removeprefix("id-")
        await self.play_from_id(id_)

    async def play_from_id(self, ids: str) -> None:
        """
        Play a song from the playlist results and play it.

        Args:
            ids (str): The id of the song to play

        """
        for i, song in enumerate(self.player.list_of_downloaded_songs):
            if song.video_id == ids:
                self.player.play_from_list(i)
                await self.toggle_button()

    @on(ListView.Selected, "#search_results")
    async def select_result(self, event: ListView.Selected) -> None:
        """Select a song from the search results and play it."""
        video_id: str = str(event.item.id).removeprefix("id-")
        self.player.play_from_ytb(video_id)
        await self.toggle_button()

    @on(Button.Pressed, "#previous")
    async def action_previous(self) -> None:
        """Play the previous song."""
        await self.toggle_button()
        playlist_results: ListView = self.query_one("#playlist_results")
        playlist_results.index = self.player.previous()

    @on(Button.Pressed, "#play_pause")
    async def action_play(self) -> None:
        """Play or pause the song."""
        if self.player.playing:
            self.player.pause_song()
        else:
            self.player.resume_song()
        await self.toggle_button()

    async def toggle_button(self) -> None:
        """Toggle the play button label and start the timer if it's not running."""
        button: Button = self.query_one("#play_pause")
        if self.player.playing:
            button.label = "󰏤"
        else:
            button.label = "󰐊"
        if self.timer is None:
            self.timer = self.set_interval(
                0.1,
                self.update_time,
                name="update_time",
            )

    @on(Button.Pressed, "#next")
    async def action_next(self) -> None:
        """Play the next song."""
        self.toggle_button()
        playlist_results: ListView = self.query_one("#playlist_results")
        playlist_results.index = self.player.next()

    @on(Button.Pressed, "#shuffle")
    async def action_shuffle(self) -> None:
        """Shuffle the list of downloaded songs."""
        playlist_results: ListView = self.query_one("#playlist_results")
        await playlist_results.clear()

        self.player.suffle()
        await self.action_select_playlist_tab(None)

    @on(Button.Pressed, "#loop")
    async def action_loop(self) -> None:
        """Toggle the loop button."""
        loop_button: Button = self.query_one("#loop")
        is_looping = self.player.loop_at_end()
        if is_looping:
            loop_button.variant = "success"
        else:
            loop_button.variant = "default"

    @on(Input.Submitted, "#search_input")
    async def search(self) -> None:
        """Search asynchronously on YTMusic."""
        search_results: ListView = self.query_one("#search_results")
        await search_results.clear()
        search_input: Input = self.query_one("#search_input")
        if search_input.value == "":
            return
        search_results.loading = True
        filters: Select = self.query_one("#search_sort")
        results: list[SongData] = self.player.query(
            search_input.value,
            filters.value,
        )
        search_results: ListView = self.query_one("#search_results")
        await search_results.clear()
        for result in results:
            search_results.append(await self._create_song_item(result))
        search_results.loading = False

    async def _create_song_item(self, song: SongData) -> ListItem:
        """
        Create a song item for the search results.

        Args:
            song (SearchResult): The song to create the item for

        Returns:
            ListItem: The song item

        """
        return ListItem(
            Horizontal(
                WidgetImage(song.thumbnail, classes="image"),
                Vertical(
                    Label(
                        song.title,
                        classes="title",
                        markup=False,
                    ),
                    Label(
                        song.get_formatted_artists(),
                        markup=False,
                        classes="artist",
                    ),
                ),
                Label(
                    song.album,
                    markup=False,
                    classes="album",
                ),
                Label(
                    song.duration,
                    markup=False,
                    classes="length",
                ),
            ),
            id=f"id-{song.video_id}",
            classes="song_item",
        )

    async def action_seek_back(self) -> None:
        """Seek backward 10 seconds."""
        self.player.seek(-10)

    async def action_seek_forward(self) -> None:
        """Seek forward 10 seconds."""
        self.player.seek(10)

    async def action_volume(self, volume: float) -> None:
        """Increase the volume."""
        self.player.volume(volume)
        self.notify(f"Volume changed to {self.player.music_player.volume:.2f}")


@logger.catch
async def main() -> None:
    setting = SettingManager()
    app = PyMusicTerm(setting)
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
