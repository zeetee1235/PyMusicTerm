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
