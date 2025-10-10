import logging
from pathlib import Path
from typing import Protocol

logger: logging.Logger = logging.getLogger(__name__)

try:
    from jnius import PythonJavaClass, autoclass, cast, java_method

    JNIUS_AVAILABLE = True
except ImportError:
    JNIUS_AVAILABLE = False
    logger.warning("pyjnius not available - Android notifications disabled")


class MediaControl(Protocol):
    def init(self, player) -> None: ...
    def on_playback(self) -> None: ...
    def on_playpause(self) -> None: ...
    def on_volume(self) -> None: ...
    def populate_playlist(self) -> None: ...
    def set_current_song(self, index: int) -> None: ...


if JNIUS_AVAILABLE:
    # Import Android Java classes
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
    except:
        # Fallback for non-Kivy apps
        try:
            PythonActivity = autoclass("org.renpy.android.PythonActivity")
        except:
            PythonActivity = None

    Context = autoclass("android.content.Context")
    Intent = autoclass("android.content.Intent")
    PendingIntent = autoclass("android.app.PendingIntent")
    BroadcastReceiver = autoclass("android.content.BroadcastReceiver")
    IntentFilter = autoclass("android.content.IntentFilter")
    NotificationManager = autoclass("android.app.NotificationManager")
    NotificationCompat = autoclass("androidx.core.app.NotificationCompat")
    NotificationChannel = autoclass("android.app.NotificationChannel")
    BitmapFactory = autoclass("android.graphics.BitmapFactory")
    MediaSessionCompat = autoclass("androidx.media.session.MediaSessionCompat")
    PlaybackStateCompat = autoclass("androidx.media.session.PlaybackStateCompat")
    MediaMetadataCompat = autoclass("androidx.media.session.MediaMetadataCompat")

    try:
        MediaStyle = autoclass("androidx.media.app.NotificationCompat$MediaStyle")
    except:
        MediaStyle = autoclass(
            "android.support.v4.media.app.NotificationCompat$MediaStyle",
        )

    # Android resources
    AndroidString = autoclass("android.R$string")
    AndroidDrawable = autoclass("android.R$drawable")


class MediaButtonReceiver(PythonJavaClass if JNIUS_AVAILABLE else object):
    """BroadcastReceiver for handling media button clicks"""

    __javainterfaces__ = ["android/content/BroadcastReceiver"]
    __javacontext__ = "app"

    def __init__(self, notification_handler):
        super().__init__()
        self.notification_handler = notification_handler

    @java_method("(Landroid/content/Context;Landroid/content/Intent;)V")
    def onReceive(self, context, intent):
        """Handle broadcast intents from notification buttons"""
        action = intent.getAction()
        logger.info(f"Received action: {action}")

        if not self.notification_handler.player:
            return

        player = self.notification_handler.player

        if action == "ACTION_PLAY":
            player.resume_song()
            self.notification_handler.on_playpause()
        elif action == "ACTION_PAUSE":
            player.pause_song()
            self.notification_handler.on_playpause()
        elif action == "ACTION_NEXT":
            player.next()
            self.notification_handler.on_playback()
        elif action == "ACTION_PREVIOUS":
            player.previous()
            self.notification_handler.on_playback()
        elif action == "ACTION_STOP":
            player.stop()
            self.notification_handler.hide_notification()


class AndroidMediaNotification:
    """Android Media Notification with playback controls using Pyjnius"""

    NOTIFICATION_ID = 1001
    CHANNEL_ID = "pymusicterm_media"

    def __init__(self):
        if not JNIUS_AVAILABLE:
            raise ImportError("pyjnius is required for Android notifications")

        if not PythonActivity:
            raise RuntimeError(
                "Cannot find PythonActivity - are you running in a proper Android app?",
            )

        self.player = None
        self.activity = PythonActivity.mActivity
        self.context = self.activity.getApplicationContext()

        # Get notification manager
        self.notification_manager = cast(
            "android.app.NotificationManager",
            self.context.getSystemService(Context.NOTIFICATION_SERVICE),
        )

        # Create notification channel (Android 8.0+)
        self._create_notification_channel()

        # Create media session
        self.media_session = MediaSessionCompat(self.context, "PyMusicTerm")
        self.media_session.setActive(True)

        # Setup broadcast receiver for button clicks
        self.receiver = MediaButtonReceiver(self)
        self._setup_broadcast_receiver()

        logger.info("Android media notification initialized")

    def _create_notification_channel(self):
        """Create notification channel for Android O+"""
        try:
            channel = NotificationChannel(
                self.CHANNEL_ID,
                "Music Playback",
                NotificationManager.IMPORTANCE_LOW,
            )
            channel.setDescription("Controls for music playback")
            channel.setShowBadge(False)
            channel.setSound(None, None)
            channel.enableVibration(False)

            self.notification_manager.createNotificationChannel(channel)
            logger.info("Notification channel created")
        except Exception as e:
            logger.error(f"Failed to create notification channel: {e}")

    def _setup_broadcast_receiver(self):
        """Register broadcast receiver for media button actions"""
        try:
            intent_filter = IntentFilter()
            intent_filter.addAction("ACTION_PLAY")
            intent_filter.addAction("ACTION_PAUSE")
            intent_filter.addAction("ACTION_NEXT")
            intent_filter.addAction("ACTION_PREVIOUS")
            intent_filter.addAction("ACTION_STOP")

            self.context.registerReceiver(self.receiver, intent_filter)
            logger.info("Broadcast receiver registered")
        except Exception as e:
            logger.error(f"Failed to register broadcast receiver: {e}")

    def _create_pending_intent(self, action: str) -> "PendingIntent":
        """Create pending intent for button actions"""
        try:
            intent = Intent(action)
            intent.setPackage(self.context.getPackageName())

            # Use FLAG_IMMUTABLE for Android 12+
            flags = PendingIntent.FLAG_UPDATE_CURRENT
            try:
                flags |= PendingIntent.FLAG_IMMUTABLE
            except AttributeError:
                pass  # FLAG_IMMUTABLE not available on older Android

            return PendingIntent.getBroadcast(
                self.context,
                hash(action) % 2147483647,
                intent,
                flags,
            )
        except Exception as e:
            logger.error(f"Failed to create pending intent for {action}: {e}")
            return None

    def _load_bitmap(self, image_path: str):
        """Load bitmap from file path"""
        try:
            if not Path(image_path).exists():
                return None

            bitmap = BitmapFactory.decodeFile(str(image_path))
            return bitmap
        except Exception as e:
            logger.error(f"Failed to load bitmap: {e}")
            return None

    def show_notification(
        self,
        title: str,
        artist: str,
        album: str,
        image_path: str = None,
        is_playing: bool = True,
    ):
        """Show or update media notification"""
        try:
            # Build notification
            builder = NotificationCompat.Builder(self.context, self.CHANNEL_ID)

            # Get app icon
            app_info = self.context.getApplicationInfo()
            builder.setSmallIcon(app_info.icon)

            # Set content
            builder.setContentTitle(title)
            builder.setContentText(artist)
            builder.setSubText(album)

            # Load album art
            if image_path:
                bitmap = self._load_bitmap(image_path)
                if bitmap:
                    builder.setLargeIcon(bitmap)

            # Create pending intents for buttons
            prev_intent = self._create_pending_intent("ACTION_PREVIOUS")
            play_pause_intent = self._create_pending_intent(
                "ACTION_PAUSE" if is_playing else "ACTION_PLAY",
            )
            next_intent = self._create_pending_intent("ACTION_NEXT")

            # Add action buttons
            if prev_intent:
                builder.addAction(
                    AndroidDrawable.ic_media_previous,
                    "Previous",
                    prev_intent,
                )

            if play_pause_intent:
                icon = (
                    AndroidDrawable.ic_media_pause
                    if is_playing
                    else AndroidDrawable.ic_media_play
                )
                label = "Pause" if is_playing else "Play"
                builder.addAction(icon, label, play_pause_intent)

            if next_intent:
                builder.addAction(
                    AndroidDrawable.ic_media_next,
                    "Next",
                    next_intent,
                )

            # Apply media style
            try:
                media_style = MediaStyle()
                media_style.setMediaSession(self.media_session.getSessionToken())
                media_style.setShowActionsInCompactView(0, 1, 2)
                builder.setStyle(media_style)
            except Exception as e:
                logger.warning(f"Could not apply media style: {e}")

            # Configure notification behavior
            builder.setOngoing(is_playing)
            builder.setShowWhen(False)
            builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            builder.setPriority(NotificationCompat.PRIORITY_HIGH)
            builder.setCategory(NotificationCompat.CATEGORY_TRANSPORT)

            # Set delete intent (when user swipes away)
            stop_intent = self._create_pending_intent("ACTION_STOP")
            if stop_intent:
                builder.setDeleteIntent(stop_intent)

            # Build and show notification
            notification = builder.build()
            self.notification_manager.notify(self.NOTIFICATION_ID, notification)

            # Update media session metadata
            self._update_media_session(title, artist, album, is_playing)

            logger.info(f"Notification shown: {title} - {artist}")

        except Exception as e:
            logger.error(f"Failed to show notification: {e}", exc_info=True)

    def _update_media_session(
        self,
        title: str,
        artist: str,
        album: str,
        is_playing: bool,
    ):
        """Update MediaSession metadata and playback state"""
        try:
            # Update metadata
            metadata_builder = MediaMetadataCompat.Builder()
            metadata_builder.putString(MediaMetadataCompat.METADATA_KEY_TITLE, title)
            metadata_builder.putString(MediaMetadataCompat.METADATA_KEY_ARTIST, artist)
            metadata_builder.putString(MediaMetadataCompat.METADATA_KEY_ALBUM, album)
            self.media_session.setMetadata(metadata_builder.build())

            # Update playback state
            state = (
                PlaybackStateCompat.STATE_PLAYING
                if is_playing
                else PlaybackStateCompat.STATE_PAUSED
            )

            playback_builder = PlaybackStateCompat.Builder()
            playback_builder.setState(
                state,
                PlaybackStateCompat.PLAYBACK_POSITION_UNKNOWN,
                1.0,
            )
            playback_builder.setActions(
                PlaybackStateCompat.ACTION_PLAY
                | PlaybackStateCompat.ACTION_PAUSE
                | PlaybackStateCompat.ACTION_SKIP_TO_NEXT
                | PlaybackStateCompat.ACTION_SKIP_TO_PREVIOUS
                | PlaybackStateCompat.ACTION_STOP,
            )

            self.media_session.setPlaybackState(playback_builder.build())

        except Exception as e:
            logger.error(f"Failed to update media session: {e}")

    def hide_notification(self):
        """Hide the notification"""
        try:
            self.notification_manager.cancel(self.NOTIFICATION_ID)
            self.media_session.setActive(False)
            logger.info("Notification hidden")
        except Exception as e:
            logger.error(f"Failed to hide notification: {e}")

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.hide_notification()
            self.context.unregisterReceiver(self.receiver)
            self.media_session.release()
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")


class MediaControlAndroid(MediaControl):
    """Android media notification control - drop-in replacement"""

    def __init__(self):
        try:
            self.notification = AndroidMediaNotification()
            logger.info("Android media notification (pyjnius) initialized")
        except Exception as e:
            logger.error(
                f"Failed to initialize Android notifications: {e}",
                exc_info=True,
            )
            self.notification = None

    def init(self, player) -> None:
        """Initialize with player instance"""
        if self.notification:
            self.notification.player = player
            self.on_playback()

    def on_playback(self) -> None:
        """Called when track changes"""
        if not self.notification or not self.notification.player:
            return

        try:
            player = self.notification.player
            song = player.list_of_downloaded_songs[player.current_song_index]

            # Find album art
            cover_path = song.path.parent / f"{song.video_id}_cover.png"
            if not cover_path.exists():
                cover_path = None

            self.notification.show_notification(
                title=song.title,
                artist=song.get_formatted_artists(),
                album=song.album,
                image_path=str(cover_path) if cover_path else None,
                is_playing=player.playing,
            )
        except Exception as e:
            logger.error(
                f"Failed to update notification on playback: {e}",
                exc_info=True,
            )

    def on_playpause(self) -> None:
        """Called when play/pause state changes"""
        self.on_playback()

    def on_volume(self) -> None:
        """Called when volume changes"""

    def populate_playlist(self) -> None:
        """Populate playlist (not needed for Android)"""

    def set_current_song(self, index: int) -> None:
        """Set current song"""
        self.on_playback()

    def __del__(self):
        """Cleanup on destruction"""
        if self.notification:
            self.notification.cleanup()
