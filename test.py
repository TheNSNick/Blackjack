import sys
import pygame
import Card01

pygame.init()
screen = pygame.display.set_mode((200, 200))
ace = Card01.Card(1, 1)
cards = pygame.sprite.Group(ace)
two = Card01.Card(2, 3, start_coords=(Card01.CARD_WIDTH, 0))
cards.add(two)
cards.draw(screen)
pygame.display.update()
while True:
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            pygame.quit()
            sys.exit()
