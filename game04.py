import os
import sys
import Dovetail
import pygame
from pygame.locals import *

# CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
CARD_WIDTH = 64
CARD_HEIGHT = 88
CARD_OFFSET = 30
NUM_DECKS = 8
CUT_DEPTH = 25
DEFAULT_CHIP_NUM = 100


# CLASSES
class Card:

    def __init__(self, value, suit):
        assert int(value) in range(1, 14), 'Invalid value.'
        assert int(suit) in range(4), 'Invalid suit.'
        self.value = int(value)
        self.suit = int(suit)

    def face_value(self):
        if self.value < 10:
            return self.value
        else:
            return 10


class Hand:

    def __init__(self):
        self.cards = []

    def __iter__(self):
        return self.cards.__iter__()

    def __len__(self):
        return len(self.cards)

    def __lt__(self, other_hand):
        assert isinstance(other_hand, Hand)
        return self.value() < other_hand.value()

    def __eq__(self, other_hand):
        assert isinstance(other_hand, Hand)
        return self.value() == other_hand.value()

    def add_card(self, new_card):
        assert isinstance(new_card, Card)
        self.cards.append(new_card)

    def can_double(self):
        return len(self) == 2

    def can_split(self):
        if len(self) == 2:
            if self.cards[0].value == self.cards[1].value:
                return True
        return False

    def clear(self):
        self.cards = []

    def is_blackjack(self):
        return len(self) == 2 and self.value() == 21

    def is_bust(self):
        return self.value > 21

    def value(self):
        if len(self) == 0:
            return 0
        else:
            ace = False
            val = 0
            for card in self:
                val += card.face_value()
                if card.face_value() == 1:
                    ace = True
            if ace and val <= 11:
                val += 10
            return val


# MAIN GAME
def main():
    # init
    pygame.init()
    # game loop
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


# FUNCTIONS

def generate_new_shoe(num_decks):
    new_shoe = []
    for _ in range(num_decks):
        for value in range(1, 14):
            for suit in range(4):
                new_shoe.append(Card(value, suit))
    return Dovetail.shuffle(new_shoe)


# START GAME WHEN RUN
if __name__ == '__main__':
    main()
