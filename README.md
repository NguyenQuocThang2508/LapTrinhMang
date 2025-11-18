# game_multiplayer

This repository is a minimal skeleton for a multiplayer game with separate client and server code.

Structure
```
client/ - client code and assets
server/ - server code
shared/ - protocol and shared constants
tests/  - pytest tests
```

Quick start (Unix bash / WSL / Git Bash on Windows)

1. Create a virtualenv and install the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the server:

```bash
python server/main.py
```

3. Run the client (in another terminal):

```bash
python client/main.py
```

Run tests:

```bash
pytest -q
```

Notes
- Files in `client/assets` are placeholders and should be replaced with real images, sounds and fonts.
- The networking code is a simple scaffold using length-prefixed JSON; for production prefer async or a robust protocol.

Windows / Git Bash notes

- If you run scripts directly (for example `python server/main.py`), Python's import search path may not include the project root and you can see "ModuleNotFoundError" for `client`, `server` or `shared`.
- Recommended ways to run from the project root (works on Windows Git Bash / WSL / Linux):

```bash
# start server from project root
cd /d/LTM/game_multiplayer
python -m server.main

# in another terminal, start client
cd /d/LTM/game_multiplayer
python -m client.main

# run tests (module mode ensures correct import path)
cd /d/LTM/game_multiplayer
python -m pytest -q

# or set PYTHONPATH explicitly when invoking pytest
cd /d/LTM/game_multiplayer
PYTHONPATH=. pytest -q
```

These approaches ensure the top-level `client`, `server`, and `shared` packages are discoverable during imports.
