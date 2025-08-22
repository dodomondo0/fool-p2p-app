# app/core/screens/menu_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from widgets.game_card import GameCard

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'menu'
        
    def on_pre_enter(self):
        self.setup_ui()
        
    def setup_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical')
        
        # Заголовок
        title = Label(
            text='Игровой зал',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)
        
        # ScrollView для таблицы игр
        scroll = ScrollView()
        
        # GridLayout с 2 столбцами для игр
        games_layout = GridLayout(cols=2, spacing=dp(15), padding=dp(15), size_hint_y=None)
        games_layout.bind(minimum_height=games_layout.setter('height'))
        
        # Получаем список всех доступных игр из реестра
        try:
            from games.registry import GameRegistry
            games = GameRegistry.get_all_games()
        except Exception as e:
            print(f"Ошибка при получении списка игр: {e}")
            games = {}
        
        # Добавляем карточки игр
        if games:
            for game_name, game_info in games.items():
                card = GameCard(
                    game_name=game_info['name'],
                    game_description=game_info['description'],
                    game_icon=game_info['icon']
                )
                games_layout.add_widget(card)
        else:
            # Если игр нет, показываем сообщение
            no_games_label = Label(
                text='Пока нет доступных игр.\nДобавьте игры в папку games/',
                halign='center',
                valign='middle'
            )
            games_layout.add_widget(no_games_label)
        
        scroll.add_widget(games_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)