from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.menu_screen import MenuScreen
from screens.game_select_screen import GameSelectScreen
from screens.game_screen import GameScreen

class MyApp(App):
    def build(self):
        self.game_selected = None
        self.game_mode = None
        self.is_host = None
        
        sm = ScreenManager()
        sm.add_widget(MenuScreen())
        sm.add_widget(GameSelectScreen())
        sm.add_widget(GameScreen())
        return sm

MyApp().run()