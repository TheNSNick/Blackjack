import pygame
from pygame.locals import *
import os
import sys
import Card
import Hand
import Dovetail

# CONSTANTS
# dimensions & other scalars
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
SHOE_NUM_DECKS = 8
SHOE_NUM_EFF_SHUFFLES = 5
CARD_WIDTH = 64
CARD_HEIGHT = 88
DEFAULT_CHIPS = 100
FONT_NAME = 'timesnewroman'
FONT_HEADER_SIZE = 24
FONT_SUBTEXT_SIZE = 18
FONT_BET_SIZE = 18
FONT_CHIP_SIZE = 18
FONT_TOTAL_SIZE = 22
CARD_DEAL_ANIM_FRAMES = 15
DEALER_DELAY_MSEC = 500
CARD_LATERAL_OFFSET = 3*SCREEN_WIDTH/80
# colors
GREEN = (0, 114, 0)
GOLD = (255, 215, 0)
# file names
FILE_NAMES = {'CARD_BACK': os.path.join('gfx', 'card_back_crosshatch.png'),
              'CARD_SHEET': os.path.join('gfx', 'card_front_sheet.png'),
              'CHIPS': os.path.join('cfg', 'config.txt')
              }
# text
TEXT = {'CAPTION': 'Blackjack',
        'INTRO_HEADER': 'Blackjack',
        'INTRO_TEXT': 'Press Enter to begin',
        'BET': 'Bet: ',
        'CHIP': 'Chips: ',
        'BET_UPS': ['UP: +1', 'RIGHT: +5'],
        'BET_DOWNS': ['DOWN: -1', 'LEFT: -5'],
        'PLAY_HIT': '[H]it',
        'PLAY_STAND': '[S]tand',
        'PLAY_DOUBLE': '[D]ouble',
        'PLAY_SPLIT': 's[P]lit',
        'RESULT_WIN': 'WIN',
        'RESULT_PUSH': 'PUSH',
        'RESULT_BJ': 'BLACKJACK!',
        'RESULT_LOSE': 'LOSS',
        'RESULT_BUST': 'BUST',
        'SHOWDOWN': 'Press Enter'
        }
# coordinates
COORDS = {'INTRO_HEADER': (SCREEN_WIDTH/2, SCREEN_HEIGHT/6),
          'INTRO_TEXT': (SCREEN_WIDTH/2, 7*SCREEN_HEIGHT/12),
          'BET_TEXT': (21*SCREEN_WIDTH/200, 5*SCREEN_HEIGHT/6),
          'CHIP_TEXT': (21*SCREEN_WIDTH/200, 5*SCREEN_HEIGHT/6+FONT_BET_SIZE+SCREEN_HEIGHT/120),
          'BET_OPTIONS': [(7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2-3*FONT_BET_SIZE-3*SCREEN_HEIGHT/60),
                          (7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2-2*FONT_BET_SIZE-2*SCREEN_HEIGHT/60),
                          (7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2-FONT_BET_SIZE-SCREEN_HEIGHT/60),
                          (7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2)
                          ],
          'PLAY_OPTIONS': [(7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2-3*FONT_BET_SIZE-3*SCREEN_HEIGHT/60),
                          (7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2-2*FONT_BET_SIZE-2*SCREEN_HEIGHT/60),
                          (7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2-FONT_BET_SIZE-SCREEN_HEIGHT/60),
                          (7*SCREEN_HEIGHT/8, SCREEN_HEIGHT/2)
                           ],
          'DEALER_HAND': (SCREEN_WIDTH/20, SCREEN_HEIGHT/6),
          'PLAYER_HAND': (SCREEN_WIDTH/20, 7*SCREEN_HEIGHT/12),
          'SPLIT_HAND': (SCREEN_WIDTH/2, 7*SCREEN_HEIGHT/12),
          'DEALER_TOTAL': (SCREEN_WIDTH/10, SCREEN_HEIGHT/6-FONT_TOTAL_SIZE-5),
          'PLAYER_TOTAL': (SCREEN_WIDTH/10, 7*SCREEN_HEIGHT/12-FONT_TOTAL_SIZE-5),
          'SPLIT_TOTAL': (11*SCREEN_WIDTH/20, 7*SCREEN_HEIGHT/12-FONT_TOTAL_SIZE-5),
          'RESULT': (3*SCREEN_WIDTH/20, 7*SCREEN_HEIGHT/12-FONT_TOTAL_SIZE-5),
          'SPLIT_RESULT': (6*SCREEN_WIDTH/10, 7*SCREEN_HEIGHT/12-FONT_TOTAL_SIZE-5),
          'SHOE': (29*SCREEN_WIDTH/32, 5*SCREEN_HEIGHT/24)
          }


def main():
    # init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TEXT['CAPTION'])
    clock = pygame.time.Clock()
    state = 'INTRO'
    phase = 'PLAYER'
    chips = -1
    bet = 1
    player = Hand.Hand()
    dealer = Hand.Hand()
    split = Hand.Hand()
    is_split = False
    shoe = generate_shoe(SHOE_NUM_DECKS, SHOE_NUM_EFF_SHUFFLES)
    card_back = pygame.image.load(FILE_NAMES['CARD_BACK']).convert()
    card_spritesheet = pygame.image.load(FILE_NAMES['CARD_SHEET']).convert()
    # loop
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if state == 'INTRO' and (event.key == K_RETURN or event.key == K_KP_ENTER):
                    chips = load_chips()
                    state = 'BET'
                elif state == 'BET':
                    if event.key == K_UP:
                        bet = adjust_bet(1, bet, chips)
                    if event.key == K_DOWN:
                        bet = adjust_bet(-1, bet, chips)
                    if event.key == K_LEFT:
                        bet = adjust_bet(-5, bet, chips)
                    if event.key == K_RIGHT:
                        bet = adjust_bet(5, bet, chips)
                    if event.key == K_RETURN or event.key == K_KP_ENTER:
                        state = 'PLAY'
                        chips -= bet
                        for i in range(2):
                            draw_card_deal_animation(screen, state, phase, is_split, bet, chips, 'PLAYER', player, dealer, split, card_spritesheet, clock)
                            player.add_card(shoe.pop(0))
                            draw_card_deal_animation(screen, state, phase, is_split, bet, chips, 'DEALER', player, dealer, split, card_spritesheet, clock)
                            dealer.add_card(shoe.pop(0))
                elif state == 'PLAY' and phase == 'PLAYER':
                    if event.key == K_h:
                        if phase == 'PLAYER':
                            draw_card_deal_animation(screen, state, phase, is_split, bet, chips, 'PLAYER', player, dealer, split, card_spritesheet, clock)
                            player.add_card(shoe.pop(0))
                            if player.is_bust():
                                if is_split:
                                    state = 'SPLIT'
                                else:
                                    state = 'SHOWDOWN'
                                    chips += pay_hand(player, dealer, bet)
                        elif phase == 'SPLIT':
                            draw_card_deal_animation(screen, state, phase, is_split, bet, chips, 'SPLIT', player, dealer, split, card_spritesheet, clock)
                            split.add_card(shoe.pop(0))
                            if split.is_bust():
                                state = 'SHOWDOWN'
                                chips += pay_hand(player, dealer, bet/2)
                                chips += pay_hand(split, dealer, bet/2)
                    if event.key == K_s:
                        if is_split and phase == 'PLAYER':
                            phase = 'SPLIT'
                        else:
                            phase = 'DEALER'
                    if event.key == K_d and player.can_double() and not is_split:
                        chips -= bet
                        bet += bet
                        draw_card_deal_animation(screen, state, phase, is_split, bet, chips, 'PLAYER', player, dealer, split, card_spritesheet, clock)
                        player.add_card(shoe.pop(0))
                        if player.is_bust():
                            state = 'SHOWDOWN'
                            chips += pay_hand(player, dealer, bet)
                        else:
                            phase = 'DEALER'
                    if event.key == K_p and player.can_split() and not is_split:
                        if chips >= bet:
                            chips -= bet
                            bet += bet
                            split.add_card(player.split())
                            is_split = True
                elif state == 'SHOWDOWN' and (event.key == K_RETURN or event.key == K_KP_ENTER):
                    phase = 'PLAYER'
                    player.clear()
                    dealer.clear()
                    write_chips(chips)
                    state = 'BET'
                    bet = adjust_bet(0, bet, chips)
        # drawing and clock
        screen.fill(GREEN)
        if state == 'INTRO':
            draw_intro(screen)
        elif state == 'BET':
            draw_bet_screen(screen, bet, chips)
        elif state == 'PLAY':
            draw_play_screen(screen, phase, is_split, bet, chips, player, dealer, split, card_spritesheet)
        elif state == 'SHOWDOWN':
            draw_showdown_screen(screen, is_split, bet, chips, player, dealer, split, card_spritesheet)
        pygame.display.update()
        clock.tick(FPS)
        # dealer play
        if state == 'PLAY' and phase == 'DEALER':
            pygame.time.delay(DEALER_DELAY_MSEC)
            if dealer.bj_value() < 17:
                draw_card_deal_animation(screen, state, phase, is_split, bet, chips, 'DEALER', player, dealer, split, card_spritesheet, clock)
                dealer.add_card(shoe.pop(0))
            else:
                state = 'SHOWDOWN'
                chips += pay_hand(player, dealer, bet)


def draw_intro(display):
    header_surface = render_text_surface(TEXT['INTRO_HEADER'], FONT_HEADER_SIZE, bold=True)
    header_rect = header_surface.get_rect()
    header_rect.center = COORDS['INTRO_HEADER']
    display.blit(header_surface, header_rect)
    subtext_surface = render_text_surface(TEXT['INTRO_TEXT'], FONT_SUBTEXT_SIZE)
    subtext_rect = subtext_surface.get_rect()
    subtext_rect.center = COORDS['INTRO_TEXT']
    display.blit(subtext_surface, subtext_rect)


def draw_bet_amount(display, num_bet):
    bet_surface = render_text_surface(TEXT['BET']+str(num_bet), FONT_BET_SIZE)
    bet_rect = bet_surface.get_rect()
    bet_rect.midright = COORDS['BET_TEXT']
    display.blit(bet_surface, bet_rect)


def draw_chip_amount(display, num_chips):
    chip_surface = render_text_surface(TEXT['CHIP']+str(num_chips), FONT_CHIP_SIZE)
    chip_rect = chip_surface.get_rect()
    chip_rect.midright = COORDS['CHIP_TEXT']
    display.blit(chip_surface, chip_rect)


def draw_total_amounts(display, game_phase, split_flag, player_hand, dealer_hand, split_hand):
    player_total_surface = render_text_surface(str(player_hand.bj_value()), FONT_TOTAL_SIZE)
    player_total_rect = player_total_surface.get_rect()
    player_total_rect.topleft = COORDS['PLAYER_TOTAL']
    display.blit(player_total_surface, player_total_rect)
    if game_phase == 'PLAYER':
        hide = True
    else:
        hide = False
    dealer_total_surface = render_text_surface(str(dealer_hand.bj_value(dealer_hide=hide)), FONT_TOTAL_SIZE)
    dealer_total_rect = dealer_total_surface.get_rect()
    dealer_total_rect.topleft = COORDS['DEALER_TOTAL']
    display.blit(dealer_total_surface, dealer_total_rect)
    if split_flag:
        split_total_surface = render_text_surface(str(split_hand.bj_value()), FONT_TOTAL_SIZE)
        split_total_rect = split_total_surface.get_rect()
        split_total_rect.topleft = COORDS['SPLIT_TOTAL']
        display.blit(split_total_surface, split_total_rect)


def draw_bet_screen(display, num_bet, num_chips):
    draw_chip_amount(display, num_chips)
    draw_bet_amount(display, num_bet)
    draw_shoe(display)
    valid_bet_options = []
    if num_bet < num_chips:
        valid_bet_options.extend(TEXT['BET_UPS'])
    if num_bet > 1:
        valid_bet_options.extend(TEXT['BET_DOWNS'])
    for i in range(len(valid_bet_options)):
        rev_index = len(valid_bet_options) - i - 1
        option_surface = render_text_surface(valid_bet_options[rev_index], FONT_SUBTEXT_SIZE)
        option_rect = option_surface.get_rect()
        option_rect.midleft = COORDS['BET_OPTIONS'][rev_index]
        display.blit(option_surface, option_rect)


def draw_play_screen(display, game_phase, split_flag, num_bet, num_chips, player_hand, dealer_hand, split_hand, card_sheet):
    draw_chip_amount(display, num_chips)
    draw_bet_amount(display, num_bet)
    draw_shoe(display)
    draw_player_hand(display, player_hand, card_sheet)
    draw_dealer_hand(display, dealer_hand, game_phase, card_sheet)
    if split_flag:
        draw_split_hand(display, split_hand, card_sheet)
    draw_total_amounts(display, game_phase, split_flag, player_hand, dealer_hand, split_hand)
    if game_phase == 'PLAYER' or game_phase == 'SPLIT':
        draw_play_options(display, player_hand, split_flag)


def draw_showdown_screen(display, split_flag, num_bet, num_chips, player_hand, dealer_hand, split_hand, card_sheet):
    draw_shoe(display)
    draw_player_hand(display, player_hand, card_sheet)
    draw_dealer_hand(display, dealer_hand, 'DEALER', card_sheet)
    draw_total_amounts(display, 'SHOWDOWN', split_flag, player_hand, dealer_hand, split_hand)
    draw_bet_amount(display, num_bet)
    draw_chip_amount(display, num_chips)
    if player_hand.is_bust():
        result_text = TEXT['RESULT_BUST']
    elif player_hand.bj_value() == dealer_hand.bj_value():
        result_text = TEXT['RESULT_PUSH']
    elif player_hand.blackjack():
        result_text = TEXT['RESULT_BJ']
    elif player_hand.bj_value() > dealer_hand.bj_value() or dealer_hand.is_bust():
        result_text = TEXT['RESULT_WIN']
    else:
        result_text = TEXT['RESULT_LOSE']
    result_surface = render_text_surface(result_text, FONT_SUBTEXT_SIZE)
    result_rect = result_surface.get_rect()
    result_rect.midleft = COORDS['RESULT']
    display.blit(result_surface, result_rect)
    subtext_surface = render_text_surface(TEXT['SHOWDOWN'], FONT_SUBTEXT_SIZE)
    subtext_rect = subtext_surface.get_rect()
    subtext_rect.midleft = COORDS['BET_OPTIONS'][3]
    display.blit(subtext_surface, subtext_rect)


def draw_play_options(display, player_hand, split_flag):
    valid_play_options = [TEXT['PLAY_HIT'], TEXT['PLAY_STAND']]
    if player_hand.can_double():
        valid_play_options.append(TEXT['PLAY_DOUBLE'])
    if player_hand.can_split() and not split_flag:
        valid_play_options.append(TEXT['PLAY_SPLIT'])
    for i in range(len(valid_play_options)):
        rev_index = len(valid_play_options) - i - 1
        option_surface = render_text_surface(valid_play_options[rev_index], FONT_SUBTEXT_SIZE)
        option_rect = option_surface.get_rect()
        option_rect.midleft = COORDS['BET_OPTIONS'][rev_index]
        display.blit(option_surface, option_rect)


def get_card_image(card, sheet):
    card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    card_subrect = Rect((card.value-1)*(CARD_WIDTH-2), card.suit*(CARD_HEIGHT-2), CARD_WIDTH, CARD_HEIGHT)
    card_surface.blit(sheet, (0, 0), card_subrect)
    return card_surface


def draw_shoe(display):
    shoe_surface = pygame.image.load(FILE_NAMES['CARD_BACK']).convert()
    shoe_rect = shoe_surface.get_rect()
    shoe_rect.topleft = COORDS['SHOE']
    display.blit(shoe_surface, shoe_rect)


def draw_dealer_hand(display, dealer_hand, game_phase, card_sheet):
    card_num = 0
    for card in dealer_hand:
        if card_num == 0 and game_phase == 'PLAYER':
            card_surface = pygame.image.load(FILE_NAMES['CARD_BACK']).convert()
        else:
            card_surface = get_card_image(card, card_sheet)
        card_x = COORDS['DEALER_HAND'][0] + card_num * CARD_LATERAL_OFFSET
        card_rect = card_surface.get_rect()
        card_rect.topleft = (card_x, COORDS['DEALER_HAND'][1])
        display.blit(card_surface, card_rect)
        card_num += 1


def draw_player_hand(display, player_hand, card_sheet):
    card_num = 0
    for card in player_hand:
        card_surface = get_card_image(card, card_sheet)
        card_x = COORDS['PLAYER_HAND'][0] + card_num * CARD_LATERAL_OFFSET
        card_rect = card_surface.get_rect()
        card_rect.topleft = (card_x, COORDS['PLAYER_HAND'][1])
        display.blit(card_surface, card_rect)
        card_num += 1


def draw_split_hand(display, split_hand, card_sheet):
    card_num = 0
    for card in split_hand:
        card_surface = get_card_image(card, card_sheet)
        card_x = COORDS['SPLIT_HAND'][0] + card_num * CARD_LATERAL_OFFSET
        card_rect = card_surface.get_rect()
        card_rect.topleft = (card_x, COORDS['SPLIT_HAND'][1])
        display.blit(card_surface, card_rect)
        card_num += 1


def draw_card_deal_animation(display, game_state, game_phase, split_flag, num_bet, num_chips, deal_to, player_hand, dealer_hand, split_hand, card_sheet, clock):
    if deal_to == 'PLAYER':
        end_x = COORDS['PLAYER_HAND'][0] + (len(player_hand)-1)*CARD_LATERAL_OFFSET
        end_y = COORDS['PLAYER_HAND'][1]
    elif deal_to == 'DEALER':
        end_x = COORDS['DEALER_HAND'][0] + (len(dealer_hand)-1)*CARD_LATERAL_OFFSET
        end_y = COORDS['DEALER_HAND'][1]
    elif deal_to == 'SPLIT':
        end_x = COORDS['SPLIT_HAND'][0] + (len(split_hand)-1)*CARD_LATERAL_OFFSET
        end_y = COORDS['SPLIT_HAND'][1]
    step_x = (end_x - COORDS['SHOE'][0]) / CARD_DEAL_ANIM_FRAMES
    step_y = (end_y - COORDS['SHOE'][1]) / CARD_DEAL_ANIM_FRAMES
    card_back_surface = pygame.image.load(FILE_NAMES['CARD_BACK']).convert()
    card_back_rect = card_back_surface.get_rect()
    for i in range(CARD_DEAL_ANIM_FRAMES):
        display.fill(GREEN)
        if game_state == 'BET':
            draw_bet_screen(display, num_bet, num_chips)
        elif game_state == 'PLAY':
            draw_play_screen(display, game_phase, split_flag, num_bet, num_chips, player_hand, dealer_hand, split_hand, card_sheet)
        card_back_rect.topleft = (COORDS['SHOE'][0]+i*step_x, COORDS['SHOE'][1]+i*step_y)
        display.blit(card_back_surface, card_back_rect)
        pygame.display.update()
        clock.tick(FPS)


def generate_shoe(num_decks=1, num_shuffles=3):
    new_shoe = []
    for _ in range(num_decks):
        for v in range(1, 14):
            for s in range(4):
                new_shoe.append(Card.Card(v, s))
    return Dovetail.shuffle(new_shoe, eff_shuffles=num_shuffles)


def load_chips():
    try:
        with open(FILE_NAMES['CHIPS']) as read_file:
            return int(read_file.read())
    except:
        write_chips(DEFAULT_CHIPS)
        return load_chips()


def write_chips(num_chips):
    with open(FILE_NAMES['CHIPS'], 'w') as write_file:
        write_file.write(str(num_chips))


def adjust_bet(change, current_bet, num_chips):
    new_bet = current_bet + change
    if new_bet > num_chips:
        new_bet = num_chips
    if new_bet <= 0:
        new_bet = 1
    return new_bet


def pay_hand(player_hand, dealer_hand, num_bet):
    if player_hand.is_bust():
        return 0
    elif player_hand.bj_value() == dealer_hand.bj_value():
        return num_bet
    elif player_hand.blackjack():
        return 5*num_bet/2
    elif player_hand.bj_value() > dealer_hand.bj_value() or dealer_hand.is_bust():
        return 2*num_bet
    else:
        return 0


def render_text_surface(text, size, color=GOLD, font=FONT_NAME, bold=False):
    pygame.font.init()
    render_font = pygame.font.SysFont(font, size, bold=bold)
    return render_font.render(text, False, color)

if __name__ == '__main__':
    main()
