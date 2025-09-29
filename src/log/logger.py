"""
Incredible ressources for logging from mCoding (https://www.youtube.com/watch?v=9L77QExPmI0)
https://github.com/mCodingLLC/VideosSampleCode/blob/master/videos/135_modern_logging/mylogger.py
"""

import atexit
import datetime as dt
import json
import logging
from logging.config import dictConfig
from pathlib import Path
from typing import Any, override

LOG_RECORD_BUILTIN_ATTRS: set[str] = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.fmt_keys: dict[str, str] = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message: dict[str, str | Any] = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, str | Any]:
        always_fields: dict[str, str] = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created,
                tz=dt.UTC,
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message: dict[str, str | Any] = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val  # noqa: PERF403

        return message


def setup_logging(log_dir: str) -> None:
    config_file: Path = Path(
        Path(__file__).parent / "logging_config.json",
    )
    with config_file.open() as f_in:
        config: dict[str, Any] = json.load(f_in)
    log_file_path: Path = Path(log_dir) / "pymusicterm.log.jsonl"
    config["handlers"]["file_json"]["filename"] = str(log_file_path)

    dictConfig(config)
    queue_handler: logging.Handler | None = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
