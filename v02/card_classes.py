import os, pygame
from pygame.locals import *

pygame.init()


class Card(pygame.sprite.Sprite):

    width, height = (64, 88)
    spritesheet = pygame.image.load(os.path.join('gfx', 'card_front_sheet.png'))
    back = pygame.image.load(os.path.join('gfx', 'card_back_crosshatch.png'))

    def __init__(self, *args, **kwargs):
        pygame.sprite.Sprite.__init__(self, args)
        assert 'value' in kwargs.keys(), 'Card.__init__(): No value given.'
        assert 1 <= int(kwargs['value']) <= 13, 'Card.__init__(): Invalid value.'
        assert 'suit' in kwargs.keys(), 'Card.__init__(): No suit given.'
        assert 0 <= int(kwargs['suit']) <= 3, 'Card.__init__(): Invalid suit.'
        self.value = int(kwargs['value'])
        self.suit = int(kwargs['suit'])
        self.image = pygame.Surface((self.width, self.height))
        fetch_face = True
        if 'face_down' in kwargs.keys():
            if kwargs['face_down']:
                self.image = self.back
                fetch_face = False
        if fetch_face:
            sub_rect = pygame.Rect((self.value - 1) * (self.width - 2), self.suit * (self.height - 2), self.width, self.height)
            self.image.blit(self.spritesheet, (0, 0), sub_rect)
        self.rect = self.image.get_rect()
        if 'coords' in kwargs.keys():
            self.rect.topleft = kwargs['coords']

    def face_value(self):
        if self.value < 11:
            return self.value
        else:
            return 10

    def flip_up(self):
        sub_rect = pygame.Rect((self.value - 1) * (self.width - 2), self.suit * (self.height - 2), self.width, self.height)
        self.image.blit(self.spritesheet, (0, 0), sub_rect)


class Hand:

    bg_color = (0, 114, 0)
    font_color = (255, 215, 0)

    def __init__(self, *args):
        self.surface = pygame.Surface((400, 200))
        self.cards = pygame.sprite.OrderedUpdates()
        for arg in args:
            if hasattr(arg, '__iter__'):
                for c in arg:
                    if isinstance(c, Card):
                        c.rect.topleft = (10 + len(self.cards) * 20, 100)
                        self.cards.add(c)
            else:
                if isinstance(arg, Card):
                    arg.rect.topleft = (10, 100)
                    self.cards.add(arg)

    def draw(self, display, **kwargs):
        self.surface.fill(self.bg_color)
        self.cards.draw(self.surface)
        pen = pygame.font.SysFont('arial', 18)
        total_surf = pen.render(str(self.total()))

    def total(self, ignore_first=False):
        total = 0
        skip = ignore_first
        for card in self.cards:
            if skip:
                skip = False
            else:
                total += card.face_value()
        return total
