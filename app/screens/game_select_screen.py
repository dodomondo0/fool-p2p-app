from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
import uuid
import re

class GameSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'game_select'
        self.mode = None
        self.room_name_input = None
        self.password_input = None
        
    def on_pre_enter(self):
        self.setup_ui()
        
    def setup_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        title = Label(
            text=f'Выбор режима для игры "{self.get_app().game_selected}"',
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Выбор режима игры
        mode_label = Label(
            text='Выберите режим игры:',
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(mode_label)
        
        # Dropdown для выбора режима
        from kivy.uix.dropdown import DropDown
        self.mode_dropdown = DropDown()
        modes = ['Подкидной', 'Переводной']
        
        for mode in modes:
            btn = Button(text=mode, size_hint_y=None, height=dp(40))
            btn.bind(on_release=lambda btn: self.mode_dropdown.select(btn.text))
            self.mode_dropdown.add_widget(btn)
        
        self.mode_button = Button(
            text='Выберите режим',
            size_hint_y=None,
            height=dp(50)
        )
        self.mode_button.bind(on_release=self.mode_dropdown.open)
        self.mode_dropdown.bind(on_select=lambda instance, x: setattr(self.mode_button, 'text', x))
        layout.add_widget(self.mode_button)
        
        # Ввод названия комнаты (для хоста)
        room_label = Label(
            text='Название комнаты (для хоста):',
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(room_label)
        
        self.room_name_input = TextInput(
            hint_text='Оставьте пустым для авто-генерации',
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        layout.add_widget(self.room_name_input)
        
        # Ввод пароля (для хоста)
        password_label = Label(
            text='Пароль комнаты (опционально):',
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(password_label)
        
        self.password_input = TextInput(
            hint_text='Оставьте пустым для открытой комнаты',
            size_hint_y=None,
            height=dp(40),
            multiline=False,
            password=True
        )
        layout.add_widget(self.password_input)
        
        # Кнопки действий
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        # Кнопка создания сервера
        create_server_btn = Button(text='Создать сервер')
        create_server_btn.bind(on_press=self.create_server)
        
        # Кнопка подключения
        connect_btn = Button(text='Подключиться')
        connect_btn.bind(on_press=self.connect_to_server)
        
        # Кнопка назад
        back_btn = Button(text='Назад')
        back_btn.bind(on_press=self.go_back)
        
        buttons_layout.add_widget(create_server_btn)
        buttons_layout.add_widget(connect_btn)
        buttons_layout.add_widget(back_btn)
        
        layout.add_widget(buttons_layout)
        self.add_widget(layout)
    
    def create_server(self, instance):
        if not self.mode_button.text or self.mode_button.text == 'Выберите режим':
            self.show_error('Пожалуйста, выберите режим игры')
            return
            
        # Проверка названия комнаты
        room_name = self.room_name_input.text.strip()
        if not room_name:
            # Авто-генерация имени комнаты
            room_name = f"fool_{str(uuid.uuid4())[:8]}"
        else:
            # Проверка на допустимые символы
            if not self.validate_room_name(room_name):
                self.show_error('Название комнаты может содержать только буквы, цифры, дефис и подчеркивание (3-20 символов)')
                return
        
        # Проверка пароля
        password = self.password_input.text
        if password and len(password) < 4:
            self.show_error('Пароль должен содержать минимум 4 символа')
            return
        
        # Сохраняем данные в приложении
        self.get_app().room_name = room_name
        self.get_app().game_mode = self.mode_button.text.lower()
        self.get_app().room_password = password if password else None
        self.get_app().is_host = True
        
        # Переходим к игре
        self.get_app().root.current = 'game'
    
    def connect_to_server(self, instance):
        if not self.mode_button.text or self.mode_button.text == 'Выберите режим':
            self.show_error('Пожалуйста, выберите режим игры')
            return
            
        # Для подключения открываем popup с вводом данных
        self.show_connect_popup()
    
    def show_connect_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        title = Label(
            text='Подключение к комнате',
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # Ввод названия комнаты
        room_label = Label(
            text='Название комнаты:',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(room_label)
        
        room_input = TextInput(
            hint_text='Введите название комнаты',
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        content.add_widget(room_input)
        
        # Ввод пароля
        password_label = Label(
            text='Пароль (если требуется):',
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(password_label)
        
        password_input = TextInput(
            hint_text='Введите пароль',
            size_hint_y=None,
            height=dp(40),
            multiline=False,
            password=True
        )
        content.add_widget(password_input)
        
        # Кнопки
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        connect_btn = Button(text='Подключиться')
        cancel_btn = Button(text='Отмена')
        
        buttons_layout.add_widget(connect_btn)
        buttons_layout.add_widget(cancel_btn)
        
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Подключение к комнате',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        # Обработчики кнопок
        def do_connect(instance):
            room_name = room_input.text.strip()
            password = password_input.text
            
            if not room_name:
                self.show_error('Введите название комнаты')
                return
            
            # Проверка названия комнаты
            if not self.validate_room_name(room_name):
                self.show_error('Недопустимое название комнаты')
                return
            
            # Сохраняем данные и подключаемся
            self.get_app().room_name = room_name
            self.get_app().game_mode = self.mode_button.text.lower()
            self.get_app().room_password = password if password else None
            self.get_app().is_host = False
            
            popup.dismiss()
            self.get_app().root.current = 'game'
        
        connect_btn.bind(on_press=do_connect)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def validate_room_name(self, room_name):
        """Проверка допустимости названия комнаты"""
        # Должен содержать 3-20 символов, только буквы, цифры, дефис и подчеркивание
        pattern = r'^[a-zA-Z0-9_-]{3,20}$'
        return bool(re.match(pattern, room_name))
    
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        popup = Popup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        self.get_app().root.current = 'menu'
    
    def get_app(self):
        from kivy.app import App
        return App.get_running_app()