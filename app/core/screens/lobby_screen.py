# app/core/screens/lobby_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
import threading
import asyncio
import time

class LobbyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signaling_client = None
        self.p2p_host = None # Только для хоста
        self.p2p_client = None # Только для клиента
        self.connected_players = []
        self.is_host = False
        self.game_params = {} # Для хранения параметров игры
        
        # UI элементы
        self.status_label = None
        self.players_layout = None
        self.players_scroll = None
        self.mode_dropdown = None
        self.deck_dropdown = None
        self.players_dropdown = None
        self.room_name_input = None
        self.password_input = None
        self.start_game_btn = None
        
    def on_pre_enter(self):
        # Определяем, является ли пользователь хостом
        # Это должно быть установлено в game_manager до перехода на этот экран
        app = self.get_app()
        self.is_host = app.game_manager.is_host if app.game_manager else False
        self.setup_ui()
        # Не вызываем setup_networking сразу, ждем действий пользователя
        
    def setup_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Заголовок
        title_text = f'Лобби - {self.get_app().game_selected}' if self.get_app().game_selected else 'Лобби'
        title = Label(
            text=title_text,
            font_size=dp(22),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Статус
        self.status_label = Label(
            text='Готов к настройке...',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.status_label)
        
        if self.is_host:
            self._setup_host_ui(layout)
        else:
            self._setup_client_ui(layout)
            
        # Кнопка "Назад"
        back_btn = Button(text='Назад в меню', size_hint_y=None, height=dp(40))
        back_btn.bind(on_press=self.leave_lobby)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
    def _setup_host_ui(self, parent_layout):
        """Настройка UI для хоста (создателя комнаты)"""
        # Параметры игры
        params_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Выбор режима игры
        mode_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        mode_label = Label(text='Режим:', size_hint_x=0.3, halign='right')
        self.mode_button = Button(text='Выбрать режим', size_hint_x=0.7)
        
        self.mode_dropdown = DropDown()
        modes = ['Подкидной', 'Переводной']
        for mode in modes:
            btn = Button(text=mode, size_hint_y=None, height=dp(30))
            btn.bind(on_release=lambda btn: self.mode_dropdown.select(btn.text))
            self.mode_dropdown.add_widget(btn)
        self.mode_dropdown.bind(on_select=lambda instance, x: setattr(self.mode_button, 'text', x))
        self.mode_button.bind(on_release=self.mode_dropdown.open)
        
        mode_layout.add_widget(mode_label)
        mode_layout.add_widget(self.mode_button)
        params_layout.add_widget(mode_layout)
        
        # Выбор колоды
        deck_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        deck_label = Label(text='Колода:', size_hint_x=0.3, halign='right')
        self.deck_button = Button(text='36 карт', size_hint_x=0.7)
        
        self.deck_dropdown = DropDown()
        decks = ['36 карт', '52 карты']
        for deck in decks:
            btn = Button(text=deck, size_hint_y=None, height=dp(30))
            btn.bind(on_release=lambda btn: self.deck_dropdown.select(btn.text))
            self.deck_dropdown.add_widget(btn)
        self.deck_dropdown.bind(on_select=lambda instance, x: setattr(self.deck_button, 'text', x))
        self.deck_button.bind(on_release=self.deck_dropdown.open)
        
        deck_layout.add_widget(deck_label)
        deck_layout.add_widget(self.deck_button)
        params_layout.add_widget(deck_layout)
        
        # Выбор количества игроков
        players_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        players_label = Label(text='Игроков:', size_hint_x=0.3, halign='right')
        self.players_button = Button(text='2', size_hint_x=0.7)
        
        self.players_dropdown = DropDown()
        players_count = [str(i) for i in range(2, 7)] # от 2 до 6
        for count in players_count:
            btn = Button(text=count, size_hint_y=None, height=dp(30))
            btn.bind(on_release=lambda btn: self.players_dropdown.select(btn.text))
            self.players_dropdown.add_widget(btn)
        self.players_dropdown.bind(on_select=lambda instance, x: setattr(self.players_button, 'text', x))
        self.players_button.bind(on_release=self.players_dropdown.open)
        
        players_layout.add_widget(players_label)
        players_layout.add_widget(self.players_button)
        params_layout.add_widget(players_layout)
        
        # Название комнаты
        room_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        room_label = Label(text='Комната:', size_hint_x=0.3, halign='right')
        self.room_name_input = TextInput(hint_text='Введите название', size_hint_x=0.7, multiline=False)
        room_layout.add_widget(room_label)
        room_layout.add_widget(self.room_name_input)
        params_layout.add_widget(room_layout)
        
        # Пароль
        pass_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        pass_label = Label(text='Пароль:', size_hint_x=0.3, halign='right')
        self.password_input = TextInput(hint_text='Опционально', size_hint_x=0.7, multiline=False, password=True)
        pass_layout.add_widget(pass_label)
        pass_layout.add_widget(self.password_input)
        params_layout.add_widget(pass_layout)
        
        parent_layout.add_widget(params_layout)
        
        # Кнопка "Создать комнату"
        self.create_room_btn = Button(text='Создать комнату', size_hint_y=None, height=dp(50))
        self.create_room_btn.bind(on_press=self.create_room)
        parent_layout.add_widget(self.create_room_btn)
        
        # Список игроков
        self._setup_players_list(parent_layout)
        
        # Кнопка "Начать игру" (изначально скрыта/отключена)
        self.start_game_btn = Button(text='Начать игру', size_hint_y=None, height=dp(50), disabled=True)
        self.start_game_btn.bind(on_press=self.start_game)
        parent_layout.add_widget(self.start_game_btn)
        
    def _setup_client_ui(self, parent_layout):
        """Настройка UI для клиента (подключающегося игрока)"""
        # Кнопка "Подключиться"
        self.connect_btn = Button(text='Подключиться к комнате', size_hint_y=None, height=dp(50))
        self.connect_btn.bind(on_press=self.show_connect_popup)
        parent_layout.add_widget(self.connect_btn)
        
        # Информация о подключении
        self.connection_info = Label(
            text='Введите название комнаты для подключения',
            size_hint_y=None,
            height=dp(40)
        )
        parent_layout.add_widget(self.connection_info)
        
        # Список игроков (будет обновляться после подключения)
        self._setup_players_list(parent_layout)
        
    def _setup_players_list(self, parent_layout):
        """Настройка списка игроков"""
        players_label = Label(
            text='Подключенные игроки:',
            size_hint_y=None,
            height=dp(30)
        )
        parent_layout.add_widget(players_label)
        
        self.players_scroll = ScrollView(size_hint_y=0.4)
        self.players_layout = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.players_layout.bind(minimum_height=self.players_layout.setter('height'))
        self.players_scroll.add_widget(self.players_layout)
        parent_layout.add_widget(self.players_scroll)
        
    def create_room(self, instance):
        """Создание комнаты (для хоста)"""
        # Валидация параметров
        if self.mode_button.text == 'Выбрать режим':
            self.show_error("Пожалуйста, выберите режим игры")
            return
            
        if not self.room_name_input.text.strip():
            self.show_error("Пожалуйста, введите название комнаты")
            return
            
        # Проверка количества карт и игроков
        deck_text = self.deck_button.text
        players_text = self.players_button.text
        deck_size = 36 if '36' in deck_text else 52
        players_count = int(players_text)
        
        # Минимальное количество карт: 6 карт на игрока при старте
        min_cards_needed = players_count * 6
        if deck_size < min_cards_needed:
            self.show_error(f"Для {players_count} игроков нужно минимум {min_cards_needed} карт. Выбрано {deck_size}.")
            return
            
        # Сохраняем параметры
        self.game_params = {
            'mode': self.mode_button.text.lower(),
            'deck_size': deck_size,
            'players_count': players_count,
            'room_name': self.room_name_input.text.strip(),
            'password': self.password_input.text
        }
        
        app = self.get_app()
        app.game_manager.game_mode = self.game_params['mode']
        app.game_manager.room_name = self.game_params['room_name']
        app.game_manager.room_password = self.game_params['password']
        app.game_manager.max_players = self.game_params['players_count']
        
        self.status_label.text = f"Создание комнаты '{self.game_params['room_name']}'..."
        self.create_room_btn.disabled = True
        
        # Запускаем подключение в отдельном потоке
        threading.Thread(target=self._connect_as_host, daemon=True).start()
        
    def show_connect_popup(self, instance):
        """Показать popup для подключения клиента"""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        title = Label(
            text='Подключение к комнате',
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # Ввод названия комнаты
        room_label = Label(text='Название комнаты:', size_hint_y=None, height=dp(25))
        content.add_widget(room_label)
        
        room_input = TextInput(
            hint_text='Введите название комнаты',
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        content.add_widget(room_input)
        
        # Ввод пароля
        password_label = Label(text='Пароль (если требуется):', size_hint_y=None, height=dp(25))
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
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        connect_btn = Button(text='Подключиться')
        cancel_btn = Button(text='Отмена')
        
        buttons_layout.add_widget(connect_btn)
        buttons_layout.add_widget(cancel_btn)
        
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Подключение к комнате',
            content=content,
            size_hint=(0.85, 0.6)
        )
        
        def do_connect(instance):
            room_name = room_input.text.strip()
            password = password_input.text
            
            if not room_name:
                self.show_error('Введите название комнаты')
                return
                
            # Сохраняем параметры подключения
            app = self.get_app()
            app.game_manager.room_name = room_name
            app.game_manager.room_password = password
            
            self.status_label.text = f"Подключение к комнате '{room_name}'..."
            self.connect_btn.disabled = True
            popup.dismiss()
            
            # Запускаем подключение в отдельном потоке
            threading.Thread(target=self._connect_as_client, daemon=True).start()
            
        connect_btn.bind(on_press=do_connect)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()
        
    def _connect_as_host(self):
        """Подключение в роли хоста"""
        try:
            from core.network.signaling_client import SignalingClient
            from core.network.p2p_host import P2PHost
            
            def on_signal_received(data):
                # Обработка сигналов в основном потоке Kivy
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.handle_signal(data), 0)
                
            def on_host_found(host_id):
                # Для хоста это не используется
                pass
                
            self.signaling_client = SignalingClient(on_signal=on_signal_received)
            self.signaling_client.is_host = True
            
            # Создаем P2P хост
            self.p2p_host = P2PHost(on_client_message_callback=self.handle_client_message)
            
            self.signaling_client.connect()
            
            # Присоединяемся к комнате
            time.sleep(1) # Небольшая задержка для установления соединения
            self.signaling_client.join_room(
                self.game_params['room_name'], 
                self.game_params['password']
            )
            
            # Обновляем UI в основном потоке
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.on_host_connected(), 0)
            
        except Exception as e:
            print(f"Ошибка подключения хоста: {e}")
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.on_connection_error(str(e)), 0)
            
    def _connect_as_client(self):
        """Подключение в роли клиента"""
        try:
            from core.network.signaling_client import SignalingClient
            
            def on_signal_received(data):
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.handle_signal(data), 0)
                
            def on_host_found(host_id):
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.on_host_found(host_id), 0)
                
            self.signaling_client = SignalingClient(on_signal=on_signal_received)
            self.signaling_client.is_host = False
            self.signaling_client.found_host_callback = on_host_found
            
            self.signaling_client.connect()
            
            # Присоединяемся к комнате
            time.sleep(1) # Небольшая задержка
            room_name = self.get_app().game_manager.room_name
            room_password = self.get_app().game_manager.room_password
            self.signaling_client.join_room(room_name, room_password)
            
        except Exception as e:
            print(f"Ошибка подключения клиента: {e}")
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.on_connection_error(str(e)), 0)
            
    def on_host_connected(self):
        """Вызывается при успешном подключении хоста"""
        self.status_label.text = f"Комната '{self.game_params['room_name']}' создана. Ожидание игроков..."
        self.add_player_to_list("Вы (хост)")
        # Кнопка "Начать игру" будет активирована, когда подключатся нужные игроки
        
    def on_connection_error(self, error_message):
        """Вызывается при ошибке подключения"""
        self.status_label.text = f"Ошибка подключения: {error_message}"
        
        if self.is_host:
            self.create_room_btn.disabled = False
            # Планируем повторную попытку через 2 секунды
            from kivy.clock import Clock
            Clock.schedule_once(self._retry_host_connection, 2)
        else:
            self.connect_btn.disabled = False
            # Планируем повторную попытку через 2 секунды
            from kivy.clock import Clock
            Clock.schedule_once(self._retry_client_connection, 2)
            
    def _retry_host_connection(self, dt):
        """Повторная попытка подключения для хоста"""
        self.status_label.text = "Повторная попытка подключения..."
        threading.Thread(target=self._connect_as_host, daemon=True).start()
        
    def _retry_client_connection(self, dt):
        """Повторная попытка подключения для клиента"""
        self.status_label.text = "Повторная попытка подключения..."
        threading.Thread(target=self._connect_as_client, daemon=True).start()
        
    def handle_signal(self, data):
        """Обработка сигнальных сообщений"""
        signal_type = data.get('type')
        signal_data = data.get('data', {})
        
        if signal_type == 'joined':
            status = signal_data.get('status')
            if status == 'success':
                if self.is_host:
                    self.status_label.text = f"Комната создана. Ожидание игроков..."
                else:
                    self.status_label.text = "Подключено к комнате"
                    self.connection_info.text = f"Комната: {self.get_app().game_manager.room_name}"
                    self.add_player_to_list("Вы")
            elif status == 'error':
                self.status_label.text = f"Ошибка: {signal_data.get('message', 'Неизвестная ошибка')}"
                
        elif signal_type == 'player_joined':
            player_name = signal_data.get('player_name', 'Игрок')
            self.add_player_to_list(player_name)
            self.status_label.text = f"Игрок {player_name} присоединился"
            
            # Проверяем, можно ли начать игру
            if self.is_host:
                current_players = len(self.connected_players)
                max_players = self.game_params.get('players_count', 2)
                if current_players >= 2: # Минимум 2 игрока
                    self.start_game_btn.disabled = False
                    if current_players >= max_players:
                        self.status_label.text = "Все игроки подключены. Можно начинать!"
                        
        elif signal_type == 'player_left':
            player_name = signal_data.get('player_name', 'Игрок')
            self.remove_player_from_list(player_name)
            self.status_label.text = f"Игрок {player_name} отключился"
            
            # Проверяем, можно ли начать игру
            if self.is_host:
                current_players = len(self.connected_players)
                if current_players < 2:
                    self.start_game_btn.disabled = True
                    
        elif signal_type == 'game_start':
            # Переход к игровому экрану
            game_name = self.get_app().game_manager.current_game.lower()
            try:
                game_module = __import__(f'games.{game_name}.game_screen', fromlist=['GameScreen'])
                game_screen_class = getattr(game_module, 'GameScreen')
                
                # Удаляем старый игровой экран, если есть
                if self.get_app().sm.has_screen('game'):
                    self.get_app().sm.remove_widget(self.get_app().sm.get_screen('game'))
                    
                game_screen = game_screen_class(name='game')
                self.get_app().sm.add_widget(game_screen)
                self.get_app().sm.current = 'game'
            except Exception as e:
                self.status_label.text = f"Ошибка запуска игры: {e}"
                
    def handle_client_message(self, client_id, message_data):
        """Обработка сообщений от клиентов (только для хоста)"""
        # TODO: Реализовать обработку сообщений от клиентов
        print(f"Получено сообщение от клиента {client_id}: {message_data}")
        
    def add_player_to_list(self, player_name):
        """Добавление игрока в список"""
        if player_name not in self.connected_players:
            self.connected_players.append(player_name)
            
        # Обновляем UI
        self.players_layout.clear_widgets()
        for player in self.connected_players:
            player_label = Label(
                text=player,
                size_hint_y=None,
                height=dp(25)
            )
            self.players_layout.add_widget(player_label)
            
    def remove_player_from_list(self, player_name):
        """Удаление игрока из списка"""
        if player_name in self.connected_players:
            self.connected_players.remove(player_name)
            
        # Обновляем UI
        self.players_layout.clear_widgets()
        for player in self.connected_players:
            player_label = Label(
                text=player,
                size_hint_y=None,
                height=dp(25)
            )
            self.players_layout.add_widget(player_label)
            
    def start_game(self, instance):
        """Начало игры (только для хоста)"""
        if self.signaling_client:
            # Отправляем сигнал о начале игры всем игрокам
            signal_data = {
                'type': 'game_start',
                'data': {
                    'game': self.get_app().game_manager.current_game,
                    'params': self.game_params
                }
            }
            # Отправляем через сигнальный сервер
            # В реальной реализации нужно отправить всем игрокам
            self.signaling_client.send_signal('all', signal_data)
            
    def leave_lobby(self, instance):
        """Выход из лобби"""
        # Закрываем соединения
        if self.signaling_client:
            try:
                if hasattr(self.signaling_client.sio, 'connected') and self.signaling_client.sio.connected:
                    self.signaling_client.sio.disconnect()
            except:
                pass
                
        # Очищаем данные менеджера игры
        if self.get_app().game_manager:
            self.get_app().game_manager.room_name = None
            self.get_app().game_manager.room_password = None
            self.get_app().game_manager.is_host = False
            self.get_app().game_manager.players = []
            
        self.get_app().sm.current = 'menu'
        
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        popup = Popup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        
    def get_app(self):
        """Получение экземпляра приложения"""
        from kivy.app import App
        return App.get_running_app()
