# -*- coding: utf-8 -*-
from itertools import combinations


CARD_VALUE_ORDER = 'a23456789tjqk'

SUITS = 'hscd'


class Card(object):

    def __init__(self, value, suit):
        if not suit in set(SUITS):
            raise ValueError('Not a suit.')

        if not value in set(CARD_VALUE_ORDER):
            raise ValueError('Not a value.')

        self.suit = suit
        self.value = value

    @classmethod
    def from_string(cls, card):
        value, suit = card[0], card[1]
        return cls(value, suit)

    def __cmp__(self, other):
        if self.suit != other.suit:
            raise ValueError("Comparing different cards.")

        self_idx = CARD_VALUE_ORDER.index(self.value)
        other_index = CARD_VALUE_ORDER.index(self.value)
        return other_index - self_idx

    def __str__(self):
        return '%s%s' % (self.value, self.suit)

    def __unicode__(self):
        return u'%s%s' % (self.value, self.suit)

    def __repr__(self):
        return "Card('%s', '%s')" % (self.value, self.suit)

    def __hash__(self):
        return hash(str(self))


class Hand(object):

    def __init__(self, cards):
        if len(cards) != 5:
            raise ValueError("A hand has 5 cards.")

        self.cards = cards

    def _sort_by_value(self):
        return ''.join(sorted([card.value for card in self.cards],
                              key=lambda x: CARD_VALUE_ORDER.index(x)))

    def _max(self):
        values = ''.join([card.value for card in sorted(self.cards)])
        if 'a' in values:
            return 'a'
        else:
            return values[-1]

    def _max_values(self):
        self._sort_by_value()[-1]

    def _same_suit(self):
        head = self.cards[0]
        return all(map(lambda card: card.suit == head.suit, self.cards))

    def _count(self):
        count = {}
        for card in self.cards:
            count[card.value] = count.get(card.value, 0) + 1
        return count

    def _straight(self):
        values = self._sort_by_value()
        return values in CARD_VALUE_ORDER

    def is_royal_flush(self):
        royal_flush_values = set(['a', 'k', 'q', 'j', 't'])
        if self._same_suit():
            values = set([card.value for card in self.cards])
            return values == royal_flush_values and 1
        return False

    def is_straight_flush(self):
        return self._same_suit() and self._straight() and 2

    def is_poker(self):
        count = self._count()
        return ([1, 4] == sorted(count.values())) and 3

    def is_full(self):
        count = self._count()
        return ([2, 3] == sorted(count.values())) and 4

    def is_flush(self):
        return self._same_suit() and 5

    def is_straight(self):
        return self._straight() and 6

    def is_set(self):
        return ([1, 1, 3] == sorted(self._count().values())) and 7

    def is_two_pair(self):
        return ([1, 2, 2] == sorted(self._count().values())) and 8

    def is_pair(self):
        return ([1, 1, 1, 2] == sorted(self._count().values())) and 9

    def classify_hand(self):
        for attrname in ('is_royal_flush', 'is_straight_flush',
                         'is_poker', 'is_full', 'is_flush', 'is_straight',
                         'is_set', 'is_two_pair', 'is_pair'):
            handtype = getattr(self, attrname)()
            if handtype:
                return handtype
        return 10

    def human_classify(self):
        klass = {1: 'royal-flush',
                 2: 'straight-flush',
                 3: 'four-of-a-kind',
                 4: 'full-house',
                 5: 'flush',
                 6: 'straight',
                 7: 'three-of-a-kind',
                 8: 'two-pairs',
                 9: 'one-pair',
                 10: 'highest-card'}
        n = self.classify_hand()
        return klass[n]

    def __cmp__(self, other):
        handtype = self.classify_hand()
        other_handtype = other.classify_hand()

        if handtype < other_handtype:
            return 1
        elif handtype > other_handtype:
            return -1
        elif handtype == other_handtype and handtype == 10:
            max_ = self._max_values()
            max_other = other._max_values()
            # The ace plays as the highest card.
            if max_ == max_other:
                return 0
            elif 'a' == max_:
                return 1
            elif 'a' == max_other:
                return -1
            else:
                return (CARD_VALUE_ORDER.index(max_other) -
                        CARD_VALUE_ORDER.index(max_))
        elif handtype == other_handtype:
            return 0

    @classmethod
    def _search_space(cls, hand, deck):
        _hand = set(hand.cards[:])
        for num in xrange(1, 6):
            for t in combinations(_hand, num):
                cards = _hand - set(t)
                cards.update(deck[:num])
                yield cls(list(cards))

    @classmethod
    def search(cls, hand, deck):
        winning_hand = hand
        for new_hand in cls._search_space(hand, deck):
            if new_hand > winning_hand:
                winning_hand = new_hand
        return winning_hand

    def __str__(self):
        return ' '.join(map(str, self.cards))


def guess(hand="", deck=""):
    _hand = Hand([Card.from_string(card) for card in hand.strip().split()])
    _deck = [Card.from_string(card) for card in deck.strip().split()]
    return Hand.search(_hand, _deck).human_classify()


if __name__ == '__main__':
    assert guess("th jh qc qd qs", "qh kh ah 2s 6s") == 'royal-flush'
    assert guess("2h 2s 3h 3s 3c", " 2d 3d 6c 9c th") == 'four-of-a-kind'
    assert guess("2h 2s 3h 3s 3c", " 2d 9c 3d 6c th") == 'full-house'
    assert guess("2h ad 5h ac 7h", " ah 6h 9h 4h 3c") == 'flush'
    assert guess("ac 2d 9c 3s kd", " 5s 4d ks as 4c") == 'straight'
    assert guess("ks ah 2h 3c 4h", " kc 2c tc 2d as") == 'three-of-a-kind'
    assert guess("ah 2c 9s ad 3c", " qh ks js jd kd") == 'two-pairs'
    assert guess("6c 9c 8c 2d 7c", " 2h tc 4c 9s ah") == 'one-pair'
    assert guess("3d 5s 2h qd td", " 6s kh 9h ad qh") == 'highest-card'
