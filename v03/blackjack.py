# imports
import sys
import dovetail
import pygame
from pygame.locals import *

# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 45
CARD_WIDTH = 64
CARD_HEIGHT = 88
HAND_OFFSET = 30
SHOE_OFFSET = 3
CHIP_FILE = 'chips.txt'
DEALER_COORDS = (10, 125)
PLAYER_COORDS = (10, 310)
SHOE_COORDS = (SCREEN_WIDTH - 10 - CARD_WIDTH, 200)
RESULT_COORDS = (SCREEN_WIDTH / 2, DEALER_COORDS[1] + (PLAYER_COORDS[1] - DEALER_COORDS[1] + CARD_HEIGHT) / 2)
BG_COLOR = (0, 114, 0)
FONT_NAME = 'timesnewroman'
FONT_SIZE = 18
FONT_COLOR = (255, 215, 0)
CARD_BACK_IMAGE_FILE = 'card_back_crosshatch.png'
CARD_SHEET_IMAGE_FILE = 'card_front_sheet.png'
CARD_DEAL_ANIM_FRAMES = 15
VALUES = {
    0: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
    10: 10,
    11: 10,
    12: 10,
        }
DEALER_DELAY = 500


# main
def main():
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    # variable init
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    card_sheet = pygame.image.load(CARD_SHEET_IMAGE_FILE).convert()
    card_back = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()
    shoe = create_shoe()
    player = Player()
    dealer = []
    state = 'intro'
    # game loop
    while True:
        # events
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if state == 'intro':
                        state = 'bet'
                    elif state == 'bet':
                        player.make_bet()
                        state = 'deal'
                    elif state == 'result':
                        if player.doubled:
                            player.bet /= 2
                        player.hand = []
                        player.insured = False
                        player.doubled = False
                        dealer = []
                        if len(shoe) < 30:
                            shoe = create_shoe()
                        state = 'bet'
                if state == 'bet':
                    if event.key == K_UP:
                        player.change_bet(5)
                    elif event.key == K_DOWN:
                        player.change_bet(-5)
                    elif event.key == K_LEFT:
                        player.change_bet(-1)
                    elif event.key == K_RIGHT:
                        player.change_bet(1)
                elif state == 'insurance':
                    if event.key == K_y:
                        if player.chips >= player.bet / 2:
                            player.chips -= player.bet / 2
                            player.insured = True
                            if hand_value(player.hand) == 21 or hand_value(dealer) == 21:
                                state = 'showdown'
                            else:
                                state = 'player'
                    elif event.key == K_n:
                        if hand_value(player.hand) == 21 or hand_value(dealer) == 21:
                            state = 'showdown'
                        else:
                            state = 'player'
                elif state == 'player':
                    if event.key == K_h:
                        state = 'player_hit'
                    if event.key == K_s:
                        state = 'dealer'
                    if event.key == K_d and len(player.hand) == 2 and player.chips >= player.bet:
                        if player.double_down():
                            card_deal_animation(screen, dealer, player, state, clock, len(shoe), card_sheet, card_back, PLAYER_COORDS,
                                            font)
                            player.hand.append(shoe.pop())
                            state = 'dealer'
        # game event(s)
        state = perform_game_action(screen, state, clock, shoe, dealer, player, card_sheet, card_back, font)
        # draw & clock
        screen.fill(BG_COLOR)
        if state == 'intro':
            draw_intro(screen)
        else:
            draw_shoe(screen, len(shoe), card_back)
            player.draw(screen, state, card_sheet, font)
            draw_dealer(screen, dealer, state, card_sheet, card_back, font)
            if state == 'insurance':
                draw_insurance_ask(screen)
            if state == 'result':
                draw_result(screen, dealer, player)
        pygame.display.update()
        clock.tick(FPS)


# classes
class Player:
    def __init__(self):
        self.hand = []
        self.split_hand = []
        self.chips = 100
        self.load_chips()
        self.bet = 1
        self.insured = False
        self.doubled = False

    def change_bet(self, change):
        self.bet += change
        if self.bet <= 0:
            self.bet = 1
        elif self.bet > self.chips:
            self.bet = self.chips

    def double_down(self):
        """Doubles bet: returns true on success, false on fail."""
        if self.chips >= self.bet:
            self.doubled = True
            self.bet += self.bet
            self.chips -= self.bet
            return True
        else:
            return False

    def draw(self, screen, state, sheet, font):
        card_num = 0
        for card in self.hand:
            card_num += 1
            source_x = card[0] * (CARD_WIDTH - 2)
            source_y = card[1] * (CARD_HEIGHT - 2)
            source_rect = Rect(source_x, source_y, CARD_WIDTH, CARD_HEIGHT)
            card_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            card_image.blit(sheet, (0, 0), source_rect)
            card_x = PLAYER_COORDS[0] + card_num * HAND_OFFSET
            screen.blit(card_image, (card_x, PLAYER_COORDS[1]))
        if card_num > 0:
            total_surf = create_text_surface('{}'.format(hand_value(self.hand)), font)
            total_rect = total_surf.get_rect()
            total_rect.topleft = PLAYER_COORDS
            total_rect.left += HAND_OFFSET
            total_rect.top -= 25
            screen.blit(total_surf, total_rect)
        chips_surf = create_text_surface('Chips: {}'.format(self.chips), font)
        chips_rect = chips_surf.get_rect()
        chips_rect.topleft = PLAYER_COORDS
        chips_rect.top += 100
        screen.blit(chips_surf, chips_rect)
        bet_surf = create_text_surface('Bet: {}'.format(self.bet), font)
        bet_rect = bet_surf.get_rect()
        bet_rect.topleft = chips_rect.topright
        bet_rect.left += 25
        screen.blit(bet_surf, bet_rect)

    def load_chips(self, filename=CHIP_FILE):
        try:
            with open(CHIP_FILE, 'r') as readfile:
                chip_amount = int(readfile.read())
            self.chips = chip_amount
        except:
            print 'Loading chips failed.'

    def make_bet(self):
        self.chips -= self.bet

    def save_chips(self, filename=CHIP_FILE):
        with open(CHIP_FILE, 'w') as writefile:
            writefile.write(str(self.chips))


# functions
def card_deal_animation(screen, dealer, player, state, clock, shoe_size, sheet, back, to_coords, font):
    card_image = back
    x_0, y_0 = SHOE_COORDS
    x_0 -= (shoe_size / 10) * SHOE_OFFSET
    if to_coords == PLAYER_COORDS:
        x_end = PLAYER_COORDS[0] + (len(player.hand) + 1) * HAND_OFFSET
        y_end = PLAYER_COORDS[1]
    elif to_coords == DEALER_COORDS:
        x_end = DEALER_COORDS[0] + (len(dealer) + 1) * HAND_OFFSET
        y_end = DEALER_COORDS[1]
    delta_x = (x_end - x_0) / CARD_DEAL_ANIM_FRAMES
    delta_y = (y_end - y_0) / CARD_DEAL_ANIM_FRAMES
    for i in range(CARD_DEAL_ANIM_FRAMES):
        card_rect = card_image.get_rect()
        card_rect.left = x_0 + i * delta_x
        card_rect.top = y_0 + i * delta_y
        screen.fill(BG_COLOR)
        draw_shoe(screen, shoe_size, back)
        player.draw(screen, state, sheet, font)
        draw_dealer(screen, dealer, state, sheet, back, font)
        screen.blit(card_image, card_rect)
        pygame.display.update()
        clock.tick(FPS)


def create_shoe(shoe_size=8):
    shoe = []
    for _ in range(shoe_size):
        deck = []
        for suit in range(4):
            for value in range(13):
                deck.append((value, suit))
        shoe.extend(deck)
    return dovetail.shuffle(shoe)


def create_text_surface(text, font, color=FONT_COLOR):
    text_surf = font.render(text, False, color)
    return text_surf


def deal_hand(shoe, dealer, player):
    player.chips -= player.bet
    for _ in range(2):
        dealer.append(shoe.pop())
        player.append(shoe.pop())


def draw_dealer(screen, dealer, state, sheet, back, font):
    num_card = 1
    show_first = False
    if state == 'dealer' or state == 'showdown' or state == 'result':
        show_first = True
    for card in dealer:
        if num_card == 1 and not show_first:
            card_image = back
        else:
            source_x = card[0] * (CARD_WIDTH - 2)
            source_y = card[1] * (CARD_HEIGHT - 2)
            source_rect = Rect(source_x, source_y, CARD_WIDTH, CARD_HEIGHT)
            card_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            card_image.blit(sheet, (0, 0), source_rect)
        card_x = DEALER_COORDS[0] + num_card * HAND_OFFSET
        screen.blit(card_image, (card_x, DEALER_COORDS[1]))
        num_card += 1
    if num_card > 1:
        if not show_first:
            if len(dealer) >= 2:
                show_hand = dealer[1:]
                total = hand_value(show_hand)
            else:
                total = 0
        else:
            total = hand_value(dealer)
        if total > 0:
            total_surf = create_text_surface('{}'.format(total), font)
            total_rect = total_surf.get_rect()
            total_rect.topleft = DEALER_COORDS
            total_rect.left += HAND_OFFSET
            total_rect.top -= 25
            screen.blit(total_surf, total_rect)


def draw_insurance_ask(screen):
    insurance_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    insurance_surf = create_text_surface('Insurance? Y/N', insurance_font)
    insurance_rect = insurance_surf.get_rect()
    insurance_rect.topleft = PLAYER_COORDS
    insurance_rect.top -= 75
    screen.blit(insurance_surf, insurance_rect)


def draw_intro(screen):
    intro_font = pygame.font.SysFont(FONT_NAME, 24)
    intro_1_surf = create_text_surface('Blackjack', intro_font)
    intro_1_rect = intro_1_surf.get_rect()
    intro_1_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    screen.blit(intro_1_surf, intro_1_rect)


def draw_result(screen, dealer, player):
    result_font = pygame.font.SysFont(FONT_NAME, 24)
    result_surf = create_text_surface(get_result_text(dealer, player), result_font)
    result_rect = result_surf.get_rect()
    result_rect.topleft = RESULT_COORDS
    screen.blit(result_surf, result_rect)


def draw_shoe(screen, shoe_size, back):
    shoe_image = back
    for i in range(max(1, shoe_size / 10)):
        shoe_rect = shoe_image.get_rect()
        shoe_rect.topleft = SHOE_COORDS
        shoe_rect.left -= i * SHOE_OFFSET
        screen.blit(shoe_image, shoe_rect)


def get_result_text(dealer, player):
    p = hand_value(player.hand)
    d = hand_value(dealer)
    if p > 21:
        return 'Bust'
    elif p == 21 and len(player.hand) == 2:
        return 'Blackjack!'
    elif p > d or d > 21:
        return 'Win!'
    elif p == d:
        return 'Push'
    elif p < d:
        return 'Lose'
    else:
        return 'wut'


def hand_value(hand):
    ace = False
    total = 0
    for card in hand:
        total += VALUES[card[0]]
        if VALUES[card[0]] == 1:
            ace = True
    if ace and total <= 11:
        total += 10
    return total


def perform_game_action(screen, state, clock, shoe, dealer, player, sheet, back, font):
    '''Returns the current state'''
    if state == 'deal':
        for _ in range(2):
            card_deal_animation(screen, dealer, player, state, clock, len(shoe), sheet, back, PLAYER_COORDS, font)
            player.hand.append(shoe.pop())
            card_deal_animation(screen, dealer, player, state, clock, len(shoe), sheet, back, DEALER_COORDS, font)
            dealer.append(shoe.pop())
        # insurance check
        if dealer[1][0] == 0:
            return 'insurance'
        # blackjack check
        elif hand_value(dealer) == 21 or hand_value(player.hand) == 21:
            return 'showdown'
        if hand_value(player.hand) == 21 or hand_value(dealer) == 21:
            return 'showdown'
        return 'player'
    elif state == 'player_hit':
        card_deal_animation(screen, dealer, player, state, clock, len(shoe), sheet, back, PLAYER_COORDS, font)
        player.hand.append(shoe.pop())
        if hand_value(player.hand) > 21:
            return 'showdown'
        else:
            return 'player'
    elif state == 'dealer':
        pygame.time.delay(DEALER_DELAY)
        if hand_value(dealer) >= 17:
            return 'showdown'
        else:
            card_deal_animation(screen, dealer, player, state, clock, len(shoe), sheet, back, DEALER_COORDS, font)
            dealer.append(shoe.pop())
    elif state == 'showdown':
        # check winner/loser, pay out if nec.
        if hand_value(player.hand) <= 21:
            if hand_value(player.hand) > hand_value(dealer) or hand_value(dealer) > 21:
                if hand_value(player.hand) == 21 and len(player.hand) == 2:
                    player.chips += 2 * player.bet + player.bet / 2
                else:
                    player.chips += 2 * player.bet
            elif hand_value(player.hand) == hand_value(dealer):
                if hand_value(player.hand) == 21 and len(player.hand) == 2:
                    if player.insured:
                        player.chips += 2 * player.bet
                    else:
                        player.chips += player.bet
                else:
                    player.chips += player.bet
        player.save_chips()
        return 'result'
    return state


def terminate():
    pygame.quit()
    sys.exit()

# run
main()
