from notifypy import Notify
from notifypy.exceptions import NotificationFailure, InvalidIconPath
from pathlib import Path

from setting import resource_path


class NotificationManager:
    def __init__(self, app_name: str = "PyMusicTerm") -> None:
        self.notification = Notify(default_notification_application_name=app_name)
        try:
            path = Path(resource_path("assets/icon.png"))
            print(path)
            self.notification.icon = path
        except InvalidIconPath as e:
            print(f"Notification failed with error: {e}")

    def send_notification(self, title: str, message: str):
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, not {type(title)}")
        if not isinstance(message, str):
            raise TypeError(f"message must be a string, not {type(message)}")
        try:
            self.notification.title = title
            self.notification.message = message
            self.notification.send(block=False)
        except NotificationFailure as e:
            print(f"Notification failed with error: {e}")
