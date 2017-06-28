import sys
import dovetail
import pygame
from pygame.locals import *

# CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 64
CARD_HEIGHT = 88
FPS = 60
FONT_SIZE = 18
LARGE_FONT_SIZE = 24
HAND_OFFSET = 30
SHOE_OFFSET = 3
SHOE_CUTOFF = 26
SHOE_TILE_SCALE = 10
INTRO_HEIGHTS = (SCREEN_HEIGHT / 3, 2 * SCREEN_HEIGHT / 3)
DEALER_COORDS = (SCREEN_WIDTH / 6, SCREEN_HEIGHT / 6)
PLAYER_COORDS = (SCREEN_WIDTH / 6, 2 * SCREEN_HEIGHT / 3)
INSURANCE_COORDS = (SCREEN_WIDTH / 6 + HAND_OFFSET, SCREEN_HEIGHT / 2)
SHOE_COORDS = (7 * SCREEN_WIDTH / 8, SCREEN_HEIGHT / 3)
BG_COLOR = (0, 114, 0)
FONT_COLOR = (255, 215, 0)
FONT_NAME = 'timesnewroman'
CHIP_FILE = 'chips.txt'
CARD_BACK_IMAGE_FILE = 'card_back_crosshatch.png'
CARD_SHEET_IMAGE_FILE = 'card_front_sheet.png'
DEALER_DELAY = 750
CARD_DEAL_ANIMATION_FRAMES = FPS / 2


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    dealer = Dealer()
    shoe = generate_shoe()
    state = 'intro'
    previous_bet = player.bet
    results = 'None'
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_KP_ENTER or event.key == K_RETURN:
                    if state == 'intro':
                        state = 'bet'
                    elif state == 'bet':
                        player.make_bet()
                        previous_bet = player.bet
                        for _ in range(2):
                            deal_card('player', screen, state, shoe, player, dealer, clock)
                            deal_card('dealer', screen, state, shoe, player, dealer, clock)
                        if dealer[1][0] == 0:
                            state = 'insurance'
                        elif player.value() == 21 or dealer.value() == 21:
                            state = 'showdown'
                        else:
                            state = 'player'
                    elif state == 'results':
                        shoe = reset_and_return_shoe(shoe, player, dealer, previous_bet)
                        state = 'bet'
                elif state == 'bet':
                    bet_changes = {
                        K_UP: 1,
                        K_DOWN: -1,
                        K_RIGHT: 5,
                        K_LEFT: -5
                                   }
                    if event.key in bet_changes:
                        player.adjust_bet(bet_changes[event.key])
                elif state == 'insurance':
                    if event.key == K_y or event.key == K_n:
                        if event.key == K_y:
                            player.buy_insurance()
                        if player.value() == 21 or dealer.value() == 21:
                            state = 'showdown'
                        else:
                            state = 'player'
                elif state == 'player':
                    if event.key == K_h:
                        deal_card('player', screen, state, shoe, player, dealer, clock)
                        if player.value() > 21:
                            state = 'showdown'
                    if event.key == K_d:
                        player.double()
                        deal_card('player', screen, state, shoe, player, dealer, clock)
                        if player.value() > 21:
                            state = 'showdown'
                        else:
                            state = 'dealer'
                    if event.key == K_s:
                        state = 'dealer'
        if state == 'dealer':
            state = dealer.perform_action(screen, state, player, shoe, clock)
        if state == 'showdown':
            results = payout(player, dealer)
            state = 'results'
        screen.fill(BG_COLOR)
        if state == 'intro':
            draw_intro(screen)
        else:
            screen.fill(BG_COLOR)
            player.draw(screen)
            dealer.draw(screen, state)
            draw_shoe(screen, shoe)
            if state == 'bet':
                draw_bet(screen)
            if state == 'insurance':
                draw_insurance(screen)
            if state == 'results':
                draw_results(screen, results)
        pygame.display.update()
        clock.tick(FPS)


def deal_card(recipient, screen, state, shoe, player, dealer, clock):
    from_x, from_y = SHOE_COORDS
    from_x -= (len(shoe) / SHOE_TILE_SCALE) * SHOE_OFFSET
    if recipient == 'player':
        to_x, to_y = PLAYER_COORDS
        to_x += len(player) * HAND_OFFSET
    elif recipient == 'dealer':
        to_x, to_y = DEALER_COORDS
        to_x += len(dealer) * HAND_OFFSET
    step_x = (to_x - from_x) / CARD_DEAL_ANIMATION_FRAMES
    step_y = (to_y - from_y) / CARD_DEAL_ANIMATION_FRAMES
    card_surf = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()
    card_rect = card_surf.get_rect()
    for i in range(CARD_DEAL_ANIMATION_FRAMES - 1):
        card_rect.topleft = (from_x + i * step_x, from_y + i * step_y)
        screen.fill(BG_COLOR)
        draw_shoe(screen, shoe)
        player.draw(screen)
        dealer.draw(screen, state)
        screen.blit(card_surf, card_rect)
        pygame.display.update()
        clock.tick(FPS)
    if recipient == 'player':
        player.cards.append(shoe.pop())
    elif recipient == 'dealer':
        dealer.cards.append(shoe.pop())


def draw_bet(screen):
    bet_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    bet_text = 'Make your wager'
    bet_surf, bet_rect = text_surface_and_rect(bet_text, bet_font)
    bet_rect.topleft = INSURANCE_COORDS
    screen.blit(bet_surf, bet_rect)


def draw_intro(screen):
    intro_font = pygame.font.SysFont(FONT_NAME, LARGE_FONT_SIZE)
    intro_text = 'BLACKJACK'
    intro_surf, intro_rect = text_surface_and_rect(intro_text, intro_font)
    intro_rect.midtop = (SCREEN_WIDTH / 2, INTRO_HEIGHTS[0])
    screen.blit(intro_surf, intro_rect)
    continue_text = 'Press Enter to continue.'
    continue_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    continue_surf, continue_rect = text_surface_and_rect(continue_text, continue_font)
    continue_rect.midbottom = (INTRO_HEIGHTS[1], SCREEN_WIDTH / 2)
    screen.blit(continue_surf, continue_rect)


def draw_insurance(screen):
    insurance_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    insurance_text = 'Insurance? Y/N'
    insurance_surf, insurance_rect = text_surface_and_rect(insurance_text, insurance_font)
    insurance_rect.topleft = INSURANCE_COORDS
    screen.blit(insurance_surf, insurance_rect)


def draw_results(screen, results):
    results_font = pygame.font.SysFont(FONT_NAME, LARGE_FONT_SIZE)
    results_surf, results_rect = text_surface_and_rect(results, results_font)
    results_rect.topleft = INSURANCE_COORDS
    screen.blit(results_surf, results_rect)


def draw_shoe(screen, shoe):
    card_back = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()
    card_rect = card_back.get_rect()
    for i in range(len(shoe) / SHOE_TILE_SCALE):
        card_rect.topleft = SHOE_COORDS
        card_rect.left -= SHOE_OFFSET * i
        screen.blit(card_back, card_rect)


def generate_shoe(num_decks=8):
    new_shoe = []
    for _ in range(num_decks):
        for value in range(13):
            for suit in range(4):
                new_shoe.append((value, suit))
    return dovetail.shuffle(new_shoe)


def payout(player, dealer):
    result = 'Bust'
    if player.value() == 21 and len(player) == 2:
        if dealer.value() == 21:
            # push plus even money if insurance was paid
            player.chips += player.bet
            result = 'Double Blackjack: Push'
            if player.insurance > 0:
                result = 'Blackjack with insurance!'
                player.chips += player.insurance + player.bet
        else:
            # 3:2
            result = 'Blackjack!'
            player.chips += (3 * player.bet) / 2 + player.bet
    elif player.value() <= 21:
        result = 'Lose'
        if player.value() > dealer.value() or dealer.value() > 21:
            result = 'Win!'
            player.chips += 2 * player.bet
        elif player.value() == dealer.value():
            result = 'Push'
            player.chips += player.bet
    return result


def reset_and_return_shoe(shoe, player, dealer, prev_bet):
    player.cards = []
    player.bet = prev_bet
    player.adjust_bet(0)
    player.insurance = 0
    dealer.cards = []
    if len(shoe) < SHOE_CUTOFF:
        return generate_shoe()
    else:
        return shoe


def text_surface_and_rect(text, font, color=FONT_COLOR):
    text_surf = font.render(text, False, color)
    text_rect = text_surf.get_rect()
    return text_surf, text_rect


def terminate():
    pygame.quit()
    sys.exit()


class Hand:
    def __init__(self):
        self.cards = []
        self.sheet = pygame.image.load(CARD_SHEET_IMAGE_FILE).convert()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

    def __getitem__(self, item):
        return self.cards.__getitem__(item)

    def __len__(self):
        return self.cards.__len__()

    def draw(self, screen):
        # to be overridden by child classes
        pass

    def get_card_surface(self, card):
        card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        card_sheet_x = card[0] * (CARD_WIDTH - 2)
        card_sheet_y = card[1] * (CARD_HEIGHT - 2)
        sheet_rect = Rect(card_sheet_x, card_sheet_y, CARD_WIDTH, CARD_HEIGHT)
        card_surf.blit(self.sheet, (0, 0), sheet_rect)
        return card_surf

    def value(self):
        value = 0
        ace = False
        for card in self.cards:
            if card[0] < 10:
                value += card[0] + 1
                if card[0] == 0:
                    ace = True
            else:
                value += 10
        if value <= 11 and ace:
            value += 10
        return value


class Player(Hand):
    def __init__(self):
        Hand.__init__(self)
        self.chips = 100  # TODO -- load_chips() & save_chips()
        self.bet = 1
        self.insurance = 0

    def adjust_bet(self, amount):
        self.bet += amount
        if self.bet > self.chips:
            self.bet = self.chips
        elif self.bet < 1:
            self.bet = 1

    def buy_insurance(self):
        self.insurance = min(self.bet / 2, self.chips)
        self.chips -= self.insurance

    def double(self):
        if self.chips >= self.bet:
            self.chips -= self.bet
            self.bet *= 2
        else:
            self.bet += self.chips
            self.chips = 0

    def draw(self, screen):
        num_card = 0
        for card in self.cards:
            card_x = PLAYER_COORDS[0] + num_card * HAND_OFFSET
            card_rect = Rect(card_x, PLAYER_COORDS[1], CARD_WIDTH, CARD_HEIGHT)
            card_surf = self.get_card_surface(card)
            screen.blit(card_surf, card_rect)
            num_card += 1
        total_topleft = (PLAYER_COORDS[0] + HAND_OFFSET, PLAYER_COORDS[1] + CARD_HEIGHT + 5)
        if num_card > 0:
            total_text = str(self.value())
            total_surf, total_rect = text_surface_and_rect(total_text, self.font)
            total_rect.topleft = total_topleft
            screen.blit(total_surf, total_rect)
        chips_surf, chips_rect = text_surface_and_rect('Chips: {}'.format(self.chips), self.font)
        chips_rect.topleft = (total_topleft[0] + 45, total_topleft[1] + 25)
        screen.blit(chips_surf, chips_rect)
        bet_surf, bet_rect = text_surface_and_rect('Bet: {}'.format(self.bet), self.font)
        bet_rect.topleft = (chips_rect.left + 100, chips_rect.top)
        screen.blit(bet_surf, bet_rect)

    def make_bet(self):
        self.chips -= self.bet


class Dealer(Hand):
    def __init__(self):
        Hand.__init__(self)
        self.back = pygame.image.load(CARD_BACK_IMAGE_FILE).convert()

    def draw(self, screen, state):
        num_card = 0
        ace = False
        hidden_total = 0
        for card in self.cards:
            card_x = DEALER_COORDS[0] + num_card * HAND_OFFSET
            card_rect = Rect(card_x, DEALER_COORDS[1], CARD_WIDTH, CARD_HEIGHT)
            if num_card == 0 and state not in ['dealer', 'showdown', 'results']:
                card_surf = self.back
            else:
                if card[0] == 0:
                    ace = True
                hidden_total += min(card[0] + 1, 10)
                card_surf = self.get_card_surface(card)
            screen.blit(card_surf, card_rect)
            num_card += 1
        if num_card > 0:
            if state not in ['dealer', 'showdown', 'results']:
                if ace and hidden_total <= 11:
                    hidden_total += 10
                total_text = str(hidden_total)
            else:
                total_text = str(self.value())
            total_surf, total_rect = text_surface_and_rect(total_text, self.font)
            total_rect.topleft = (DEALER_COORDS[0] + HAND_OFFSET, DEALER_COORDS[1] + CARD_HEIGHT + 5)
            screen.blit(total_surf, total_rect)

    def perform_action(self, screen, state, player, shoe, clock):
        '''Returns what state the game should be in.'''
        pygame.time.wait(DEALER_DELAY)
        if self.value() < 17:
            deal_card('dealer', screen, state, shoe, player, self, clock)
            return state
        else:
            return 'showdown'


if __name__ == '__main__':
    main()
