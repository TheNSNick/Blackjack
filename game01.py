import pygame
from pygame.locals import *
import os
import sys
import Card
import Hand
import Dovetail

# CONSTANTS
# scalars
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
FPS = 30
SHOE_NUM_DECKS = 8
SHOE_NUM_EFF_SHUFFLES = 5
CARD_WIDTH = 64
CARD_HEIGHT = 88
DEFAULT_CHIPS = 100
CARD_DEAL_NUM_FRAMES = 15
CARD_LATERAL_OFFSET = 30
# colors
GREEN = (0, 114, 0)
GOLD = (255, 215, 0)
# file names
CARD_BACK_IMAGE_FILE = os.path.join('gfx', 'card_back_crosshatch.png')
CARD_FRONT_SHEET_FILE = os.path.join('gfx', 'card_front_sheet.png')
CHIPS_FILE = os.path.join('cfg', 'config.txt')
# coordinates
INTRO_COORDS = {'header_height':100, 'below_height':350}
HAND_COORDS = {'player':(40, 400), 'dealer':(40, 200), 'shoe':(725, 225)}
TEXT_COORDS = {'chips':(20, 550), 'bet':(72, 500), 'options':(300, 300)}


def main():
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Blackjack')
    clock = pygame.time.Clock()
    # game init
    shoe = []
    player_hand = Hand.Hand()
    dealer_hand = Hand.Hand()
    game_state = 'INTRO'
    play_state = 'PLAYER'
    chip_stack = 0
    bet_amount = 1
    animation_frames = CARD_DEAL_NUM_FRAMES
    deck_spritesheet = pygame.image.load(CARD_FRONT_SHEET_FILE).convert()
    # game loop
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if game_state == 'INTRO' and (event.key == K_RETURN or event.key == K_KP_ENTER):
                    shoe = Card.generate_shoe(num_decks=SHOE_NUM_DECKS, num_shuffles=SHOE_NUM_EFF_SHUFFLES)
                    chip_stack = load_chips()
                    game_state = 'BET'
                elif game_state == 'BET':
                    if event.key == K_UP:
                        bet_amount += 1
                    elif event.key == K_DOWN:
                        bet_amount -= 1
                    elif event.key == K_LEFT:
                        bet_amount -= 5
                    elif event.key == K_RIGHT:
                        bet_amount += 5
                    if bet_amount > chip_stack:
                        bet_amount = chip_stack
                    if bet_amount < 1:
                        bet_amount = 1
                    if event.key == K_KP_ENTER or event.key == K_RETURN:
                        chip_stack -= bet_amount
                        for _ in range(2):
                            deal_player_card(screen, shoe, player_hand)
                            deal_dealer_card(screen, shoe, dealer_hand)
                        game_state = 'PLAY'
            # display
            screen.fill(GREEN)
            if game_state == 'INTRO':
                draw_intro(screen)
            elif game_state == 'BET':
                draw_bet(screen, chip_stack, bet_amount)
            elif game_state == 'PLAY':
                # vvv STAND IN FOR LATER vvv
                draw_chip_amount(screen, chip_stack)
                draw_bet_amount(screen, bet_amount)
                draw_shoe(screen)
                draw_player_hand(screen, player_hand, deck_spritesheet)
                draw_dealer_hand(screen, dealer_hand, deck_spritesheet)
                # ^^^ STAND IN FOR LATER ^^^
            # TODO -- hands, totals, options, etc
            pygame.display.update()
            clock.tick(FPS)


def draw_intro(display):
    pygame.font.init()
    header_font = pygame.font.SysFont('timesnewroman', 24, bold=True)
    header_text = 'Blackjack'
    header_surface = header_font.render(header_text, False, GOLD)
    header_rect = header_surface.get_rect()
    header_rect.midtop = (SCREEN_WIDTH / 2, INTRO_COORDS['header_height'])
    display.blit(header_surface, header_rect)
    below_font = pygame.font.SysFont('timesnewroman', 18)
    below_text = 'Press Enter to begin'
    below_surface = below_font.render(below_text, False, GOLD)
    below_rect = below_surface.get_rect()
    below_rect.midtop = (SCREEN_WIDTH / 2, INTRO_COORDS['below_height'])
    display.blit(below_surface, below_rect)


def load_chips():
    try:
        with open(CHIPS_FILE) as read_file:
            return int(read_file.read())
    except:
        with open(CHIPS_FILE, 'w') as write_file:
            write_file.write(str(DEFAULT_CHIPS))
        return load_chips()


def draw_chip_amount(display, chips):
    pygame.font.init()
    chip_font = pygame.font.SysFont('timesnewroman', 18)
    chip_text = 'Chips: {}'.format(chips)
    chip_surface = chip_font.render(chip_text, False, GOLD)
    display.blit(chip_surface, TEXT_COORDS['chips'])


def draw_bet_amount(display, bet):
    pygame.font.init()
    bet_font = pygame.font.SysFont('timesnewroman', 18)
    bet_text = 'Bet: {}'.format(bet)
    bet_surface = bet_font.render(bet_text, False, GOLD)
    display.blit(bet_surface, TEXT_COORDS['bet'])


def draw_bet(display, chips, bet):
    draw_chip_amount(display, chips)
    draw_bet_amount(display, bet)
    draw_shoe(display)
    x = TEXT_COORDS['options'][0]
    start_y = TEXT_COORDS['options'][1]
    text_coords = [(x, start_y-84), (x, start_y-56), (x, start_y-28), (x, start_y)]
    option_font = pygame.font.SysFont('timesnewroman', 18)
    up_surface = option_font.render('UP: +1', False, GOLD)
    down_surface = option_font.render('DOWN: -1', False, GOLD)
    left_surface = option_font.render('LEFT: -5', False, GOLD)
    right_surface = option_font.render('RIGHT: +5', False, GOLD)
    if bet == chips:
        display.blit(down_surface, text_coords[2])
        display.blit(left_surface, text_coords[3])
    elif bet <= 1:
        display.blit(up_surface, text_coords[2])
        display.blit(right_surface, text_coords[3])
    else:
        display.blit(up_surface, text_coords[0])
        display.blit(right_surface, text_coords[1])
        display.blit(down_surface, text_coords[2])
        display.blit(left_surface, text_coords[3])


def draw_dealing_card(display, current_frame, dealing_to, hand_size):
    if dealing_to == 'PLAYER':
        end_x, end_y  = HAND_COORDS['player']
    elif dealing_to == 'DEALER':
        end_x, end_y = HAND_COORDS['dealer']
    else:
        raise ValueError('draw_dealing_card(): Invalid \'dealing_to\' param passed.')
    start_x, start_y = HAND_COORDS['shoe']
    start_x += 30 * hand_size
    delta_x = (end_x - start_x) / CARD_DEAL_NUM_FRAMES
    draw_x = start_x + delta_x * current_frame
    delta_y = (end_y - start_y) / CARD_DEAL_NUM_FRAMES
    draw_y = start_y + delta_y * current_frame
    card_surface = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()
    display.blit(card_surface, (draw_x, draw_y))
    current_frame -= 1
    if current_frame > 0:
        draw_dealing_card(display, current_frame, dealing_to, hand_size)


def deal_player_card(display, deck, player):
    frames = CARD_DEAL_NUM_FRAMES
    while frames > 0:
        draw_dealing_card(display, frames, 'PLAYER', len(player))
        frames -= 1
    player.add_card(deck.pop(0))


def deal_dealer_card(display, deck, dealer):
    frames = CARD_DEAL_NUM_FRAMES
    while frames > 0:
        draw_dealing_card(display, frames, 'DEALER', len(dealer))
        frames -= 1
    dealer.add_card(deck.pop(0))


def draw_player_card(display, card, spritesheet, x_offset):
    card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    card_subrect = Rect((card.value-1)*(CARD_WIDTH-2), card.suit * (CARD_HEIGHT - 2), CARD_WIDTH, CARD_HEIGHT)
    card_surface.blit(spritesheet, (0, 0), card_subrect)
    display.blit(card_surface, (HAND_COORDS['player'][0] + x_offset*CARD_LATERAL_OFFSET, HAND_COORDS['player'][1]))


def draw_player_hand(display, player, spritesheet):
    num_card = 0
    for card in player:
        draw_player_card(display, card, spritesheet, num_card)


def draw_dealer_card(display, card, spritesheet, x_offset):
    if x_offset == 0:
        card_surface = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()
    else:
        card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        card_subrect = Rect((card.value-1)*(CARD_WIDTH-2), card.suit * (CARD_HEIGHT - 2), CARD_WIDTH, CARD_HEIGHT)
        card_surface.blit(spritesheet, (0, 0), card_subrect)
    display.blit(card_surface, (HAND_COORDS['dealer'][0] + x_offset*CARD_LATERAL_OFFSET, HAND_COORDS['dealer'][1]))


def draw_dealer_hand(display, dealer, spritesheet):
    num_card = 0
    for card in dealer:
        draw_dealer_card(display, card, spritesheet, num_card)


def draw_shoe(display):
    shoe_surface = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()
    display.blit(shoe_surface, HAND_COORDS['shoe'])

if __name__ == '__main__':
    main()
