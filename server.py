# RUN THIS FILE AND GO TO LOCALHOST:8000 to use the app
from textual_serve.server import Server

# TODO MAKE IT COMPATIBLE WITH WINDOWS AND GLOBAL INSTALLATION

server = Server(
    ".venv/bin/python src/main.py",
)

if __name__ == "__main__":
    server.serve()
