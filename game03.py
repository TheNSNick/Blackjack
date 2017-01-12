import os
import sys
import Card
import Hand
import Dovetail
import pygame
from pygame.locals import *
# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
CARD_WIDTH = 64
CARD_HEIGHT = 88
CARD_OFFSET = 30
SHOE_NUM_DECKS = 8
SHOE_CUT_DEPTH = 25
CHIP_DEFAULT_NUM = 100
DEAL_ANIM_FRAMES = 15
DEALER_DELAY = 500
COLORS = {'GREEN': (0, 114, 0),
          'GOLD': (255, 215, 0),
          }
COORDS = {'INTRO_HEADER': (SCREEN_WIDTH/2, SCREEN_HEIGHT/6),
          'INTRO_SUBTEXT': (SCREEN_WIDTH/2, 7*SCREEN_HEIGHT/12),
          'DEALER_HAND': (SCREEN_WIDTH/20, SCREEN_HEIGHT/6),
          'PLAYER_HAND': (SCREEN_WIDTH/20, 7*SCREEN_HEIGHT/12),
          'SPLIT_HAND': (SCREEN_WIDTH/2, 7*SCREEN_HEIGHT/12),
          'DEALER_TOTAL': (SCREEN_WIDTH/10, SCREEN_HEIGHT/6-27),
          'PLAYER_TOTAL': (SCREEN_WIDTH/10, 7*SCREEN_HEIGHT/12-22-SCREEN_HEIGHT/120),
          'SPLIT_TOTAL': (11*SCREEN_WIDTH/20, 7*SCREEN_HEIGHT/12-22-SCREEN_HEIGHT/120),
          'BET_DISPLAY': (21*SCREEN_WIDTH/200, 5*SCREEN_HEIGHT/6),
          'SPLIT_BET_DISPLAY': (121*SCREEN_WIDTH/200, 5*SCREEN_HEIGHT/6),
          'CHIPS_DISPLAY': (21*SCREEN_WIDTH/200, 5*SCREEN_HEIGHT/6+18+SCREEN_HEIGHT/120),
          'RESULT': (3*SCREEN_WIDTH/20, 7*SCREEN_HEIGHT/12-22-SCREEN_HEIGHT/120),
          'SPLIT_RESULT': (6*SCREEN_WIDTH/10, 7*SCREEN_HEIGHT/12-22-SCREEN_HEIGHT/120),
          'SHOE': (29*SCREEN_WIDTH/32, 5*SCREEN_HEIGHT/24),
          'INSURANCE': (SCREEN_HEIGHT/2, 5*SCREEN_HEIGHT/12),
          'INSURE_ASK': (SCREEN_HEIGHT/2, 5*SCREEN_HEIGHT/12+22+SCREEN_HEIGHT/120),
          'OPTION_TOP_LEFT': (SCREEN_WIDTH/3, 5*SCREEN_HEIGHT/12),
          'OPTION_BOTTOM_LEFT': (SCREEN_WIDTH/3, 5*SCREEN_HEIGHT/12+18+SCREEN_HEIGHT/120),
          'OPTION_TOP_RIGHT': (SCREEN_WIDTH/2, 5*SCREEN_HEIGHT/12),
          'OPTION_BOTTOM_RIGHT': (SCREEN_WIDTH/2, 5*SCREEN_HEIGHT/12+18+SCREEN_HEIGHT/120)
          }
TEXT = {'CAPTION': 'Blackjack',
        'INTRO_HEADER': 'Blackjack',
        'INTRO_SUBTEXT': 'Press Enter to begin',
        'INSURANCE': 'Would you like insurance?',
        'INSURE_ASK': 'Y / N',
        'HIT': '[H]it',
        'STAND': '[S]tand',
        'DOUBLE': '[D]ouble',
        'SPLIT': 's[P]lit'
        }
FONT_SIZES = {'INTRO_HEADER': 24,
              'INTRO_SUBTEXT': 18,
              'TOTALS': 22,
              'INSURANCE': 22,
              'OTHER': 18,
              }
FILE_NAMES = {'CHIP_AMOUNT': os.path.join('cfg', 'chips.txt'),
              'CARD_BACK': os.path.join('gfx', 'card_back_crosshatch.png'),
              'CARD_SPRITESHEET': os.path.join('gfx', 'card_front_sheet.png'),
              }
IMAGES = {'CARD_BACK': None,
          'CARD_SPRITESHEET': None}


def main():
    # init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TEXT['CAPTION'])
    clock = pygame.time.Clock()
    global IMAGES
    IMAGES['CARD_BACK'] = pygame.image.load(FILE_NAMES['CARD_BACK']).convert()
    IMAGES['CARD_SPRITESHEET'] = pygame.image.load(FILE_NAMES['CARD_SPRITESHEET']).convert()
    shoe = generate_new_shoe(SHOE_NUM_DECKS)
    player = Hand.Hand()
    dealer = Hand.Hand()
    split = Hand.Hand()
    flags = {'is_split': False,
             'is_insured': False,
             }
    state = 'INTRO'
    chips = 0
    bet = 0
    split_bet = 0
    # game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if state == 'INTRO':
                    if event.key == K_RETURN or event.key == K_KP_ENTER:
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
                        if len(shoe) < SHOE_CUT_DEPTH:
                            shoe = generate_new_shoe(SHOE_NUM_DECKS)
                        chips -= bet
                        for _ in range(2):
                            deal_card(screen, shoe, 'PLAYER', player, dealer, split, bet, chips, split_bet, flags, clock, hide_first=True)
                            deal_card(screen, shoe, 'DEALER', player, dealer, split, bet, chips, split_bet, flags, clock, hide_first=True)
                        if dealer.cards[1].value == 1:
                            state = 'INSURANCE'
                        else:
                            state = 'PLAYER'
                elif state == 'PLAYER':
                    if event.key == K_h:
                        deal_card(screen, shoe, 'PLAYER', player, dealer, split, bet, chips, split_bet, flags, clock, hide_first=True)
                        if player.is_bust():
                            if flags['is_split']:
                                state = 'SPLIT'
                            else:
                                state = 'SHOWDOWN'
                    if event.key == K_s:
                        if flags['is_split']:
                            state = 'SPLIT'
                        else:
                            state = 'DEALER'
                    if event.key == K_d and player.can_double() and chips >= bet:
                        chips -= bet
                        bet += bet
                        deal_card(screen, shoe, 'PLAYER', player, dealer, split, bet, chips, split_bet, flags, clock,
                                  hide_first=True)
                        if flags['is_split']:
                            state = 'SPLIT'
                        else:
                            if player.is_bust():
                                state = 'SHOWDOWN'
                            else:
                                state = 'DEALER'
                    if event.key == K_p and player.can_split() and not flags['is_split'] and chips >= bet:
                        flags['is_split'] = True
                        split_bet = bet
                        chips -= split_bet
                        split.add_card(player.cards.pop(1))
                elif state == 'INSURANCE':
                    if event.key == K_y and chips >= bet / 2:
                        flags['is_insured'] = True
                        chips -= bet / 2
                        state = 'PLAYER'
                    if event.key == K_n:
                        state = 'PLAYER'
                elif state == 'SPLIT':
                    if event.key == K_h:
                        deal_card(screen, shoe, 'SPLIT', player, dealer, split, bet, chips, split_bet, flags, clock, hide_first=True)
                        if split.is_bust():
                            chips += pay_hand(player, dealer, bet)
                            state = 'SHOWDOWN'
                    if event.key == K_s:
                        state = 'DEALER'
                    if event.key == K_d and split.can_double() and chips >= split_bet:
                        chips -= split_bet
                        split_bet += split_bet
                        deal_card(screen, shoe, 'SPLIT', player, dealer, split, bet, chips, split_bet, flags, clock,
                                  hide_first=True)
                        if split.is_bust():
                            pay_hand(player, dealer, bet)
                            state = 'SHOWDOWN'
                        else:
                            state = 'DEALER'
                elif state == 'SHOWDOWN':
                    if event.key == K_RETURN or event.key == K_KP_ENTER:
                        write_chips(chips)
                        player.clear()
                        dealer.clear()
                        split.clear()
                        flags['is_split'] = False
                        state = 'BET'
        # drawing
        screen.fill(COLORS['GREEN'])
        if state == 'INTRO':
            draw_intro(screen)
        elif state == 'BET':
            draw_chips(screen, chips)
            draw_bet(screen, bet)
            draw_shoe(screen, shoe)
        elif state == 'PLAYER' or state == 'SPLIT' or state == 'DEALER' or state == 'SHOWDOWN' or state == 'INSURANCE':
            draw_play(screen, shoe, player, dealer, split, bet, chips, split_bet, flags, hide_first=(state == 'PLAYER' or state == 'INSURANCE' or state == 'SPLIT'))
        if state == 'PLAYER':
            draw_play_options(screen, player, flags)
        if state == 'SPLIT':
            draw_play_options(screen, split, flags)
        if state == 'INSURANCE':
            draw_insurance(screen)
        if state == 'SHOWDOWN':
            draw_result(screen, player, dealer, split, flags)
        pygame.display.update()
        clock.tick(FPS)
        # game logic
        if state == 'PLAYER' and (player.blackjack() or dealer.blackjack()):
            chips += pay_hand(player, dealer, bet)
            state = 'SHOWDOWN'
        elif state == 'PLAYER' and len(player) == 1:
            deal_card(screen, shoe, 'PLAYER', player, dealer, split, bet, chips, split_bet, flags, clock,
                      hide_first=True)
        elif state == 'SPLIT' and len(split) == 1:
            deal_card(screen, shoe, 'SPLIT', player, dealer, split, bet, chips, split_bet, flags, clock, hide_first=True)
        elif state == 'DEALER':
            pygame.time.wait(DEALER_DELAY)
            if dealer.bj_value() < 17:
                deal_card(screen, shoe, 'DEALER', player, dealer, split, bet, chips, split_bet, flags, clock)
                if dealer.is_bust():
                    chips += pay_hand(player, dealer, bet)
                    if flags['is_split']:
                        chips += pay_hand(split, dealer, split_bet)
                    state = 'SHOWDOWN'
            else:
                chips += pay_hand(player, dealer, bet)
                if flags['is_split']:
                    chips += pay_hand(split, dealer, split_bet)
                state = 'SHOWDOWN'


def generate_new_shoe(num_decks):
    new_shoe = []
    for _ in range(num_decks):
        for value in range(1, 14):
            for suit in range(4):
                new_shoe.append(Card.Card(value, suit))
    return Dovetail.shuffle(new_shoe)


def load_chips():
    try:
        with open(FILE_NAMES['CHIP_AMOUNT']) as readfile:
            return int(readfile.read())
    except:
        return write_chips(CHIP_DEFAULT_NUM)


def write_chips(num_chips):
    with open(FILE_NAMES['CHIP_AMOUNT'], 'w') as writefile:
        writefile.write(str(num_chips))
        return num_chips


def adjust_bet(change, current_bet, num_chips):
    new_bet = current_bet + change
    if new_bet > num_chips:
        new_bet = num_chips
    if new_bet < 0:
        new_bet = 0
    return new_bet


def deal_card(display, deck, deal_to, player_hand, dealer_hand, split_hand, bet_amount, chip_amount, split_bet_amount, flags, clock, hide_first=False):
    start_x = COORDS['SHOE'][0] - len(deck)*3/10
    start_y = COORDS['SHOE'][1]
    if deal_to == 'PLAYER':
        end_x = COORDS['PLAYER_HAND'][0] + (len(player_hand)-1) * CARD_OFFSET
        end_y = COORDS['PLAYER_HAND'][1]
    elif deal_to == 'DEALER':
        end_x = COORDS['DEALER_HAND'][0] + (len(dealer_hand)-1) * CARD_OFFSET
        end_y = COORDS['DEALER_HAND'][1]
    elif deal_to == 'SPLIT':
        end_x = COORDS['SPLIT_HAND'][0] + (len(split_hand)-1) * CARD_OFFSET
        end_y = COORDS['SPLIT_HAND'][1]
    step_x = (end_x - start_x) / DEAL_ANIM_FRAMES
    step_y = (end_y - start_y) / DEAL_ANIM_FRAMES
    card_back_surface = IMAGES['CARD_BACK']
    card_back_rect = card_back_surface.get_rect()
    for i in range(DEAL_ANIM_FRAMES):
        display.fill(COLORS['GREEN'])
        draw_play(display, deck, player_hand, dealer_hand, split_hand, bet_amount, chip_amount, split_bet_amount, flags, hide_first=hide_first)
        card_back_rect.topleft = (start_x + i * step_x, start_y + i * step_y)
        display.blit(card_back_surface, card_back_rect)
        pygame.display.update()
        clock.tick(FPS)
    if deal_to == 'PLAYER':
        player_hand.add_card(deck.pop(0))
    elif deal_to == 'DEALER':
        dealer_hand.add_card(deck.pop(0))
    elif deal_to == 'SPLIT':
        split_hand.add_card(deck.pop(0))


def render_text_surface(text, size, color=COLORS['GOLD'], font='timesnewroman', bold=False):
    write_font = pygame.font.SysFont(font, size, bold=bold)
    return write_font.render(text, False, color)


def get_card_image(card):
    card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    card_subrect = Rect((card.value-1)*(CARD_WIDTH-2), card.suit*(CARD_HEIGHT-2), CARD_WIDTH, CARD_HEIGHT)
    card_surface.blit(IMAGES['CARD_SPRITESHEET'], (0, 0), card_subrect)
    return card_surface


def draw_intro(display):
    header_surface = render_text_surface(TEXT['INTRO_HEADER'], FONT_SIZES['INTRO_HEADER'], bold=True)
    header_rect = header_surface.get_rect()
    header_rect.center = COORDS['INTRO_HEADER']
    display.blit(header_surface, header_rect)
    subtext_surface = render_text_surface(TEXT['INTRO_SUBTEXT'], FONT_SIZES['INTRO_SUBTEXT'])
    subtext_rect = subtext_surface.get_rect()
    subtext_rect.center = COORDS['INTRO_SUBTEXT']
    display.blit(subtext_surface, subtext_rect)


def draw_play(display, shoe, player_hand, dealer_hand, split_hand, bet_amount, chip_amount, split_bet_amount, flags, hide_first=False):
    draw_shoe(display, shoe)
    draw_hand(display, 'PLAYER', player_hand)
    draw_hand(display, 'DEALER', dealer_hand, hide_first=hide_first)
    draw_bet(display, bet_amount)
    draw_chips(display, chip_amount)
    if flags['is_split']:
        draw_hand(display, 'SPLIT', split_hand)
        draw_split_bet(display, split_bet_amount)


def draw_bet(display, bet_amount, chip_amount):
    draw_bet(display, bet_amount)
    draw_chips(display, chip_amount)


def draw_bet(display, bet_amount):
    bet_text = 'Bet: {}'.format(bet_amount)
    bet_surface = render_text_surface(bet_text, FONT_SIZES['OTHER'])
    bet_rect = bet_surface.get_rect()
    bet_rect.topleft = COORDS['BET_DISPLAY']
    display.blit(bet_surface, bet_rect)


def draw_chips(display, chip_amount):
    chip_text = 'Chips: {}'.format(chip_amount)
    chip_surface = render_text_surface(chip_text, FONT_SIZES['OTHER'])
    chip_rect = chip_surface.get_rect()
    chip_rect.topleft = COORDS['CHIPS_DISPLAY']
    display.blit(chip_surface, chip_rect)


def draw_split_bet(display, split_bet_amount):
    split_bet_text = 'Bet: {}'.format(split_bet_amount)
    split_bet_surface = render_text_surface(split_bet_text, FONT_SIZES['OTHER'])
    split_bet_rect = split_bet_surface.get_rect()
    split_bet_rect.topleft = COORDS['SPLIT_BET_DISPLAY']
    display.blit(split_bet_surface, split_bet_rect)


def draw_shoe(display, shoe):
    shoe_surface = IMAGES['CARD_BACK']
    shoe_rect = shoe_surface.get_rect()
    for i in range(len(shoe)/10):
        shoe_rect.topleft = (COORDS['SHOE'][0]-i*3, COORDS['SHOE'][1])
        display.blit(shoe_surface, shoe_rect)


def draw_hand(display, owner, hand, hide_first=False):
    if owner == 'PLAYER':
        hand_x, hand_y = COORDS['PLAYER_HAND']
    elif owner == 'DEALER':
        hand_x, hand_y = COORDS['DEALER_HAND']
    elif owner == 'SPLIT':
        hand_x, hand_y = COORDS['SPLIT_HAND']
    first = True
    for card in hand:
        if hide_first and first:
            display.blit(IMAGES['CARD_BACK'], (hand_x, hand_y))
            first = False
        else:
            display.blit(get_card_image(card), (hand_x, hand_y))
        hand_x += CARD_OFFSET
    draw_total(display, owner, hand, hide_first=hide_first)


def draw_total(display, owner, hand, hide_first=False):
    if owner == 'PLAYER':
        coords = COORDS['PLAYER_TOTAL']
    elif owner == 'DEALER':
        coords = COORDS['DEALER_TOTAL']
    elif owner == 'SPLIT':
        coords = COORDS['SPLIT_TOTAL']
    if hide_first:
        total_hand = Hand.Hand()
        first = True
        for card in hand:
            if not first:
                total_hand.add_card(card)
            else:
                first = False
    else:
        total_hand = hand
    if total_hand.bj_value() > 0:
        total_surface = render_text_surface(str(total_hand.bj_value()), FONT_SIZES['TOTALS'])
        total_rect = total_surface.get_rect()
        total_rect.topleft = coords
        display.blit(total_surface, total_rect)


def draw_result(display, player_hand, dealer_hand, split_hand, flags):
    if player_hand.is_bust():
        result_text = 'BUST'
    elif player_hand.bj_value() == dealer_hand.bj_value():
        result_text = 'PUSH'
    elif player_hand.blackjack():
        result_text = 'BLACKJACK!'
    elif player_hand.bj_value() > dealer_hand.bj_value() or dealer_hand.is_bust():
        result_text = 'WIN'
    else:
        result_text = 'LOSS'
    result_surface = render_text_surface(result_text, FONT_SIZES['OTHER'])
    result_rect = result_surface.get_rect()
    result_rect.topleft = COORDS['RESULT']
    display.blit(result_surface, result_rect)
    if flags['is_split']:
        if split_hand.is_bust():
            split_result_text = 'BUST'
        elif split_hand.bj_value() == dealer_hand.bj_value():
            split_result_text = 'PUSH'
        elif split_hand.blackjack():
            split_result_text = 'BLACKJACK!'
        elif split_hand.bj_value() > dealer_hand.bj_value() or dealer_hand.is_bust():
            split_result_text = 'WIN'
        else:
            split_result_text = 'LOSS'
        split_result_surface = render_text_surface(split_result_text, FONT_SIZES['OTHER'])
        split_result_rect = split_result_surface.get_rect()
        split_result_rect.topleft = COORDS['SPLIT_RESULT']
        display.blit(split_result_surface, split_result_rect)


def draw_insurance(display):
    insurance_surface = render_text_surface(TEXT['INSURANCE'], FONT_SIZES['INSURANCE'])
    insurance_rect = insurance_surface.get_rect()
    insurance_rect.center = COORDS['INSURANCE']
    display.blit(insurance_surface, insurance_rect)
    insure_ask_surface = render_text_surface(TEXT['INSURE_ASK'], FONT_SIZES['OTHER'])
    insure_ask_rect = insure_ask_surface.get_rect()
    insure_ask_rect.center = COORDS['INSURE_ASK']
    display.blit(insure_ask_surface, insure_ask_rect)


def draw_play_options(display, player_hand, flags):
    hit_surface = render_text_surface(TEXT['HIT'], FONT_SIZES['OTHER'])
    hit_rect = hit_surface.get_rect()
    hit_rect.topleft = COORDS['OPTION_TOP_LEFT']
    display.blit(hit_surface, hit_rect)
    stand_surface = render_text_surface(TEXT['STAND'], FONT_SIZES['OTHER'])
    stand_rect = stand_surface.get_rect()
    stand_rect.topleft = COORDS['OPTION_BOTTOM_LEFT']
    display.blit(stand_surface, stand_rect)
    if player_hand.can_double():
        double_surface = render_text_surface(TEXT['DOUBLE'], FONT_SIZES['OTHER'])
        double_rect = double_surface.get_rect()
        double_rect.topleft = COORDS['OPTION_TOP_RIGHT']
        display.blit(double_surface, double_rect)
    if player_hand.can_split() and not flags['is_split']:
        split_surface = render_text_surface(TEXT['SPLIT'], FONT_SIZES['OTHER'])
        split_rect = split_surface.get_rect()
        split_rect.topleft = COORDS['OPTION_BOTTOM_RIGHT']
        display.blit(split_surface, split_rect)


def pay_hand(hand, dealer_hand, bet_amount):
    if hand.is_bust():
        return 0
    elif hand.bj_value() == dealer_hand.bj_value():
        return bet_amount
    elif hand.blackjack():
        return 3 * bet_amount / 2
    elif hand.bj_value() > dealer_hand.bj_value() or dealer_hand.is_bust():
        return 2 * bet_amount
    else:
        return 0

if __name__ == '__main__':
    main()
