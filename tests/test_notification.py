import pytest
from unittest.mock import patch
from api.notification_manager import NotificationManager


def test_send_notification_success():
    with patch("notifypy.Notify.send") as mock_notify:
        manager = NotificationManager()
        manager.send_notification("Test Title", "Test Message")
        mock_notify.assert_called_once()


def test_send_notification_invalid_title():
    manager = NotificationManager()
    with pytest.raises(TypeError):
        manager.send_notification(123, "Test Message")


def test_send_notification_invalid_message():
    manager = NotificationManager()
    with pytest.raises(TypeError):
        manager.send_notification("Test Title", 123)
