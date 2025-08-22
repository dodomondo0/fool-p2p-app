# app/games/base/base_game_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

class BaseGameScreen(Screen):
    """Базовый класс для всех игровых экранов"""
    
    def __init__(self, game_logic=None, **kwargs):
        super().__init__(**kwargs)
        self.game_logic = game_logic
        self.p2p_client = None
        self.signaling_client = None
        
    def setup_ui(self):
        """Настройка базового интерфейса"""
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Заголовок игры
        self.title_label = Label(
            text=self.game_logic.GAME_NAME if self.game_logic else 'Игра',
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(self.title_label)
        
        # Область для игрового поля (переопределяется в подклассах)
        self.game_area = BoxLayout(orientation='vertical')
        layout.add_widget(self.game_area)
        
        # Область для сообщений/логов
        self.log_area = BoxLayout(size_hint_y=0.3)
        self.log_label = Label(
            text=f'Добро пожаловать в {self.game_logic.GAME_NAME}!' if self.game_logic else 'Добро пожаловать в игру!',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.log_area.add_widget(self.log_label)
        layout.add_widget(self.log_area)
        
        self.add_widget(layout)
        
    def add_log_message(self, message):
        """Добавление сообщения в лог"""
        current_text = self.log_label.text
        welcome_text = f'Добро пожаловать в {self.game_logic.GAME_NAME}!' if self.game_logic else 'Добро пожаловать в игру!'
        
        if current_text == welcome_text:
            self.log_label.text = message
        else:
            self.log_label.text = current_text + '\n' + message
        print(f"[{self.game_logic.GAME_NAME if self.game_logic else 'GAME'} LOG] {message}")
        
    def setup_networking(self):
        """Настройка сетевого взаимодействия (переопределяется в подклассах)"""
        pass
        
    def handle_network_message(self, message):
        """Обработка сетевых сообщений (переопределяется в подклассах)"""
        pass
        
    def on_pre_enter(self):
        """Вызывается перед отображением экрана"""
        self.setup_ui()
        self.setup_networking()