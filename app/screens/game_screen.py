from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
import uuid

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'game'
        self.signaling_client = None
        self.host_id = None
        self.is_connected = False
        
    def on_pre_enter(self):
        self.setup_ui()
        self.setup_signaling()
        
    def setup_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        title = Label(
            text=f'Игра "{self.get_app().game_selected}" - {self.get_app().game_mode}',
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Информация о статусе
        self.status_label = Label(
            text='Инициализация подключения...',
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.status_label)
        
        # Лог подключения
        self.log_label = Label(
            text='Лог подключения будет здесь...',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        layout.add_widget(self.log_label)
        
        # Поле для отображения игрового процесса
        game_area = BoxLayout(orientation='vertical', size_hint_y=0.5)
        game_area.add_widget(Label(text='Здесь будет игровое поле'))
        layout.add_widget(game_area)
        
        # Кнопки управления
        controls_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        if self.get_app().is_host:
            start_btn = Button(text='Начать игру')
            start_btn.bind(on_press=self.start_game)
            controls_layout.add_widget(start_btn)
        
        back_btn = Button(text='Назад')
        back_btn.bind(on_press=self.go_back)
        controls_layout.add_widget(back_btn)
        
        layout.add_widget(controls_layout)
        self.add_widget(layout)
    
    def setup_signaling(self):
        """Настройка сигнального клиента"""
        try:
            from signaling_client import SignalingClient
            
            def on_signal_received(data):
                self.add_log(f"Получен сигнал: {data.get('type', 'unknown')}")
                # Здесь будет обработка сигнала
            
            def on_host_found(host_id):
                self.add_log(f"Найден хост: {host_id}")
                self.host_id = host_id
                self.status_label.text = 'Подключение к хосту...'
                self.is_connected = True
            
            # Создаем сигнальный клиент
            self.signaling_client = SignalingClient(on_signal=on_signal_received)
            self.signaling_client.is_host = self.get_app().is_host
            self.signaling_client.found_host_callback = on_host_found
            
            # Подключаемся к серверу
            self.signaling_client.connect()
            
            # Получаем имя комнаты и пароль из приложения
            room_name = getattr(self.get_app(), 'room_name', 'default_room')
            room_password = getattr(self.get_app(), 'room_password', None)
            
            role = "Создание" if self.get_app().is_host else "Подключение к"
            self.add_log(f"{role} комнате: {room_name}")
            if room_password:
                self.add_log("Комната защищена паролем")
            
            # Присоединяемся к комнате с небольшой задержкой
            Clock.schedule_once(lambda dt: self.join_room(room_name, room_password), 1)
            
        except Exception as e:
            self.add_log(f"Ошибка настройки сигнализации: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def join_room(self, room_name, room_password):
        """Присоединение к комнате с задержкой"""
        try:
            if self.signaling_client:
                self.signaling_client.join_room(room_name, room_password)
                if self.get_app().is_host:
                    self.status_label.text = 'Ожидание подключения игрока...'
                    self.add_log("Сервер создан. Ожидание подключения...")
                else:
                    self.status_label.text = 'Поиск сервера...'
                    self.add_log("Поиск доступного сервера...")
        except Exception as e:
            self.add_log(f"Ошибка подключения к комнате: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def add_log(self, message):
        """Добавление сообщения в лог"""
        current_text = self.log_label.text
        if current_text == 'Лог подключения будет здесь...':
            self.log_label.text = message
        else:
            self.log_label.text = current_text + '\n' + message
        print(f"[LOG] {message}")  # Также выводим в консоль
    
    def start_game(self, instance):
        """Начало игры (только для хоста)"""
        if self.is_connected:
            self.add_log("Игра начата!")
        else:
            self.add_log("Ошибка: Нет подключения к другому игроку")
    
    def go_back(self, instance):
        # Отключаемся от сервера при выходе
        if self.signaling_client:
            try:
                if hasattr(self.signaling_client.sio, 'connected') and self.signaling_client.sio.connected:
                    self.signaling_client.sio.disconnect()
            except:
                pass
        self.get_app().root.current = 'game_select'
    
    def get_app(self):
        from kivy.app import App
        return App.get_running_app()