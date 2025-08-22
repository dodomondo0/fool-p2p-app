# app/games/fool/game_screen.py
from games.base.base_game_screen import BaseGameScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

class GameScreen(BaseGameScreen):
    """Игровой экран для игры 'Дурак'"""
    
    def __init__(self, game_logic=None, **kwargs):
        super().__init__(game_logic=game_logic, **kwargs)
        
    def setup_ui(self):
        """Настройка интерфейса для 'Дурака'"""
        super().setup_ui()
        if self.game_logic:
            self.title_label.text = f'Игра "{self.game_logic.GAME_NAME}"'
        
        # Очистим стандартную игровую область
        self.game_area.clear_widgets()
        
        # Верхняя область - козырь и отбой
        top_area = BoxLayout(size_hint_y=0.2, spacing=dp(10))
        self.trump_label = Label(text='Козырь: ?')
        self.discard_label = Label(text='Отбой: 0')
        top_area.add_widget(self.trump_label)
        top_area.add_widget(self.discard_label)
        self.game_area.add_widget(top_area)
        
        # Центральная область - игровое поле (карты на столе)
        self.table_area = BoxLayout(size_hint_y=0.4)
        self.table_label = Label(text='Игровое поле\n(здесь будут карты)')
        self.table_area.add_widget(self.table_label)
        self.game_area.add_widget(self.table_area)
        
        # Нижняя область - рука игрока
        self.hand_area = BoxLayout(size_hint_y=0.3, orientation='horizontal')
        self.hand_label = Label(text='Ваши карты\n(здесь будут ваши карты)')
        self.hand_area.add_widget(self.hand_label)
        self.game_area.add_widget(self.hand_area)
        
    def on_pre_enter(self):
        """Вызывается перед отображением экрана"""
        super().on_pre_enter()
        if self.game_logic:
            self.add_log_message(f"Игра '{self.game_logic.GAME_NAME}' готова к началу")