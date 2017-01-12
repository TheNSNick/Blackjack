class Card:
    value_short_name = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                        8: '8', 9: '9', 10: '10', 11:'J', 12: 'Q', 13: 'K'}
    value_long_name = {1: 'ace', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
                        8: 'eight', 9: 'nine', 10: 'ten', 11:'jack', 12: 'queen', 13: 'king'}
    suit_short_name = {0: 'h', 1: 's', 2: 'd', 3: 'c'}
    suit_long_name = {0: 'hearts', 1: 'spades', 2: 'diamonds', 3: 'clubs'}

    def __init__(self, value, suit):
        if int(value) in self.value_short_name.keys():
            self.value = int(value)
        else:
            raise ValueError('Card() init: invalid value: {}'.format(value))
        if int(suit) in self.suit_short_name.keys():
            self.suit = int(suit)
        else:
            raise ValueError('Card() init: invalid suit: {}'.format(suit))

    def __repr__(self):
        return '{}{}'.format(self.value_short_name[self.value], self.suit_short_name[self.suit])

    def full_name(self):
        return '{} of {}'.format(self.value_long_name[self.value], self.suit_long_name[self.suit])

    def bj_value(self):
        if self.value < 10:
            return self.value
        else:
            return 10