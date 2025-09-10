import asyncio
from multiprocessing import Queue

from winrt._winrt_windows_media import (
    SystemMediaTransportControls,
    SystemMediaTransportControlsDisplayUpdater,
)
from winrt.windows.foundation import Uri
from winrt.windows.media import (
    SystemMediaTransportControlsButton,
)
from winrt.windows.media.core import MediaSource
from winrt.windows.media.playback import MediaPlaybackItem, MediaPlayer


def smtc_process(cmd_queue: Queue, event_queue: Queue) -> None:
    async def main() -> None:
        player = MediaPlayer()

        # Dummy media to initialize SMTC
        dummy_uri = Uri("file:///C:/Windows/Media/Windows Notify.wav")
        source: MediaSource = MediaSource.create_from_uri(dummy_uri)
        item = MediaPlaybackItem(source)
        player.source = item

        smtc: SystemMediaTransportControls = player.system_media_transport_controls
        smtc.is_play_enabled = True
        smtc.is_pause_enabled = True
        smtc.is_next_enabled = True
        smtc.is_previous_enabled = True

        display_updater: SystemMediaTransportControlsDisplayUpdater = (
            smtc.display_updater
        )
        display_updater.music_properties.title = "Idle"
        display_updater.music_properties.artist = "None"
        display_updater.update()

        # SMTC button callback
        def button_pressed(sender, args) -> None:
            if args.button == SystemMediaTransportControlsButton.PLAY:
                event_queue.put("play")
            elif args.button == SystemMediaTransportControlsButton.PAUSE:
                event_queue.put("pause")
            elif args.button == SystemMediaTransportControlsButton.NEXT:
                event_queue.put("next")
            elif args.button == SystemMediaTransportControlsButton.PREVIOUS:
                event_queue.put("previous")

        smtc.add_button_pressed(button_pressed)

        # Main loop
        while True:
            try:
                cmd = cmd_queue.get_nowait()
            except:
                cmd = None

            if cmd:
                action = cmd.get("action")
                if action == "update_metadata":
                    title = cmd.get("title", "Unknown")
                    artist = cmd.get("artist", "Unknown")
                    display_updater.music_properties.title = title
                    display_updater.music_properties.artist = artist
                    display_updater.update()
                elif action == "play":
                    player.play()
                elif action == "pause":
                    player.pause()
                elif action == "stop":
                    break
            await asyncio.sleep(0.1)

    asyncio.run(main())
