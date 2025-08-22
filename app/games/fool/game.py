# app/games/fool/game.py
import random
from games.base.base_game import BaseGame

class Game(BaseGame):
    """Логика игры 'Дурак'"""
    
    GAME_NAME = "Дурак"
    GAME_DESCRIPTION = "Классическая русская карточная игра. Цель - избавиться от всех карт первым."
    GAME_ICON = "assets/icons/fool_icon.png"  # Создай этот файл
    
    def __init__(self, game_mode='подкидной'):
        super().__init__(game_mode)
        self.deck = []
        self.trump_suit = None
        self.hands = {}
        self.table = []
        self.discard = []
        self.attacker = None
        self.defender = None
        
    def start_game(self, players):
        """Начало игры"""
        if len(players) < 2:
            raise ValueError("Для игры в 'Дурак' нужно минимум 2 игрока")
            
        self.players = players.copy()
        self.deck = self.create_deck()
        self.trump_suit = self.deck[-1]['suit'] if self.deck else None
        
        # Раздача карт
        self.hands = {player: [] for player in players}
        for _ in range(6):
            for player in players:
                if self.deck:
                    self.hands[player].append(self.deck.pop())
                    
        # Определение первого атакующего
        self.attacker = self.find_first_attacker()
        self.defender = self.get_next_player(self.attacker)
        self.is_started = True
        
        return {
            'type': 'game_started',
            'players': players,
            'attacker': self.attacker,
            'defender': self.defender,
            'trump_suit': self.trump_suit
        }
        
    def create_deck(self, count=36):
        """Создание колоды"""
        suits = ['♠', '♥', '♦', '♣']
        values = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [{'value': v, 'suit': s} for s in suits for v in values]
        random.shuffle(deck)
        return deck[:count]
        
    def find_first_attacker(self):
        """Поиск первого атакующего"""
        min_trump_value = float('inf')
        first_attacker = self.players[0]
        
        for player in self.players:
            for card in self.hands[player]:
                if card['suit'] == self.trump_suit:
                    card_value = self.get_card_value(card)
                    if card_value < min_trump_value:
                        min_trump_value = card_value
                        first_attacker = player
                        
        return first_attacker
        
    def get_next_player(self, current_player):
        """Получение следующего игрока"""
        try:
            current_index = self.players.index(current_player)
            next_index = (current_index + 1) % len(self.players)
            return self.players[next_index]
        except ValueError:
            return self.players[0] if self.players else None
            
    def get_card_value(self, card):
        """Получение значения карты"""
        values = {'6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return values.get(card['value'], 0)
        
    def process_move(self, player_id, move_data):
        """Обработка хода игрока"""
        # Упрощенная реализация
        return {'type': 'move_processed', 'player': player_id, 'data': move_data}
        
    def get_game_state(self):
        """Получение текущего состояния игры"""
        return {
            'game_started': self.is_started,
            'players': self.players,
            'hands_count': {p: len(cards) for p, cards in self.hands.items()},
            'table': self.table,
            'discard': len(self.discard),
            'trump_suit': self.trump_suit,
            'attacker': self.attacker,
            'defender': self.defender
        }
        
    def is_game_over(self):
        """Проверка, закончилась ли игра"""
        for player, hand in self.hands.items():
            if len(hand) == 0:
                return True
        return False