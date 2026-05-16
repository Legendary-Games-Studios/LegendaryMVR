import os
import re
import threading
import requests
import http.server
import socketserver
import webbrowser

from kivy.app import App
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
# GameName_V1.0.html → (GameName, 100)
# -----------------------
def parse_game(file):
    match = re.match(r"(.*)_V(\d+)\.(\d+)\.html", file)
    if match:
        name = match.group(1)
        major = int(match.group(2))
        minor = int(match.group(3))
        version = major * 100 + minor
        return name, version

    return file.replace(".html", ""), 1

# -----------------------
# DOWNLOAD GAME
# -----------------------
def download_game(file_name):
    try:
        url = f"https://raw.githubusercontent.com/Legendary-Games-Studios/Legendary-MVR-Apps/main/{file_name}"
        r = requests.get(url)
        r.raise_for_status()

        local_path = os.path.join(GAMES_DIR, file_name)

        with open(local_path, "wb") as f:
            f.write(r.content)

        print(f"Downloaded: {file_name}")

    except Exception as e:
        print("Download error:", e)

# -----------------------
# HUB
# -----------------------
class VRHub(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=6, padding=6)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)

        self.repo_games = {}

        self.load_repo()
        self.load_local()

    # -----------------------
    # LOAD GITHUB
    # -----------------------
    def load_repo(self):
        try:
            data = requests.get(GITHUB_REPO_API).json()

            for item in data:
                if item["name"].endswith(".html"):

                    name, version = parse_game(item["name"])

                    # keep highest version per game
                    if name not in self.repo_games:
                        self.repo_games[name] = {
                            "file": item["name"],
                            "version": version
                        }
                    else:
                        if version > self.repo_games[name]["version"]:
                            self.repo_games[name] = {
                                "file": item["name"],
                                "version": version
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

        repo_names = set(self.repo_games.keys())

        # ---------------- LOCAL GAMES ----------------
        for file in local_files:

            name, version = parse_game(file)

            # LOCAL ONLY
            if name not in repo_names:
                self.add_button(file, f"[LOCAL] {name}", False)
                continue

            repo_version = self.repo_games[name]["version"]

            # UPDATE CHECK
            if version < repo_version:
                print(f"Updating {name}...")

                download_game(self.repo_games[name]["file"])

                file = self.repo_games[name]["file"]

            self.add_button(file, name, True)

        # ---------------- MISSING GAMES ----------------
        for name in self.repo_games:

            exists = any(name in f for f in local_files)

            if not exists:
                file = self.repo_games[name]["file"]
                self.add_button(file, name, True)

    # -----------------------
    # UI BUTTON
    # -----------------------
    def add_button(self, file_name, display_name, from_repo):

        btn = Button(
            text=display_name,
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
class VRHubApp(App):
    def build(self):
        return VRHub()

if __name__ == "__main__":
    VRHubApp().run()