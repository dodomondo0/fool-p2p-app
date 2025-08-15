# app/game.py
import random

class FoolGame:
    def __init__(self, mode='подкидной', card_count=36):
        self.mode = mode
        self.deck = self.create_deck(card_count)
        self.trump_suit = self.deck[-1]['suit']
        self.players = []

    def create_deck(self, count):
        suits = ['♠', '♥', '♦', '♣']
        values = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [{'value': v, 'suit': s} for s in suits for v in values]
        random.shuffle(deck)
        return deck[:count]

    def deal_cards(self, players_count=2):
        hands = [[] for _ in range(players_count)]
        for _ in range(6):
            for hand in hands:
                if self.deck:
                    hand.append(self.deck.pop())
        return hands