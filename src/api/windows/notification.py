from win11toast import notify, update_progress
import humanize


class Notification:
    def __init__(
        self, title: str, status: str, value: int, valueStringOverride: str
    ) -> None:
        notify(
            progress={
                "title": title,
                "status": status,
                "value": value,
                "valueStringOverride": valueStringOverride,
            },
        )

    def update_download_progress(self, value: int, total: int) -> None:
        update_progress(
            {
                "value": value / total,
                "valueStringOverride": f"{humanize.naturalsize(value)}/{humanize.naturalsize(total)}",
            }
        )

    def update_progress(self, value: int, total: int) -> None:
        update_progress(
            {
                "value": value / total,
                "valueStringOverride": f"{value}/{total}",
            }
        )

    def finish_download(self) -> None:
        update_progress({"status": "Completed!"})
