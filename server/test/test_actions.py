import logging
import json
import random
import pytest
import copy

from yugioh.cards import load_deck_from_file
from yugioh.player import ComputerPlayer
from yugioh.game import Game

import yugioh.actions as actions

import test.utils as utils


def test_draw_card_equality():
    ygogame = utils.create_training_game()

    action1 = actions.DrawCard(ygogame.p1, ygogame.p2)
    action2 = actions.DrawCard(ygogame.p2, ygogame.p1)
    action3 = copy.deepcopy(action1)

    assert action1 == action3
    assert action1 != action2


def test_advance_equality():
    ygogame = utils.create_training_game()

    action1 = actions.Advance(ygogame.p1, ygogame.p2)
    action2 = actions.Advance(ygogame.p2, ygogame.p1)
    action3 = copy.deepcopy(action1)

    assert action1 == action3
    assert action1 == action2


def test_normal_summon_equality():
    ygogame = utils.create_training_game()

    action1 = actions.NormalSummon(ygogame.p1, ygogame.p2, ygogame.p1.hand.cards[0])
    action2 = actions.NormalSummon(ygogame.p2, ygogame.p1, ygogame.p2.hand.cards[0])
    action3 = copy.deepcopy(action1)

    assert action1 == action3
    assert action1 != action2 


def test_attack_equality():
    ygogame = utils.create_training_game()

    action1 = actions.Attack(ygogame.p1, ygogame.p2, ygogame.p1.hand.cards[0], ygogame.p2.hand.cards[0])
    action2 = actions.Attack(ygogame.p2, ygogame.p1, ygogame.p2.hand.cards[0], ygogame.p1.hand.cards[0])
    action3 = copy.deepcopy(action1)

    assert action1 == action3
    assert action1 != action2


def test_direct_attack_equality():
    ygogame = utils.create_training_game()

    action1 = actions.DirectAttack(ygogame.p1, ygogame.p2, ygogame.p1.hand.cards[0])
    action2 = actions.DirectAttack(ygogame.p2, ygogame.p1, ygogame.p2.hand.cards[0])
    action3 = copy.deepcopy(action1)

    assert action1 == action3
    assert action1 != action2 


