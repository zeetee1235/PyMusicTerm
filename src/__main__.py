import subprocess
from setting import Setting

if __name__ == "__main__":
    setting = Setting()
    subprocess.run(
        [
            "c:/Users/Zach/PycharmProjects/PyMusicTerm/.venv/Scripts/python.exe",
            "c:/Users/Zach/PycharmProjects/PyMusicTerm/src/main.py",
        ],
        shell=True,
    )
