# app/widgets/game_card.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.metrics import dp
import os

class GameCard(BoxLayout):
    def __init__(self, game_name, game_description, game_icon, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(180)
        self.padding = dp(10)
        self.spacing = dp(8)
        
        # Проверяем существование иконки, если нет - используем заглушку
        if not os.path.exists(game_icon):
            game_icon = 'assets/default_icon.png'  # Создай этот файл
            
        # Иконка игры
        icon = Image(source=game_icon, size_hint=(1, 0.7))
        self.add_widget(icon)
        
        # Название игры
        name_label = Label(
            text=game_name,
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            bold=True
        )
        self.add_widget(name_label)
        
        # Кнопка для открытия popup
        play_btn = Button(
            text='Играть',
            size_hint_y=None,
            height=dp(40)
        )
        play_btn.bind(on_press=lambda x: self.show_game_popup(game_name, game_description))
        self.add_widget(play_btn)
    
    def show_game_popup(self, game_name, game_description):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        title = Label(
            text=game_name,
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # Описание
        description = Label(
            text=game_description,
            text_size=(dp(300), None),
            halign='center'
        )
        content.add_widget(description)
        
        # Кнопки
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        play_btn = Button(text='Играть')
        play_btn.bind(on_press=lambda x: self.start_game(game_name))
        
        close_btn = Button(text='Закрыть')
        
        buttons_layout.add_widget(play_btn)
        buttons_layout.add_widget(close_btn)
        
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Информация об игре',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        play_btn.bind(on_press=lambda x: [popup.dismiss(), self.start_game(game_name)])
        
        popup.open()
    

    def start_game(self, game_name):
        from kivy.app import App
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.metrics import dp
        
        app = App.get_running_app()
        app.game_selected = game_name
        
        # Показываем popup с выбором роли
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = Label(
            text=f'Начать игру "{game_name}"',
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        label = Label(
            text='Выберите роль:',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(label)
        
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        host_btn = Button(text='Создать комнату')
        client_btn = Button(text='Подключиться')
        
        def start_as_host(instance):
            popup.dismiss()
            app.game_manager.is_host = True
            app.root.current = 'lobby'
            
        def start_as_client(instance):
            popup.dismiss()
            app.game_manager.is_host = False
            app.root.current = 'lobby'
            
        host_btn.bind(on_press=start_as_host)
        client_btn.bind(on_press=start_as_client)
        
        buttons_layout.add_widget(host_btn)
        buttons_layout.add_widget(client_btn)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Выбор роли',
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        popup.open()
