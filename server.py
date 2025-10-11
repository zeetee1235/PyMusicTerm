from textual_serve.server import Server

# TODO MAKE IT COMPATIBLE WITH WINDOWS AND GLOBAL INSTALLATION

server = Server(
    ".venv/bin/python src/main.py",
)
server.serve()
