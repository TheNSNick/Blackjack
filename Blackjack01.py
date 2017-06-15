import sys
import os
import Card01
import Player01
import Dovetail
import pygame
from pygame.locals import *

# CONSTANTS
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
FPS = 30
SHOE_SIZE = 8
CARD_DEAL_FRAMES = 30
COLORS = {'BACKGROUND': (0, 114, 0),
          'TEXT': (255, 215, 0)}
COORDS = {'SHOE': (725, 225),
          'PLAYER': (40, 400),
          'DEALER': (40, 150)}
CHIPS_FILE = os.path.join('cfg', 'chips.txt')


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    shoe = generate_decks(SHOE_SIZE, coords=COORDS['SHOE'])
    player = Player01.Player(COORDS['PLAYER'])
    dealer = Player01.Player(COORDS['DEALER'])
    all = [player, dealer]
    chips = load_chips()
    # TESTING
    deal_card(screen, player, all, shoe, clock)
    deal_card(screen, dealer, all, shoe, clock, flip=False)
    deal_card(screen, player, all, shoe, clock)
    deal_card(screen, dealer, all, shoe, clock)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(COLORS['BACKGROUND'])
        draw_deck(screen, shoe)
        for group in all:
            group.draw(screen)
        pygame.display.update()
        clock.tick(FPS)


def deal_card(display, to_player, all_players, deck, clock, flip=True):
    if to_player:
        end_x = len(to_player) * Player01.CARD_WIDTH + Player01.CARD_WIDTH / 2
    else:
        end_x = Player01.CARD_WIDTH / 2
    step_x = (deck[0].rect.left - end_x) / CARD_DEAL_FRAMES
    step_y = (deck[0].rect.top - to_player.coords[1]) / CARD_DEAL_FRAMES
    for _ in range(CARD_DEAL_FRAMES):
        deck[0].rect.left -= step_x
        deck[0].rect.top -= step_y
        display.fill(COLORS['BACKGROUND'])
        draw_deck(display, deck)
        to_player.draw(display)
        for player in all_players:
            player.draw(display)
        pygame.display.update()
        clock.tick(FPS)
    to_player.add_card(deck.pop(0), flip=flip)


def draw_deck(display, deck):
    if len(deck) > 1:
        display.blit(deck[1].image, deck[1].rect)
    if len(deck) > 0:
        display.blit(deck[0].image, deck[0].rect)


def generate_decks(num, coords=(0,0)):
    decks = []
    for _ in range(num):
        for v in range(1, 14):
            for s in range(4):
                decks.append(Card01.Card(v, s, face_up=False, start_coords=coords))
    return Dovetail.shuffle(decks)


def load_chips():
    with open(CHIPS_FILE, 'r') as readfile:
        return int(readfile.read())


def write_chips(num_chips):
    with open(CHIPS_FILE, 'w') as writefile:
        writefile.write(str(num_chips))

if __name__ == '__main__':
    main()
