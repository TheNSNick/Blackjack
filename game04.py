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
CHIPS_FILE = os.path.join('cfg', 'chips.dat')
PLAYER_HAND_COORDS = (10, 400)
DEALER_HAND_COORDS = (10, 200)


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
        total_surface = render_text(str(self.value(hide_first=hide_first)))
        total_rect = total_surface.get_rect()
        total_rect.topleft = (coords[0] + CARD_WIDTH/2, coords[1] - CARD_HEIGHT/4)
        display.blit(total_surface, total_rect)

    def is_blackjack(self):
        return len(self) == 2 and self.value() == 21

    def is_bust(self):
        return self.value > 21

    def value(self, hide_first=False):
        if len(self) == 0:
            return 0
        else:
            ace = False
            val = 0
            for i, card in enumerate(self):
                if i > 0 or not hide_first:
                    val += card.face_value()
                    if card.face_value() == 1:
                        ace = True
            if ace and val <= 11:
                val += 10
            return val


class Player:

    def __init__(self, chips):
        self.hand = Hand()
        self.chips = int(chips)
        self.bet = 0
        self.is_playing = False
        self.split = None

    def adjust_bet(self, adjustment):
        self.bet += int(adjustment)
        if self.bet > self.chips:
            self.bet = self.chips
        if self.bet < 0:
            self.bet = 0

    def double_bet(self):
        if self.chips >= self.bet:
            self.chips -= self.bet
            self.bet += self.bet
            return True
        else:
            return False

    def draw_bet(self, display, coords):
        bet_surf = render_text('Bet: {}'.format(self.bet))
        bet_rect = bet_surf.get_rect()
        bet_rect.topleft = coords
        display.blit(bet_surf, bet_rect)

    def draw_chips(self, display, coords):
        chip_surf = render_text('Chips: {}'.format(self.chips))
        chip_rect = chip_surf.get_rect()
        chip_rect.topleft = coords
        display.blit(chip_surf, chip_rect)

    def make_bet(self):
        if self.chips >= self.bet:
            self.chips -= self.bet
            return True
        else:
            return False


# MAIN GAME
def main():
    # init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    state = 'INTRO'
    card_back = pygame.image.load(CARD_BACK_FILE).convert()
    card_sheet = pygame.image.load(CARD_SPRITESHEET_FILE).convert()
    shoe = generate_new_shoe(NUM_DECKS)
    player = Player(load_chips())
    dealer = Hand()
    # game loop
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    if state == 'INTRO':
                        state = 'BET'
                    elif state == 'BET':
                        if player.make_bet():
                            for _ in range(2):
                                player.hand.add_card(shoe.pop())
                                dealer.add_card(shoe.pop())
                        state = 'PLAY'
                    elif state == 'SHOWDOWN':
                        player.hand.clear()
                        dealer.clear()
                        if len(shoe) < 20:
                            shoe = generate_new_shoe(NUM_DECKS)
                        state = 'BET'
                if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
                    if state == 'BET':
                        amounts = {K_UP: 5, K_DOWN: -5, K_LEFT: -1, K_RIGHT: 1}
                        player.adjust_bet(amounts[event.key])
                if state == 'PLAY':
                    if event.key == K_h:
                        player.hand.add_card(shoe.pop())
                        if player.hand.is_bust():
                            state = 'SHOWDOWN'
                    elif event.key == K_s:
                        state = 'DEALER'
        # drawing
        screen.fill(BACKGROUND_COLOR)
        if state == 'INTRO':
            draw_intro(screen)
        if state != 'INTRO':
            bet_coords = (PLAYER_HAND_COORDS[0] + CARD_WIDTH / 2, PLAYER_HAND_COORDS[1] + 5 * CARD_HEIGHT / 4)
            player.draw_bet(screen, bet_coords)
            chip_coords = (PLAYER_HAND_COORDS[0] + 2 * CARD_WIDTH, PLAYER_HAND_COORDS[1] + 5 * CARD_HEIGHT / 4)
            player.draw_chips(screen, chip_coords)
        if state == 'PLAY':
            player.hand.draw(screen, PLAYER_HAND_COORDS, card_sheet, card_back)
            dealer.draw(screen, DEALER_HAND_COORDS, card_sheet, card_back, hide_first=True)
        if state == 'DEALER' or state == 'SHOWDOWN':
            player.hand.draw(screen, PLAYER_HAND_COORDS, card_sheet, card_back)
            dealer.draw(screen, DEALER_HAND_COORDS, card_sheet, card_back)
        pygame.display.update()
        clock.tick(FPS)
        # dealer action
        if state == 'DEALER':
            pygame.time.wait(333)
            if dealer.value() >= 17:
                state = 'SHOWDOWN'
                if dealer.value() > 21 or dealer.value() < player.hand.value():
                    player.chips += 2 * player.bet
                elif dealer.value() == player.hand.value():
                    player.chips += player.bet
            else:
                dealer.add_card(shoe.pop())


# FUNCTIONS

def draw_intro(display):
    intro_surf = render_text('Blackjack', size=36)
    intro_rect = intro_surf.get_rect()
    intro_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    display.blit(intro_surf, intro_rect)


def generate_new_shoe(num_decks):
    new_shoe = []
    for _ in range(num_decks):
        for value in range(1, 14):
            for suit in range(4):
                new_shoe.append(Card(value, suit))
    return Dovetail.shuffle(new_shoe)


def load_chips():
    try:
        with open(CHIPS_FILE, 'r') as infile:
            return int(infile.read())
    except:
        write_chips(DEFAULT_CHIP_NUM)
        return load_chips()


def render_text(text, text_color=DEFAULT_TEXT_COLOR, size=DEFAULT_TEXT_SIZE, font_name=DEFAULT_FONT):
    font = pygame.font.SysFont(font_name, size)
    return font.render(text, False, text_color)


def terminate():
    pygame.quit()
    sys.exit()


def write_chips(chip_amt):
    with open(CHIPS_FILE, 'w') as outfile:
        outfile.write(str(chip_amt))

# START GAME WHEN RUN
if __name__ == '__main__':
    main()
