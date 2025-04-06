from datetime import timedelta


def format_time(seconds: int | float) -> str:
    """Format the time to a string (ex: 90s -> 01:30)

    Args:
        seconds (int | float): The time in secondes

    Raises:
        TypeError: If the type of the seconds is not int or float

    Returns:
        str: The string representation of the time
    """
    if not isinstance(seconds, (int, float)):
        raise TypeError(
            f"Invalid type for time for {type(seconds)}, please use int or float"
        )
    if isinstance(seconds, float):
        seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    seconds = str(timedelta(seconds=seconds)).removeprefix("0:").removeprefix("0")
    return seconds
