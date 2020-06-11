import sys
import os
import logging
import json
import pytest
import random

import yugioh.actions as actions

import test.utils as utils

from pandas.io.json import json_normalize

random.seed(30)


def test_make_default_decision():
    ygogame = utils.create_training_game(method='default')

    # Move to Main Phase
    ygogame.play_full_step()
    ygogame.play_full_step()

    player_move = ygogame.p1.decisionmanager.make_decision(ygogame)
    opp_move = ygogame.p2.decisionmanager.make_decision(ygogame, player_perspective=False)

    assert isinstance(player_move, actions.Advance)
    assert isinstance(opp_move, actions.Advance)


def test_make_random_decision():
    ygogame = utils.create_training_game()

    # Move to Main Phase
    ygogame.play_full_step()
    ygogame.play_full_step()

    player_move = ygogame.p1.decisionmanager.make_decision(ygogame)
    opp_move = ygogame.p2.decisionmanager.make_decision(ygogame, player_perspective=False)

    assert isinstance(player_move, actions.Action)
    assert isinstance(opp_move, actions.Action)


def test_make_network_decision():
    ygogame = utils.create_training_game(include_model=True)

    # Move to Main Phase
    ygogame.play_full_step()
    ygogame.play_full_step()

    ygogame.p1.decisionmanager.method = 'network'
    ygogame.p2.decisionmanager.method = 'network'

    player_move = ygogame.p1.decisionmanager.make_decision(ygogame)
    opp_move = ygogame.p2.decisionmanager.make_decision(ygogame, player_perspective=False)

    assert isinstance(player_move, actions.NormalSummon)
    assert isinstance(opp_move, actions.Advance)



