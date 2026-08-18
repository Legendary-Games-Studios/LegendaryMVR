import os
import re
import threading
import requests
import http.server
import socketserver
import webbrowser

# Must be set before kivy/SDL2 create the window - this controls the
# WM_CLASS hint that Linux taskbars/window switchers display, which is
# separate from the in-window title bar text.
os.environ["SDL_VIDEO_X11_WMCLASS"] = "LegendaryMVR"

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

# -----------------------
# MVR STRUCTURE
# -----------------------
BASE_DIR = "LegendaryMVR"
GAMES_DIR = os.path.join(BASE_DIR, "games")

os.makedirs(GAMES_DIR, exist_ok=True)

# -----------------------
# CONFIG
# -----------------------
GITHUB_REPO_API = "https://api.github.com/repos/Legendary-Games-Studios/Legendary-MVR-Apps/contents/"
PORT = 8000

# -----------------------
# SERVER
# -----------------------
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"MVR running at http://localhost:{PORT}")
        httpd.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# -----------------------
# PARSE VERSION
# "GameName_V1.0.html" -> ("GameName", 1, 0)
# Anything without a _V<major>.<minor> suffix is treated as version (0, 0)
# so any repo version will be considered newer than it.
#
# NOTE: name matching elsewhere uses EXACT equality on the parsed name,
# never substring checks. This matters because "parkour" and "parkour 2"
# are different games whose filenames both start with "parkour" -- a
# substring match would wrongly treat one as a copy of the other.
# -----------------------
def parse_game(file):
    match = re.match(r"^(.*)_V(\d+)\.(\d+)\.html$", file)
    if match:
        name = match.group(1)
        major = int(match.group(2))
        minor = int(match.group(3))
        return name, major, minor

    return file[:-5] if file.endswith(".html") else file, 0, 0

def version_str(major, minor):
    return f"v{major}.{minor}"

# -----------------------
# DOWNLOAD GAME
# -----------------------
def download_game(file_name):
    try:
        url = f"https://raw.githubusercontent.com/Legendary-Games-Studios/Legendary-MVR-Apps/main/{file_name}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        local_path = os.path.join(GAMES_DIR, file_name)

        with open(local_path, "wb") as f:
            f.write(r.content)

        print(f"Downloaded: {file_name}")
        return True

    except Exception as e:
        print("Download error:", e)
        return False

def delete_old_version(old_file_name):
    """Remove a superseded local file after a newer version has been installed."""
    try:
        old_path = os.path.join(GAMES_DIR, old_file_name)
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"Removed old version: {old_file_name}")
    except Exception as e:
        print("Delete error:", e)

# -----------------------
# HUB
# -----------------------
class LegendaryMVRHub(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=6, padding=6)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)

        # repo_games[name] = {"file": str, "major": int, "minor": int}
        self.repo_games = {}

        self.load_repo()
        self.load_local()

    # -----------------------
    # LOAD GITHUB
    # -----------------------
    def load_repo(self):
        try:
            r = requests.get(GITHUB_REPO_API, timeout=10)
            r.raise_for_status()
            data = r.json()

            if not isinstance(data, list):
                print("Repo error: unexpected response", data)
                return

            for item in data:
                if item.get("name", "").endswith(".html"):

                    name, major, minor = parse_game(item["name"])

                    if name not in self.repo_games:
                        self.repo_games[name] = {
                            "file": item["name"],
                            "major": major,
                            "minor": minor,
                        }
                    else:
                        cur = self.repo_games[name]
                        if (major, minor) > (cur["major"], cur["minor"]):
                            self.repo_games[name] = {
                                "file": item["name"],
                                "major": major,
                                "minor": minor,
                            }

        except Exception as e:
            print("Repo error:", e)

    # -----------------------
    # LOAD LOCAL
    # -----------------------
    def load_local(self):
        self.grid.clear_widgets()

        local_files = [
            f for f in os.listdir(GAMES_DIR)
            if f.endswith(".html")
        ]

        # Parse every local file once: name -> (file, major, minor)
        local_games = {}
        for file in local_files:
            name, major, minor = parse_game(file)
            local_games[name] = {"file": file, "major": major, "minor": minor}

        repo_names = set(self.repo_games.keys())

        # ---------------- LOCAL GAMES ----------------
        for name, info in local_games.items():
            file = info["file"]
            major, minor = info["major"], info["minor"]

            # LOCAL ONLY (exact name match against repo, not substring)
            if name not in repo_names:
                self.add_button(file, name, major, minor, False)
                continue

            repo_entry = self.repo_games[name]
            repo_version = (repo_entry["major"], repo_entry["minor"])

            # UPDATE CHECK
            if (major, minor) < repo_version:
                print(f"Updating {name}...")

                new_file = repo_entry["file"]
                if download_game(new_file):
                    if new_file != file:
                        delete_old_version(file)
                    file = new_file
                    major, minor = repo_entry["major"], repo_entry["minor"]

            self.add_button(file, name, major, minor, True)

        # ---------------- MISSING GAMES ----------------
        for name, entry in self.repo_games.items():
            # Exact match: is this repo game already accounted for locally?
            if name not in local_games:
                self.add_button(entry["file"], name, entry["major"], entry["minor"], True)

    # -----------------------
    # UI BUTTON
    # -----------------------
    def add_button(self, file_name, display_name, major, minor, from_repo):

        label = f"{display_name} ({version_str(major, minor)})"

        btn = Button(
            text=label,
            size_hint_y=None,
            height=55,
            font_size=18
        )

        def on_click(_):

            if from_repo:
                download_game(file_name)

            url = f"http://localhost:{PORT}/games/{file_name}"
            webbrowser.open(url)

        btn.bind(on_release=on_click)
        self.grid.add_widget(btn)

# -----------------------
# APP
# -----------------------
class LegendaryMVRApp(App):
    title = "LegendaryMVR"

    def build(self):
        Window.set_title("LegendaryMVR")
        return LegendaryMVRHub()

if __name__ == "__main__":
    LegendaryMVRApp().run()
