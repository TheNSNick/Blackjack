import Card
import Hand
import Dovetail

def generate_deck():
    deck = []
    for s in range(4):
        for v in range(1, 14):
            deck.append(Card.Card(v, s))
    return deck

print 'Generating deck.'
deck = generate_deck()
deck = Dovetail.shuffle(deck)
print '{} cards.'.format(len(deck))

print 'Dealing 2 cards...'
hand = Hand.Hand()
for _ in range(2):
    hand.add_card(deck.pop(0))
print hand
print 'Hand is worth {}'.format(hand.bj_value())
if hand.contains_ace():
    print 'and it contains an ace.'
if hand.can_split():
    print 'and it can be split.'
if hand.blackjack():
    print 'and it\'s a blackjack!'
if not hand.can_double():
    print 'But something\'s wrong with Hand.can_double().'

print 'Loading available fonts:'
import pygame
pygame.init()
available_fonts = pygame.font.get_fonts()
for font in available_fonts:
    print font
if 'timesnewroman' in pygame.font.get_fonts():
    test_font = pygame.font.SysFont('timesnewroman', 18)
    print 'Loaded Times New Roman'
else:
    test_font = pygame.font.SysFont(None, 18)