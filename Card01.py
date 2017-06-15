import os
import pygame
from pygame.locals import *

CARD_WIDTH = 64
CARD_HEIGHT = 88
SHEET_FILE = os.path.join('gfx', 'card_front_sheet.png')
BACK_FILE = os.path.join('gfx', 'card_back_crosshatch.png')


class Card(pygame.sprite.Sprite):

    def __init__(self, value, suit, face_up=True, start_coords=None):
        assert 1 <= int(value) <= 13, 'Card.init(): Invalid value passed: {}'.format(value)
        assert 0 <= int(suit) <= 3, 'Card.init(): Invalid suit passed: {}'.format(suit)
        pygame.sprite.Sprite.__init__(self)
        self.value = int(value)
        self.suit = int(suit)
        self.face_up = face_up
        self.image = pygame.Surface((0, 0))
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.load_image_and_rect(start_coords)

    def face_value(self):
        if not self.face_up:
            return 0
        elif self.value < 10:
            return self.value
        else:
            return 10

    def flip(self):
        self.face_up = not self.face_up
        self.load_image_and_rect()

    def load_image_and_rect(self, rect_coords=None):
        if self.face_up:
            sheet = pygame.image.load(SHEET_FILE).convert()
            sub_rect = Rect((self.value - 1) * (CARD_WIDTH - 2), self.suit * (CARD_HEIGHT - 2), CARD_WIDTH, CARD_HEIGHT)
            self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.image.blit(sheet, (0, 0), sub_rect)
        else:
            self.image = pygame.image.load(BACK_FILE).convert()
        if rect_coords is None:
            self.rect.width = CARD_WIDTH
            self.rect.height = CARD_HEIGHT
        else:
            self.rect = Rect(rect_coords[0], rect_coords[1], CARD_WIDTH, CARD_HEIGHT)
