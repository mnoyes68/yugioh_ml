import sys
import os
import logging
import json
import pytest
import random

from learning.simulator import Simulator
from learning.ISMCTS import Node, ISMCTS

from yugioh.cards import load_deck_from_file
from yugioh.player import ComputerPlayer
from yugioh.game import Game, DrawPhase, MainPhase, BattlePhase, MainPhase2
import yugioh.actions as actions

import test.utils as utils

from pandas.io.json import json_normalize

random.seed(30)


def test_game_ismcts_begin():
    ygogame = utils.create_training_game(include_model=True)

    p1_tree = ygogame.p1.decisionmanager.buildISMCTS(ygogame, True)
    p2_tree = ygogame.p2.decisionmanager.buildISMCTS(ygogame, False)

    assert p1_tree.source_game.p1.life_points == 4000
    assert p1_tree.source_game.p1.hand.get_size() == 5
    assert p1_tree.source_game.p1.name == "Yugi"

    assert p2_tree.source_game.p2.life_points == 4000
    assert p2_tree.source_game.p2.hand.get_size() == 5
    assert p2_tree.source_game.p2.name == "Opponent"


def test_ismcts_first_step():
    ygogame = utils.create_training_game(include_model=True)
    ygogame.play_full_step()

    tree = ygogame.p1.decisionmanager.buildISMCTS(ygogame, True)

    assert tree.source_game.p1.hand.get_size() == 6
    assert tree.source_game.p2.hand.get_size() == 5


def test_draw_phase_run_draw_simulation():
    ygogame = utils.create_training_game(include_model=True)
    simulator = ygogame.p1.decisionmanager.simulator

    tree = simulator.buildISMCTS(ygogame, True)
    simulator.run_simulation(tree)
    root = tree.root

    assert len(root.edges) == 1
    edge = root.edges[0]
    assert isinstance(edge.action, actions.DrawCard)
    assert root.sims == 1

    # Run additional simulations
    for i in range(0, 10):
        simulator.run_simulation(tree)

    root = tree.root
    assert len(root.edges) == 1
    assert root.sims == 11
    edge = root.edges[0]
    assert isinstance(edge.action, actions.DrawCard)


def test_draw_phase_resolve_simulation():
    ygogame = utils.create_training_game(include_model=True)
    simulator = ygogame.p1.decisionmanager.simulator

    # Run two simulations
    tree = simulator.buildISMCTS(ygogame, True)
    simulator.run_simulation(tree)
    simulator.run_simulation(tree)

    root = tree.root
    assert root.sims == 2
    node = root.edges[0].post_node

    assert len(node.edges) == 1
    edge = node.edges[0]
    assert isinstance(edge.action, actions.Advance)
    node = edge.post_node


def test_draw_phase_advance_simulation():
    ygogame = utils.create_training_game(include_model=True)
    simulator = ygogame.p1.decisionmanager.simulator

    # Run two simulations
    tree = simulator.buildISMCTS(ygogame, True)
    simulator.run_simulation(tree)
    simulator.run_simulation(tree)
    simulator.run_simulation(tree)

    root = tree.root
    assert root.sims == 3
    node = root.edges[0].post_node.edges[0].post_node

    assert len(node.edges) == 1
    edge = node.edges[0]
    assert isinstance(edge.action, actions.Advance)
    node = edge.post_node


def test_inspect_tree():
    # Make sure this test is done default mode
    ygogame = utils.create_training_game(include_model=True)
    simulator = ygogame.p1.decisionmanager.simulator

    tree = simulator.buildISMCTS(ygogame, True)

    for i in range(0, 30):
        simulator.run_simulation(tree)

    root = tree.root
    assert root.sims == 30

    # Draw
    assert len(root.edges) == 1
    edge = root.edges[0]
    assert isinstance(edge.action, actions.DrawCard)
    node = edge.post_node

    # Resolve
    assert len(node.edges) == 1
    edge = node.edges[0]
    assert isinstance(edge.action, actions.Advance)
    node = edge.post_node

    # Advance
    assert len(node.edges) == 1
    edge = node.edges[0]
    assert isinstance(edge.action, actions.Advance)
    node = edge.post_node

    # Summon
    #assert isinstance(node.game.current_phase, MainPhase)
    assert len(node.edges) > 7
    assert len(node.edges) <= 26
    action_set = set(map(lambda e: e.action.__class__, node.edges))
    assert len(action_set) == 2


def test_inspect_tree_opponent_turn():
    # P1 Goes First, view tree from P2 Perspective
    ygogame = utils.create_training_game(include_model=True)
    simulator = ygogame.p2.decisionmanager.simulator

    tree = simulator.buildISMCTS(ygogame, False)

    for i in range(0, 60):
        simulator.run_simulation(tree)

    root = tree.root
    assert root.sims == 60

    # Draw
    assert len(root.edges) == 1
    edge = root.edges[0]
    assert isinstance(edge.action, actions.DrawCard)
    assert edge.action.player == ygogame.p1
    node = edge.post_node

    # Resolve
    assert len(node.edges) == 1
    edge = node.edges[0]
    assert isinstance(edge.action, actions.Advance)
    node = edge.post_node

    # Advance
    assert len(node.edges) == 1
    edge = node.edges[0]
    assert isinstance(edge.action, actions.Advance)
    node = edge.post_node

    # Summon
    assert len(node.edges) > 7
    assert len(node.edges) <= 26
    action_class_set = set(map(lambda e: e.action.__class__, node.edges))
    assert len(action_class_set) == 2

    # Ensure no monster is summoned twice and player is p1 for all moves
    monsters = []
    for edge in node.edges:
        assert edge.action.player == ygogame.p1
        if isinstance(edge.action, actions.NormalSummon):
            assert edge.action.monster not in monsters
            monsters.append(edge.action.monster)


def test_tree_switch_turns():
    # P1 Goes First, view tree from P2 Perspective
    ygogame = utils.create_training_game(include_model=True)

    ygogame.p1.decisionmanager.method = 'default'
    ygogame.p2.decisionmanager.method = 'default'

    utils.setup_direct_attack(ygogame, 'SDY-006')

    ygogame.p1.decisionmanager.method = 'network'
    ygogame.p2.decisionmanager.method = 'network'

    simulator = ygogame.p2.decisionmanager.simulator
    tree = simulator.buildISMCTS(ygogame, True)

    for i in range(0, 1200):
        print('Simulation: ' + str(i+1))
        for edge in tree.root.edges:
            print(edge.action.get_name() + ': ' + str(edge.post_node.score) + ' : ' + str(edge.post_node.sims))
        simulator.run_simulation(tree)
        print('\n')

    node = tree.root
    assert isinstance(ygogame.current_phase, BattlePhase)
    assert len(node.edges) == 2
    action_set = set(map(lambda e: e.action.__class__, node.edges))
    assert len(action_set) == 2
    assert actions.Advance in action_set
    assert actions.DirectAttack in action_set

    assert False


def test_back_propogate():
    # Make sure this test is done default mode
    ygogame = utils.create_training_game(include_model=True)
    simulator = ygogame.p1.decisionmanager.simulator

    tree = simulator.buildISMCTS(ygogame, True)

    for i in range(0, 30):
        simulator.run_simulation(tree)

    # Advance to main phase
    node = tree.root
    for i in range(0, 3):
        edge = node.edges[0]
        node = edge.post_node

    total_sims = 1
    total_score = node.state_score

    for edge in node.edges:
        post_node = edge.post_node
        sims = post_node.sims
        total_sims += sims
        total_score += post_node.score * sims

    calculated_score = float(total_score) / total_sims
    assert calculated_score == node.score














