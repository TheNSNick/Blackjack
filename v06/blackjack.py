import sys
import pygame
import dovetail


# CONSTANTS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 64
CARD_HEIGHT = 88
FPS = 60
BG_COLOR = (0, 114, 0)
FONT_COLOR = (255, 215, 0)
PLAYER_COORDS = (50, 450)
DEALER_COORDS = (50, 75)
SHOE_COORDS = (700, 100)
DEAL_FRAMES = FPS / 4


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Blackjack')
    clock = pygame.time.Clock()
    card_sheet = pygame.image.load('card_sheet.png').convert()
    card_back = pygame.image.load('card_back.png').convert()
    intro_image = pygame.image.load('intro_main.png').convert()
    intro_text = pygame.image.load('intro_text.png').convert()
    chip_amount = 100   # TODO -- loading/saving chips
    bet = 1
    player = pygame.sprite.OrderedUpdates()
    dealer = pygame.sprite.OrderedUpdates()
    shoe = new_decks(8)
    state = 'intro'
    font = pygame.font.SysFont('arial', 16)
    # MAIN GAME LOOP
    while True:
        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    if state == 'intro':
                        state = 'bet'
                    elif state == 'bet':
                        chip_amount -= bet
                        deal_opening_hand(screen, clock, card_sheet, card_back, player, dealer, shoe)
                        state = 'play'
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT] and state == 'bet':
                    bet_changes = {pygame.K_UP: 1, pygame.K_DOWN: -1, pygame.K_LEFT: -5, pygame.K_RIGHT: 5}
                    bet += bet_changes[event.key]
                    if bet < 1:
                        bet = 1
                    if bet > chip_amount:
                        bet = chip_amount
                    print bet
                # TESTING: CLEAR, AND REVEAL CARDS
                elif event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]:
                    player.empty()
                    dealer.empty()
                elif event.key == pygame.K_SPACE:
                    reveal(dealer)
                # END TESTING
        # DRAWING
        screen.fill(BG_COLOR)
        # GameState-based drawing
        if state == 'intro':
            intro_rect = intro_image.get_rect()
            intro_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            screen.blit(intro_image, intro_rect)
            intro_rect_2 = intro_text.get_rect()
            intro_rect_2.midtop = (SCREEN_WIDTH / 2, intro_rect.bottom + 5)
            screen.blit(intro_text, intro_rect_2)
        else:
            player.draw(screen)
            # TODO -- states will need tweaking
            if state != 'bet':
                draw_hand_total(screen, player, PLAYER_COORDS, font)
            dealer.draw(screen)
            if state == 'dealer':
                draw_hand_total(screen, dealer, DEALER_COORDS, font)
            screen.blit(card_back, SHOE_COORDS)
        pygame.display.update()
        clock.tick(FPS)
# END MAIN LOOP


def animate_card_deal(draw_surface, game_clock, card_back_image, player, dealer, recipient):
    if not isinstance(recipient, str):
        raise TypeError('recipient should be a string indicating the [D]ealer or the [P]layer.')
    if recipient[0].lower() not in ['d', 'p']:
        raise ValueError('recipient should be a string indicating the [D]ealer or the [P]layer.')
    elif recipient[0].lower() == 'd':
        to_coords = [DEALER_COORDS[0] + len(dealer) * CARD_WIDTH / 2, DEALER_COORDS[1]]
    else:
        to_coords = [PLAYER_COORDS[0] + len(player) * CARD_WIDTH / 2, PLAYER_COORDS[1]]
    card_coords = list(SHOE_COORDS)
    delta_x = (to_coords[0] - SHOE_COORDS[0]) / DEAL_FRAMES
    delta_y = (to_coords[1] - SHOE_COORDS[1]) / DEAL_FRAMES
    for i in range(DEAL_FRAMES):
        draw_surface.fill(BG_COLOR)
        player.draw(draw_surface)
        dealer.draw(draw_surface)
        draw_surface.blit(card_back_image, card_coords)
        card_coords[0] += delta_x
        card_coords[1] += delta_y
        if card_coords != SHOE_COORDS:
            draw_surface.blit(card_back_image, card_coords)
        pygame.display.update()
        game_clock.tick(FPS)


def deal_opening_hand(draw_surface, game_clock, card_tile_sheet, card_back_image, player, dealer, shoe):
    x = PLAYER_COORDS[0]
    animate_card_deal(draw_surface, game_clock, card_back_image, player, dealer, 'player')
    player.add(get_card_from_tuple(shoe.pop(), card_tile_sheet, (x, PLAYER_COORDS[1])))
    draw_surface.fill(BG_COLOR)
    player.draw(draw_surface)
    dealer.draw(draw_surface)
    draw_surface.blit(card_back_image, SHOE_COORDS)
    animate_card_deal(draw_surface, game_clock, card_back_image, player, dealer, 'd')
    dealer.add(get_card_from_tuple(shoe.pop(), card_tile_sheet, (x, DEALER_COORDS[1])))
    cover_card = pygame.sprite.Sprite()
    cover_card.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    cover_card.image.blit(card_back_image, (0, 0))
    cover_card.rect = cover_card.image.get_rect()
    cover_card.rect.topleft = (x, DEALER_COORDS[1])
    dealer.add(cover_card)
    x += CARD_WIDTH / 2
    draw_surface.fill(BG_COLOR)
    player.draw(draw_surface)
    dealer.draw(draw_surface)
    draw_surface.blit(card_back_image, SHOE_COORDS)
    animate_card_deal(draw_surface, game_clock, card_back_image, player, dealer, 'p')
    player.add(get_card_from_tuple(shoe.pop(), card_tile_sheet, (x, PLAYER_COORDS[1])))
    draw_surface.fill(BG_COLOR)
    player.draw(draw_surface)
    dealer.draw(draw_surface)
    draw_surface.blit(card_back_image, SHOE_COORDS)
    animate_card_deal(draw_surface, game_clock, card_back_image, player, dealer, 'd')
    dealer.add(get_card_from_tuple(shoe.pop(), card_tile_sheet, (x, DEALER_COORDS[1])))


def draw_hand_total(draw_surface, hand, coords, font):
    total_surf, total_rect = text_sr(str(hand_total(hand)), font)
    total_rect.topleft = (coords[0] + 20, coords[1] + CARD_HEIGHT + 5)
    draw_surface.blit(total_surf, total_rect)


def get_card_from_tuple(card_tuple, sprite_sheet, coords=None):
    card_value = min(card_tuple[0] + 1, 10)
    new_card = Card(card_value)
    x = (CARD_WIDTH - 2) * card_tuple[0]
    y = (CARD_HEIGHT - 2) * card_tuple[1]
    sheet_selection = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    new_card.image.blit(sprite_sheet, (0, 0), sheet_selection)
    if coords is not None:
        new_card.rect.topleft = coords
    return new_card


def get_card_back_sprite(card_back_image, coords=None):
    card_sprite = pygame.sprite.Sprite()
    card_sprite.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    card_sprite.image.blit(card_back_image, (0, 0))
    card_sprite.rect = card_sprite.image.get_rect()
    if coords is not None:
        card_sprite.rect.topleft = coords
    return card_sprite


def hand_total(hand):
    ace = False
    total = 0
    for card_sprite in hand:
        if isinstance(card_sprite, Card):
            total += card_sprite.value
            if card_sprite.value == 1:
                ace = True
    if ace and total < 12:
        total += 10
    return total


def new_decks(num_decks):
    decks = []
    for i in range(num_decks):
        for v in range(13):
            for s in range(4):
                decks.append((v, s))
    return dovetail.shuffle(decks)


def reveal(hand_group):
    for sprite in hand_group:
        if not isinstance(sprite, Card):
            hand_group.remove(sprite)


def terminate():
    pygame.quit()
    sys.exit()


def text_sr(text_string, text_font):
    text_surface = text_font.render(text_string, True, FONT_COLOR, BG_COLOR)
    text_rect = text_surface.get_rect()
    return text_surface, text_rect


class Card(pygame.sprite.Sprite):
    def __init__(self, value, *groups):
        pygame.sprite.Sprite.__init__(self, groups)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect()
        self.value = value


if __name__ == '__main__':
    main()
