import cards

from learning.decisionmanager import DecisionManager

import string
import random
import logging


class Player():
    def __init__(self, name, deck, portrait, decisionmanager=None, decision_method='default', starting_lp=4000):
        self.name = name
        self.deck = deck
        self.portrait = portrait
        self.hand = Hand()
        self.board = Board()
        self.life_points = starting_lp
        self.memory = []
        self.performance_memory = []
        self.summons_remaining = 0
        self.hashed_id = self.hashed_id = name + ':' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))

        if decisionmanager:
            self.decisionmanager = decisionmanager
        else:
            self.decisionmanager = DecisionManager(None, None, None, None, method='random')


    def make_decision(self, game, player_perspective):
        return self.decisionmanager.make_decision(game, player_perspective)


    def draw_card(self):
        c = self.deck.cards.pop(0)
        self.hand.cards.append(c)
        message = self.name + " drew " + c.name
        logging.debug(message)


    def add_cards_to_deck(self):
        hand_size = self.hand.get_size()
        for i in range(0, hand_size):
            card = self.hand.cards.pop(0)
            self.deck.add_card(card)


    def increase_life_points(self, amount):
        self.life_points += amount


    def decrease_life_points(self, amount):
        self.life_points -= amount
        if self.life_points <= 0:
            self.life_points = 0
            logging.debug("GAME OVER!")

        message = self.name + "'s life points are now " + str(self.life_points)
        logging.debug(message)


    def __eq__(self, other):
        if isinstance(other, Player):
            if other.hashed_id == self.hashed_id:
                return True
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


class Hand():
    def __init__(self):
        self.cards = []


    def add_card(self, card):
        logging.debug('Adding ' + card.name)
        self.cards.append(card)
        return self.cards


    def remove_card(self, card):
        logging.debug('Removing ' + card.name)
        self.cards.remove(card)


    def get_card_by_id(self, card_id):
        for card in self.cards:
            if card.card_id == card_id:
                return card
        raise ValueError("Couldn't locate card in hand with ID: " + card_id)


    def get_cards(self):
        return self.cards


    def get_size(self):
        return len(self.cards)


    def __eq__(self, other):
        if isinstance(other, Hand):
            if self.get_size() != other.get_size():
                return False
            my_cards = sorted(self.get_cards(), key=lambda x: x.card_id)
            op_cards = sorted(other.get_cards(), key=lambda x: x.card_id)
            return my_cards == op_cards
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


class Board():
    def __init__(self):
        self.monster_spaces = []
        self.magic_trap_spaces = []
        self.graveyard = Graveyard()
        for i in range(0,5):
            self.monster_spaces.append(Space("Monster"))
            self.magic_trap_spaces.append(Space("Magic-Trap"))


    def get_occupied_monster_spaces(self):
        occupied_spaces = [s for s in self.monster_spaces if s.occupied == True]
        return len(occupied_spaces)


    def get_monsters(self):
        return [s.card for s in self.monster_spaces if s.occupied == True]


    def destroy_monster(self, monster):
        for space in self.monster_spaces:
            if monster == space.card:
                space.remove_card()
                self.graveyard.add_card(monster)
                message = monster.name + " is now destroyed"
                logging.debug(message)
                break


    def __eq__(self, other):
        if isinstance(other, Board):
            if self.get_occupied_monster_spaces() != other.get_occupied_monster_spaces():
                return False
            my_monsters = sorted(self.get_monsters(), key=lambda x: x.card_id)
            op_monsters = sorted(other.get_monsters(), key=lambda x: x.card_id)
            return my_monsters == op_monsters and self.graveyard == other.graveyard
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


class Graveyard():
    def __init__(self):
        self.cards = []


    def add_card(self, card):
        self.cards.append(card)
        return self.cards


    def remove_card(self, card):
        self.cards.remove(card)


    def get_cards(self):
        return self.cards


    def get_size(self):
        return len(self.cards)


    def __eq__(self, other):
        if isinstance(other, Graveyard):
            if self.get_size() != other.get_size():
                return False
            my_cards = sorted(self.get_cards(), key=lambda x: x.card_id)
            op_cards = sorted(other.get_cards(), key=lambda x: x.card_id)
            return my_cards == op_cards
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


class Space():
    def __init__(self, card_type):
        self.card_type = card_type
        self.occupied = False
        self.card = None

    def add_card(self, card):
        self.card = card
        self.occupied = True

    def remove_card(self):
        self.card = None
        self.occupied = False


class ComputerPlayer(Player):
    player_type = "Computer"

    def __init__(self, name, deck, portrait, model, scaler):
        Player.__init__(self, name, deck, portrait)
        self.model = model
        self.scaler = scaler


class HumanPlayer(Player):
    player_type = "Human"

    def __init__(self, name, deck, portrait):
        Player.__init__(self, name, deck, portrait)


