import pygame

CARD_WIDTH = 64
CARD_HEIGHT = 88
FONT_NAME = 'timesnewroman'
FONT_SIZE = 18
FONT_COLOR = (255, 215, 0)


class Player(pygame.sprite.OrderedUpdates):

    def __init__(self, start_coords):
        pygame.sprite.OrderedUpdates.__init__(self)
        self.coords = start_coords
        self.bet = 0

    def add_card(self, new_card, flip=True):
        if flip:
            new_card.flip()
        new_card.rect.topleft = (self.coords[0] + len(self) * (CARD_WIDTH / 2), self.coords[1])
        self.add(new_card)

    def draw(self, display):
        pygame.sprite.OrderedUpdates.draw(self, display)
        if self.face_total() > 0:
            total_surf, total_rect = render_text_surf_and_rect(str(self.face_total()))
            total_rect.topleft = (self.coords[0] + 25, self.coords[1] - total_surf.get_height() - 5)
            display.blit(total_surf, total_rect)

    def face_total(self):
        value = 0
        if self:
            ace = False
            for card in self:
                value += card.face_value()
                if card.face_value() == 1:
                    ace = True
            if ace and value <= 11:
                value += 10
        return value


def render_text_surf_and_rect(text, bold=False, italic=False):
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, bold, italic)
    font_surf = font.render(text, False, FONT_COLOR)
    font_rect = font_surf.get_rect()
    return font_surf, font_rect
