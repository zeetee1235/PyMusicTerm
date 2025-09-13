from datetime import timedelta


def format_time(seconds: float) -> str:
    """
    Format the time to a string (ex: 90s -> 01:30).

    Args:
        seconds (int | float): The time in secondes

    Raises:
        TypeError: If the type of the seconds is not int or float

    Returns:
        str: The string representation of the time

    """
    if not isinstance(seconds, int | float):
        msg: str = (
            f"Invalid type for time for {type(seconds)}, please use int or float",
        )

        raise TypeError(msg)
    if isinstance(seconds, float):
        seconds = int(seconds)
    seconds = max(seconds, 0)
    return str(timedelta(seconds=seconds)).removeprefix("0:").removeprefix("0")


def seconds_to_string(seconds: int) -> str:
    minutes: int = seconds // 60
    secs: int = seconds % 60
    return f"{minutes:02}:{secs:02}"


def string_to_seconds(time_str: str) -> int:
    minutes, secs = map(int, time_str.split(":"))
    return minutes * 60 + secs
