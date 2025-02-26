from glob import glob


def fetch_songs_from_folder(folder_path: str) -> list[str | None]:
    """Fetch all the songs from a folder
    Args:
        folder_path (str): The path of the folder
    Returns:
        list[Song]: The list of songs found
    """
    if not isinstance(folder_path, str):
        raise TypeError(f"folder_path must be a string, not {type(folder_path)}")
    songs = []
    for file in glob(f"{folder_path}/*.mp3"):
        songs.append(file)
    return songs


def fetch_lyrics_from_folder(folder_path: str) -> list[str | None]:
    """Fetch all the lyrics from a folder
    Args:
        folder_path (str): The path of the folder
    Returns:
        list[str]: The list of lyrics found
    """
    if not isinstance(folder_path, str):
        raise TypeError(f"folder_path must be a string, not {type(folder_path)}")
    lyrics = []
    for file in glob(f"{folder_path}/*.md"):
        lyrics.append(file)
    return lyrics


if __name__ == "__main__":
    pass
