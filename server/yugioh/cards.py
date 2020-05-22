import logging
import random
import copy
import actions
import json
import string


class Card():
    def __init__(self, name, card_id):
        self.name = name
        self.card_id = card_id
        self.hashed_id = card_id + ':' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))


    def serialize():
        raise NotImplementedError('users must define to use this base class')


    def __eq__(self, other):
        if isinstance(other, Card):
            return self.hashed_id == other.hashed_id
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("Card:" + self.hashed_id)


class MonsterCard(Card):
    card_type = "Monster"


    def __init__(self, name, card_id, atk, defn, level, img):
        Card.__init__(self, name, card_id)
        self.atk = atk
        self.defn = defn
        self.level = level
        self.attacked_this_turn = False
        self.img = img


    def serialize(self):
        card_json = {}
        card_json['Name'] = self.name
        card_json['Attack'] = self.atk
        card_json['Defense'] = self.defn
        card_json['Level'] = self.level
        card_json['AttackedThisTurn'] = self.attacked_this_turn
        card_json['CardID'] = self.card_id
        card_json['img'] = self.img 
        return card_json


class Deck():
    def __init__(self, cards, shuffle=True):
        self.cards = cards
        if shuffle:
            self.shuffle()


    def shuffle(self):
        random.shuffle(self.cards)


    def add_card(self, card):
        logging.debug('Adding ' + card.name)
        self.cards.append(card)


    def remove_card(self, card):
        logging.debug('Removing ' + card.name)
        self.cards.remove(card)


    def get_card_by_id(self, card_id):
        for card in self.cards:
            if card.card_id == card_id:
                return card
        raise ValueError("Couldn't locate card in deck with ID: " + card_id)


    def get_size(self):
        return len(self.cards)


    def set_first_cards(self, id_list):
        cards_to_add = []
        for card_id in id_list:
            card = self.get_card_by_id(card_id)
            self.remove_card(card)
            cards_to_add.append(card)

        cards_to_add.reverse()
        for card in cards_to_add:
            self.cards.insert(0, card)


    def __len__(self):
        return self.cards.__len__()


# Utility functions
def load_deck_from_file(deck_file):
    with open(deck_file, "r") as deck:
        deck_json = json.loads(deck.read())
        deck_list = []
        for c in deck_json:
            card = MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'), c.get('img'))
            deck_list.append(card)
        deck = Deck(deck_list, shuffle=False)
        return deck









