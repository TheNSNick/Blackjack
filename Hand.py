import Card


class Hand:

    def __init__(self, start_hand=[]):
        self.cards = []
        self.cards.extend(start_hand)

    def __iter__(self):
        return self.cards.__iter__()

    def __repr__(self):
        return str(self.cards)

    def __len__(self):
        return len(self.cards)

    def contains_ace(self):
        for c in self.cards:
            if c.bj_value() == 1:
                return True
        return False

    def bj_value(self, dealer_hide=False):
        total = 0
        for c in self.cards:
            if not dealer_hide:
                total += c.bj_value()
            else:
                dealer_hide = False
        if total <= 11 and self.contains_ace():
            total += 10
        return total

    def add_card(self, new_card):
        self.cards.append(new_card)

    def add_cards(self, new_cards):
        self.cards.extend(new_cards)

    def clear(self):
        self.cards = []

    def blackjack(self):
        if len(self.cards) == 2:
            if self.bj_value() == 21:
                return True
        return False

    def can_split(self):
        if len(self.cards) == 2:
            if self.cards[0].value == self.cards[1].value:
                return True
        return False

    def can_double(self):
        return len(self.cards) == 2

    def is_bust(self):
        return self.bj_value() > 21
