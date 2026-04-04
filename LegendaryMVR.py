import os
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
# Config
# -----------------------
GITHUB_REPO_API = "https://api.github.com/repos/Legendary-Games-Studios/Legendary-MVR-Apps/contents/"
LOCAL_DIR = "downloaded_games"
PORT = 8000

os.makedirs(LOCAL_DIR, exist_ok=True)

# -----------------------
# Local HTTP Server
# -----------------------
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=LOCAL_DIR, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# -----------------------
# VR Hub GUI
# -----------------------
class VRHub(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=6, padding=6)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)
        self.load_games()

    def load_games(self):
        try:
            response = requests.get(GITHUB_REPO_API).json()
            games = [item['name'] for item in response if item['name'].endswith('.html')]
            for file_name in games:
                display_name = file_name.replace('.html', '')
                btn = Button(
                    text=display_name,
                    size_hint_y=None,
                    height=55,
                    font_size=18
                )
                btn.bind(on_release=lambda btn, name=file_name: self.download_and_launch(name))
                self.grid.add_widget(btn)
        except Exception as e:
            print("Error fetching repo:", e)

    def download_and_launch(self, game_file):
        local_path = os.path.join(LOCAL_DIR, game_file)
        if not os.path.exists(local_path):
            raw_url = f"https://raw.githubusercontent.com/Legendary-Games-Studios/Legendary-MVR-Apps/main/{game_file}"
            try:
                r = requests.get(raw_url)
                r.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded {game_file}")
            except Exception as e:
                print("Error downloading file:", e)
                return
        # Launch in default browser from Python
        url = f"http://localhost:{PORT}/{game_file}"
        webbrowser.open(url)  # <-- works fully in Python

class VRHubApp(App):
    def build(self):
        return VRHub()

if __name__ == "__main__":
    VRHubApp().run()