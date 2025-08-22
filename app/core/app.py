# app/core/app.py
import sys
import os

# Убедимся, что папка 'app' в пути поиска модулей
app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from core.screens.menu_screen import MenuScreen
from core.screens.lobby_screen import LobbyScreen

class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_manager = GameManager(self)
        
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(LobbyScreen(name='lobby'))
        return self.sm

class GameManager:
    """Менеджер для управления текущей игрой"""
    def __init__(self, app):
        self.app = app
        self.current_game = None
        self.game_logic = None
        self.game_screen = None
        self.is_host = False
        self.room_name = None
        self.room_password = None
        self.game_mode = None
        self.players = []
        
    def start_game(self, game_name):
        """Запуск новой игры"""
        self.current_game = game_name.lower()
        
        try:
            # Импортируем реестр игр
            from games.registry import GameRegistry
            
            # Получаем класс игры
            GameClass = GameRegistry.get_game_class(game_name)
            if not GameClass:
                raise ImportError(f"Игра '{game_name}' не найдена в реестре")
                
            # Создаем экземпляр логики игры
            self.game_logic = GameClass(game_mode=self.game_mode)
            
            # Динамически загружаем игровой экран
            game_screen_module = __import__(f'games.{self.current_game}.game_screen', fromlist=['GameScreen'])
            GameScreenClass = getattr(game_screen_module, 'GameScreen')
            
            self.game_screen = GameScreenClass(game_logic=self.game_logic, name='game')
            
            # Удаляем старый игровой экран, если есть
            if self.app.sm.has_screen('game'):
                self.app.sm.remove_widget(self.app.sm.get_screen('game'))
            self.app.sm.add_widget(self.game_screen)
            self.app.sm.current = 'game'
            
        except ImportError as e:
            print(f"Ошибка импорта игры {game_name}: {e}")
        except AttributeError as e:
            print(f"Ошибка: Класс GameScreen не найден в модуле {game_name}: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка при запуске игры {game_name}: {e}")