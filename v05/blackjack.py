import sys
import dovetail
import pygame
from pygame.locals import *

# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 64
CARD_HEIGHT = 88
FPS = 60
HAND_WIDTH = 300
HAND_OFFSET = 30
SHOE_OFFSET = 3
BG_COLOR = (0, 114, 0)
FONT_COLOR = (255, 215, 0)
PLAYER_COORDS = (0, 400)
DEALER_COORDS = (0, 100)
SHOE_COORDS = (555, 55)
RESULTS_COORDS = (50, 245)
CHIP_COORDS = (SCREEN_WIDTH / 2, 555)
BET_COORDS = (SCREEN_WIDTH / 4, 555)
SPLIT_COORDS = (450, 400)
SPLIT_BET_COORDS = (3 * SCREEN_WIDTH / 4, 555)
SPLIT_RESULTS_COORDS = (500, 245)
OPTION_COORDS = (350, 400)
OPTION_OFFSET = 5
DEALER_DELAY = 666
SHOE_CUT_POINT = 30
ANIMATION_FRAMES = 30


class GameState:

    def __init__(self):
        self.state = 'intro'
        self.clock = pygame.time.Clock()
        self.bet = 1
        self.chips = 100
        self.insurance = 0
        self.player = Hand(PLAYER_COORDS)
        self.dealer = Dealer()
        self.split = None
        self.prev_bet = 1
        self.split_bet = 0
        self.results = None
        self.split_results = None
        self.shoe = []
        self.load_chips()
        self.replace_shoe()
        self.font = pygame.font.SysFont('timesnewroman', 18)

    def adjust_bet(self, amount):
        self.bet += amount
        if self.bet > self.chips:
            self.bet = self.chips
        elif self.bet < 1:
            self.bet = 1

    def buy_insurance(self):
        if self.chips >= self.bet / 2:
            self.insurance = self.bet / 2
            self.chips -= self.insurance
        else:
            self.insurance = self.chips
            self.chips = 0

    def card_animation(self, screen, from_coords, to_coords):
        delta_x = (from_coords[0] - to_coords[0]) / ANIMATION_FRAMES
        delta_y = (from_coords[1] - to_coords[1]) / ANIMATION_FRAMES
        for i in range(ANIMATION_FRAMES):
            self.draw(screen)
            card_surf = self.dealer.card_back
            card_rect = card_surf.get_rect()
            card_rect.left = from_coords[0] - (i * delta_x)
            card_rect.top = from_coords[1] - (i * delta_y)
            screen.blit(card_surf, card_rect)
            pygame.display.update()
            self.clock.tick(FPS)

    def deal_card(self, screen, recipient):
        from_coords = list(SHOE_COORDS)
        from_coords[0] -= (len(self.shoe) / 10) * SHOE_OFFSET
        if recipient == 'player':
            to_coords = list(PLAYER_COORDS)
            to_coords[0] += len(self.player) * HAND_OFFSET
            self.card_animation(screen, from_coords, to_coords)
            self.player.append(self.shoe.pop())
        elif recipient == 'dealer':
            to_coords = list(DEALER_COORDS)
            to_coords[0] += len(self.dealer) * HAND_OFFSET
            self.card_animation(screen, from_coords, to_coords)
            self.dealer.append(self.shoe.pop())
        elif recipient == 'split':
            to_coords = list(SPLIT_COORDS)
            to_coords[0] += len(self.split) * HAND_OFFSET
            self.card_animation(screen, from_coords, to_coords)
            self.split.append(self.shoe.pop())

    def deal_hand(self, screen):
        self.chips -= self.bet
        self.prev_bet = self.bet
        for _ in range(2):
            self.deal_card(screen, 'player')
            self.deal_card(screen, 'dealer')
        if self.dealer.insurance():
            self.state = 'insurance'
        elif self.player.blackjack() or self.dealer.blackjack():
            self.state = 'showdown'
        else:
            self.state = 'player'

    def dealer_action(self, screen):
        pygame.time.delay(DEALER_DELAY)
        if self.dealer.total() >= 17:
            self.state = 'showdown'
        else:
            self.deal_card(screen, 'dealer')

    def double_bet(self):
        if self.chips >= self.bet:
            self.chips -= self.bet
            self.bet *= 2
        else:
            self.bet += self.chips
            self.chips = 0

    def draw(self, screen):
        screen.fill(BG_COLOR)
        if self.state == 'intro':
            self.draw_intro(screen)
        else:
            self.draw_chip_total(screen)
            self.draw_bet(screen)
            self.draw_shoe(screen)
            self.player.draw(screen)
            self.draw_turn_arrow(screen)
            if self.split is not None:
                self.split.draw(screen)
            hide_first_card = False
            if self.state in ['bet', 'player', 'insurance', 'split']:
                hide_first_card = True
                self.draw_key_options(screen)
            self.dealer.draw(screen, hide_first_card)
            if self.state == 'insurance':
                self.draw_insurance(screen)
            elif self.state == 'results':
                self.draw_results(screen)

    def draw_bet(self, screen):
        bet_surf, bet_rect = text_surf_and_rect('Bet: {}'.format(self.bet), self.font)
        bet_rect.midtop = BET_COORDS
        screen.blit(bet_surf, bet_rect)
        if self.split_bet > 0:
            split_surf, split_rect = text_surf_and_rect('Split bet: {}'.format(self.split_bet), self.font)
            split_rect.topleft = SPLIT_BET_COORDS
            screen.blit(split_surf, split_rect)

    def draw_chip_total(self, screen):
        chip_surf, chip_rect = text_surf_and_rect('Chips: {}'.format(self.chips), self.font)
        chip_rect.midtop = CHIP_COORDS
        screen.blit(chip_surf, chip_rect)

    def draw_insurance(self, screen):
        insurance_surf, insurance_rect = text_surf_and_rect('Insurance? Y/N', self.font)
        insurance_rect.topleft = RESULTS_COORDS
        screen.blit(insurance_surf, insurance_rect)

    def draw_intro(self, screen):
        large_font = pygame.font.SysFont('timesnewroman', 24)
        header_surf, header_rect = text_surf_and_rect('Blackjack', large_font)
        header_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        screen.blit(header_surf, header_rect)
        footer_surf, footer_rect = text_surf_and_rect('Press Enter', self.font)
        footer_rect.center = (SCREEN_WIDTH / 2, 2 * SCREEN_HEIGHT / 3)
        screen.blit(footer_surf, footer_rect)

    def draw_key_options(self, screen):
        if self.state == 'player' or self.state == 'split':
            hit_surf, hit_rect = text_surf_and_rect('H - Hit', self.font)
            hit_rect.topleft = OPTION_COORDS
            screen.blit(hit_surf, hit_rect)
            stand_surf, stand_rect = text_surf_and_rect('S - Stand', self.font)
            stand_rect.left = OPTION_COORDS[0]
            stand_rect.top = hit_rect.bottom + OPTION_OFFSET
            screen.blit(stand_surf, stand_rect)
            double_rect = None
            if (self.state == 'player' and len(self.player) == 2) or (self.state == 'split' and len(self.split) == 2):
                double_surf, double_rect = text_surf_and_rect('D - Double', self.font)
                double_rect.left = OPTION_COORDS[0]
                double_rect.top = stand_rect.bottom + OPTION_OFFSET
                screen.blit(double_surf, double_rect)
            if self.state == 'player' and len(self.player) == 2 and self.player.cards[0][0] == self.player.cards[1][0]:
                split_surf, split_rect = text_surf_and_rect('P - Split', self.font)
                split_rect.left = OPTION_COORDS[0]
                if double_rect is not None:
                    split_rect.top = double_rect.bottom + OPTION_OFFSET
                else:
                    split_rect.top = stand_rect.bottom + OPTION_OFFSET
                screen.blit(split_surf, split_rect)

    def draw_results(self, screen):
        results_surf, results_rect = text_surf_and_rect(self.results, self.font)
        results_rect.topleft = RESULTS_COORDS
        screen.blit(results_surf, results_rect)
        if self.split_results is not None:
            split_surf, split_rect = text_surf_and_rect(self.split_results, self.font)
            split_rect.topleft = SPLIT_RESULTS_COORDS
            screen.blit(split_surf, split_rect)

    def draw_shoe(self, screen):
        for i in range(len(self.shoe) / 10):
            card_surf = self.dealer.card_back
            card_rect = card_surf.get_rect()
            card_rect.topleft = SHOE_COORDS
            card_rect.left -= i * SHOE_OFFSET
            screen.blit(card_surf, card_rect)

    def draw_turn_arrow(self, screen):
        if self.state == 'player':
            arrow_point_1 = list(PLAYER_COORDS)
        elif self.state == 'dealer':
            arrow_point_1 = list(DEALER_COORDS)
        elif self.state == 'split':
            arrow_point_1 = list(SPLIT_COORDS)
        else:
            return
        arrow_point_1[0] += 10 + HAND_OFFSET
        arrow_point_1[1] -= 10
        arrow_point_2 = (arrow_point_1[0] + 10, arrow_point_1[1])
        arrow_point_3 = (arrow_point_1[0] + 5, arrow_point_1[1] + 5)
        arrow_points = [arrow_point_1, arrow_point_2, arrow_point_3]
        pygame.draw.polygon(screen, FONT_COLOR, arrow_points)

    def load_chips(self):
        with open('chips.txt', 'r') as readfile:
            self.chips = int(readfile.read())

    def payout(self):
        if self.player.total() > 21:
            self.results = 'Bust'
        elif self.dealer.blackjack():
            self.results = 'Dealer blackjack'
            if self.player.blackjack():
                self.chips += self.bet
                self.results = 'Blackjack push'
            if self.insurance > 0:
                self.chips += 3 * self.insurance
                self.results += ' - insurance paid'
        elif self.player.blackjack() and self.split is None:
            self.results = 'Blackjack!'
            self.chips += 5 * self.bet / 2
        else:
            if self.dealer.total() > 21:
                self.results = 'Win - dealer bust'
                self.chips += self.bet * 2
            elif self.player.total() > self.dealer.total():
                self.results = 'Win - higher total'
                self.chips += self.bet * 2
            elif self.player.total() == self.dealer.total():
                self.results = 'Push'
                self.chips += self.bet
            else:
                self.results = 'Lose - lower total'
        if self.split is not None:
            if self.split.total() > 21:
                self.split_results = 'Bust'
            elif self.dealer.total() > 21:
                self.split_results = 'Win - Dealer bust'
                self.chips += self.split_bet * 2
            elif self.split.total() > self.dealer.total():
                self.split_results = 'Win - higher total'
                self.chips += self.split_bet * 2
            elif self.split.total() == self.dealer.total():
                self.split_results = 'Push'
                self.chips += self.split_bet
            else:
                self.split_results = 'Lose - lower total'
        self.state = 'results'

    def replace_shoe(self, num_decks=8):
        new_shoe = []
        for _ in range(num_decks):
            for value in range(13):
                for suit in range(4):
                    new_shoe.append((value, suit))
        self.shoe = dovetail.shuffle(new_shoe, 7)

    def reset(self):
        self.save_chips()
        self.player.reset()
        self.dealer.reset()
        self.bet = self.prev_bet
        self.insurance = 0
        self.split = None
        self.split_bet = 0
        self.split_results = None
        self.results = None
        if len(self.shoe) < SHOE_CUT_POINT:
            self.replace_shoe()

    def save_chips(self):
        with open('chips.txt', 'w') as writefile:
            writefile.write(str(self.chips))

    def split_hand(self, screen):
        if self.chips >= self.bet:
            self.split_bet = self.bet
            self.chips -= self.split_bet
        else:
            self.split_bet = self.chips
            self.chips = 0
        self.split = Hand(SPLIT_COORDS)
        from_coords = list(PLAYER_COORDS)
        from_coords[0] += HAND_OFFSET
        to_coords = list(SPLIT_COORDS)
        split_card = self.player.cards.pop()
        self.card_animation(screen, from_coords, to_coords)
        self.split.append(split_card)
        self.deal_card(screen, 'player')


class Hand:

    def __init__(self, coords):
        self.cards = []
        self.coords = coords
        self.font = pygame.font.SysFont('timesnewroman', 18)
        self.card_sheet = pygame.image.load('card_front_sheet.png').convert()

    def __iter__(self):
        return self.cards.__iter__()

    def __len__(self):
        return self.cards.__len__()

    def append(self, new_card):
        self.cards.append(new_card)

    def blackjack(self):
        if len(self) == 2 and self.total() == 21:
            return True
        else:
            return False

    def draw(self, screen):
        draw_surf = pygame.Surface((HAND_WIDTH, CARD_HEIGHT))
        draw_surf.fill(BG_COLOR)
        if len(self) > 0:
            total_surf, total_rect = text_surf_and_rect(str(self.total()), self.font)
            total_rect.center = (HAND_OFFSET / 2, CARD_HEIGHT / 2)
            draw_surf.blit(total_surf, total_rect)
            card_rect = Rect(HAND_OFFSET, 0, CARD_WIDTH, CARD_HEIGHT)
            for card in self:
                sprite_rect = Rect(card[0] * (CARD_WIDTH - 2), card[1] * (CARD_HEIGHT - 2), CARD_WIDTH, CARD_HEIGHT)
                card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                card_surf.blit(self.card_sheet, (0, 0), sprite_rect)
                draw_surf.blit(card_surf, card_rect)
                card_rect.left += HAND_OFFSET
        screen.blit(draw_surf, self.coords)

    def reset(self):
        self.cards = []

    def total(self):
        total = 0
        ace = False
        for card in self:
            if card[0] == 0:
                ace = True
            total += min(10, card[0] + 1)
        if ace and total <= 11:
            total += 10
        return total


class Dealer(Hand):

    def __init__(self):
        Hand.__init__(self, DEALER_COORDS)
        self.card_back = pygame.image.load('card_back_crosshatch.png').convert()

    def draw(self, screen, hide_first=False):
        if hide_first and len(self) >= 1:
            draw_surf = pygame.Surface((HAND_WIDTH, CARD_HEIGHT))
            draw_surf.fill(BG_COLOR)
            card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            card_rect = Rect(HAND_OFFSET, 0, CARD_WIDTH, CARD_HEIGHT)
            draw_surf.blit(self.card_back, card_rect)
            hidden_hand = self.cards[1:]
            total = 0
            ace = False
            for card in hidden_hand:
                total += min(10, card[0] + 1)
                card_rect.left += HAND_OFFSET
                if card[0] == 0:
                    ace = True
                sprite_rect = (card[0] * (CARD_WIDTH - 2), card[1] * (CARD_HEIGHT - 2), CARD_WIDTH, CARD_HEIGHT)
                card_surf.blit(self.card_sheet, (0, 0), sprite_rect)
                draw_surf.blit(card_surf, card_rect)
            if ace and total <= 11:
                total += 10
            if total == 0:
                total_text = '-'
            else:
                total_text = str(total)
            total_surf, total_rect = text_surf_and_rect(total_text, self.font)
            total_rect.center = (HAND_OFFSET / 2, CARD_HEIGHT / 2)
            draw_surf.blit(total_surf, total_rect)
            screen.blit(draw_surf, self.coords)
        else:
            Hand.draw(self, screen)

    def insurance(self):
        if len(self) == 2 and self.cards[1][0] == 0:
            return True
        else:
            return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = GameState()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_KP_ENTER or event.key == K_RETURN:
                    if game.state == 'intro':
                        game.state = 'bet'
                    elif game.state == 'bet':
                        game.deal_hand(screen)
                    elif game.state == 'results':
                        game.reset()
                        game.state = 'bet'
                elif game.state == 'bet':
                    bet_keys = {K_UP: 5, K_DOWN: -5, K_LEFT: -1, K_RIGHT: 1}
                    if event.key in bet_keys:
                        game.adjust_bet(bet_keys[event.key])
                elif game.state == 'insurance':
                    if event.key == K_y or event.key == K_n:
                        if event.key == K_y:
                            game.buy_insurance()
                        if game.player.blackjack() or game.dealer.blackjack():
                            game.state = 'showdown'
                        else:
                            game.state = 'player'
                elif game.state == 'player':
                    if event.key == K_h:
                        game.deal_card(screen, 'player')
                        if game.player.total() > 21:
                            if game.split is None:
                                game.state = 'showdown'
                            else:
                                game.deal_card(screen, 'split')
                                game.state = 'split'
                    elif event.key == K_s:
                        if game.split is None:
                            game.state = 'dealer'
                        else:
                            game.deal_card(screen, 'split')
                            game.state = 'split'
                    elif event.key == K_d and len(game.player) == 2:
                        game.double_bet()
                        game.deal_card(screen, 'player')
                        if game.split is not None:
                            game.deal_card(screen, 'split')
                            game.state = 'split'
                        elif game.player.total() > 21:
                            game.state = 'showdown'
                        else:
                            game.state = 'dealer'
                    elif event.key == K_p and len(game.player) == 2 and game.split is None:
                        if game.player.cards[0][0] == game.player.cards[1][0]:
                            game.split_hand(screen)
                elif game.state == 'split':
                    if event.key == K_h:
                        game.deal_card(screen, 'split')
                        if game.split.total() > 21:
                            if game.player.total() > 21:
                                game.state = 'showdown'
                            else:
                                game.state = 'dealer'
                    elif event.key == K_s:
                        game.state = 'dealer'
        game.draw(screen)
        pygame.display.update()
        game.clock.tick(FPS)
        if game.state == 'dealer':
            game.dealer_action(screen)
        elif game.state == 'showdown':
            game.payout()


def terminate():
    pygame.quit()
    sys.exit()


def text_surf_and_rect(text, font, color=FONT_COLOR):
    surf = font.render(text, False, color)
    return surf, surf.get_rect()


if __name__ == '__main__':
    main()