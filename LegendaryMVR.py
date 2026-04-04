# vr_hub_android.py
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

# Android WebView support
try:
    from kivy_webview import WebView
except ImportError:
    WebView = None  # fallback for desktop/testing

# Your GitHub repo contents API
GITHUB_REPO_API = "https://api.github.com/repos/Legendary-Games-Studios/Legendary-MVR-Apps/contents/"

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
            # Filter and list .html files
            games = [item['name'] for item in response if item['name'].endswith('.html')]
            for file_name in games:
                # strip ".html"
                display_name = file_name.replace('.html', '')
                btn = Button(
                    text=display_name,
                    size_hint_y=None,
                    height=55,
                    font_size=18
                )
                btn.bind(on_release=lambda btn, name=file_name: self.launch_game(name))
                self.grid.add_widget(btn)
        except Exception as e:
            print("Error loading repo contents:", e)

    def launch_game(self, game_file):
        # Construct the raw file URL
        url = f"https://raw.githubusercontent.com/Legendary-Games-Studios/Legendary-MVR-Apps/main/{game_file}"
        if WebView:
            self.clear_widgets()
            self.add_widget(WebView(url=url))
        else:
            print("Would open in WebView:", url)  # desktop fallback

class VRHubApp(App):
    def build(self):
        return VRHub()

if __name__ == "__main__":
    VRHubApp().run()