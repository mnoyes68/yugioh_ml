import sys
import os
import logging
import json
import random
import pytest
import copy

from yugioh.cards import load_deck_from_file
from yugioh.player import ComputerPlayer
from yugioh.game import Game


def create_training_game():
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')

    yugi_deck = load_deck_from_file("decks/yugi.json")
    opp_deck = load_deck_from_file("decks/yugi.json")

    yugi = ComputerPlayer("Yugi", yugi_deck, None, None, None)
    opponent = ComputerPlayer("Opponent", opp_deck, None, None, None)

    ygogame = Game(yugi, opponent)

    return ygogame


def test_set_first_cards():
    ygogame = create_training_game()

    ygogame.p1.deck.set_first_cards(['SDY-002', 'SDY-004', 'SDY-009', 'SDY-013', 'SDY-035'])
    assert ygogame.p1.deck.cards[0].name == 'Feral Imp'
    assert ygogame.p1.deck.cards[1].name == 'Summoned Skull'
    assert ygogame.p1.deck.cards[2].name == 'Celtic Guardian'
    assert ygogame.p1.deck.cards[3].name == 'Giant Soldier of Stone'
    assert ygogame.p1.deck.cards[4].name == 'Neo the Magic Swordsman'


def test_copy():
    ygogame = create_training_game()
    card = ygogame.p1.deck.cards[0]
    copy_card = copy.copy(card)
    assert card == copy_card
    assert card.hashed_id == copy_card.hashed_id
