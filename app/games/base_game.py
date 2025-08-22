# app/games/base_game.py
from abc import ABC, abstractmethod

class BaseGame(ABC):
    """Базовый класс для всех игр"""
    
    def __init__(self, game_mode=None):
        self.game_mode = game_mode
        self.players = []
        self.game_state = {}
        
    @abstractmethod
    def start_game(self, players):
        """Начало игры с указанными игроками"""
        pass
        
    @abstractmethod
    def process_move(self, player_id, move_data):
        """Обработка хода игрока"""
        pass
        
    @abstractmethod
    def get_game_state(self):
        """Получение текущего состояния игры"""
        pass
        
    @abstractmethod
    def is_game_over(self):
        """Проверка, закончилась ли игра"""
        pass
        
    def add_player(self, player_id):
        """Добавление игрока"""
        if player_id not in self.players:
            self.players.append(player_id)
            
    def remove_player(self, player_id):
        """Удаление игрока"""
        if player_id in self.players:
            self.players.remove(player_id)