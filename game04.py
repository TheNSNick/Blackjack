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
DEFAULT_TEXT_SIZE = 18
DEFAULT_TEXT_COLOR = (255, 215, 0)
DEFAULT_FONT = 'timesnewroman'
BACKGROUND_COLOR = (0, 114, 0)
CARD_SPRITESHEET_FILE = os.path.join('gfx', 'card_front_sheet.png')
CARD_BACK_FILE = os.path.join('gfx', 'card_back_crosshatch.png')


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

    def draw(self, display, coords, card_spritesheet, card_back, hide_first=False):
        card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        card_rect = card_surface.get_rect()
        hand_total = 0
        for i, card in enumerate(self):
            if i == 0 and hide_first:
                card_surface.blit(card_back, (0, 0))
            else:
                sprite_rect = Rect((card.value-1)*(CARD_WIDTH-2), card.suit*(CARD_HEIGHT-2), CARD_WIDTH, CARD_HEIGHT)
                card_surface.blit(card_spritesheet, (0,0), sprite_rect)
                hand_total += card.face_value()
            card_rect.topleft = (coords[0]+i*CARD_OFFSET, coords[1])
            display.blit(card_surface, card_rect)
        total_surface = render_text(str(hand_total))
        total_rect = total_surface.get_rect()
        total_rect.topleft = (coords[0] + CARD_WIDTH/2, coords[1] - CARD_HEIGHT/4)
        display.blit(total_surface, total_rect)

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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    card_back = pygame.image.load(CARD_BACK_FILE).convert()
    card_sheet = pygame.image.load(CARD_SPRITESHEET_FILE).convert()
    # game loop
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        # drawing
        screen.fill(BACKGROUND_COLOR)
        pygame.display.update()
        clock.tick(FPS)


# FUNCTIONS

def generate_new_shoe(num_decks):
    new_shoe = []
    for _ in range(num_decks):
        for value in range(1, 14):
            for suit in range(4):
                new_shoe.append(Card(value, suit))
    return Dovetail.shuffle(new_shoe)


def render_text(text, color=DEFAULT_TEXT_COLOR, size=DEFAULT_TEXT_SIZE, font_name=DEFAULT_FONT):
    font = pygame.font.SysFont(font_name, size)
    return font.render(text, False, color)

# START GAME WHEN RUN
if __name__ == '__main__':
    main()
