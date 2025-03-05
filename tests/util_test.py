from pathlib import Path


class Cleaner:
    def __init__(self, test_path: Path):
        self.test_path = test_path

    def __enter__(self):
        self._delete_file()

    def __exit__(self, *args):
        self._delete_file()

    def _delete_file(self):
        for file in Path(self.test_path).iterdir():
            file.unlink()
