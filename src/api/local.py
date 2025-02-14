from glob import glob


def fetch_songs_from_folder(folder_path: str) -> list[str] | None:
    """Fetch all the songs from a folder
    Args:
        folder_path (str): The path of the folder
    Returns:
        list[Song]: The list of songs found
    """
    songs = []
    for file in glob(f"{folder_path}/*.mp3"):
        songs.append(file)

    return songs


if __name__ == "__main__":
    pass
