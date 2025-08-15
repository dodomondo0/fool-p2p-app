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
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Заголовок
        title = Label(
            text='Выберите игру',
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)
        
        # ScrollView для списка игр
        scroll = ScrollView()
        games_layout = GridLayout(cols=2, spacing=dp(20), padding=dp(20), size_hint_y=None)
        games_layout.bind(minimum_height=games_layout.setter('height'))
        
        # Добавляем игры
        games = [
            {
                'name': 'Дурак',
                'description': 'Классическая русская карточная игра. Цель - избавиться от всех карт первым.',
                'icon': 'assets/fool_icon.png'
            },
            # Здесь можно добавить другие игры в будущем
        ]
        
        for game in games:
            card = GameCard(
                game_name=game['name'],
                game_description=game['description'],
                game_icon=game['icon']
            )
            games_layout.add_widget(card)
        
        scroll.add_widget(games_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)