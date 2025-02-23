from notifypy import Notify
from notifypy.exceptions import NotificationFailure, InvalidIconPath
from pathlib import Path


class NotificationManager:
    def __init__(self, app_name: str = "PyMusicTerm") -> None:
        self.notification = Notify(default_notification_application_name=app_name)
        try:
            path = Path("/home/zach/Dev/PyMusicTerm/src/assets/icon.png").resolve()
            print(path)
            self.notification.icon = path
        except InvalidIconPath as e:
            print(f"Notification failed with error: {e}")

    def send_notification(self, title: str, message: str):
        try:
            self.notification.title = title
            self.notification.message = message
            self.notification.send(block=False)
        except NotificationFailure as e:
            print(f"Notification failed with error: {e}")
