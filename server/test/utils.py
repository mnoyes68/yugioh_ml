import sys
import os
import logging
import json
import random
import pytest

from yugioh.cards import load_deck_from_file
from yugioh.player import Player
from yugioh.game import Game, DrawPhase, MainPhase, BattlePhase, MainPhase2
import yugioh.actions as actions

# from learning.network_factory import initialize_multithread_newtork, create_scaler
from learning.network_factory import initialize_network, create_scaler
from learning.decisionmanager import DecisionManager


## UTILITY FUNCTIONS


def create_training_game(method='random', include_model=False):
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')

    yugi_deck = load_deck_from_file("decks/yugi.json")
    opp_deck = load_deck_from_file("decks/yugi.json")

    yugi_deck.shuffle()
    opp_deck.shuffle()

    if method == 'network' or include_model:
        model1 = initialize_network('learning/models/model_network_ff.h5')
        model2 = initialize_network('learning/models/model_network_ff.h5')

        #model1, graph1, thread_session1 = initialize_multithread_newtork('learning/models/model_network_ff.h5')
        #model2, graph2, thread_session2 = initialize_multithread_newtork('learning/models/model_network_ff.h5')

        scaler1 = create_scaler('learning/models/training_scaler.pkl')
        scaler2 = create_scaler('learning/models/training_scaler.pkl')

        # dm1 = DecisionManager(model1, scaler1, graph1, thread_session1, method='network')
        # dm2 = DecisionManager(model2, scaler2, graph2, thread_session2, method='network')

        dm1 = DecisionManager(model1, scaler1, None, None, method='network')
        dm2 = DecisionManager(model2, scaler2, None, None, method='network')

        yugi = Player("Yugi", yugi_deck, None, decisionmanager=dm1)
        opponent = Player("Opponent", opp_deck, None, decisionmanager=dm2)
    else:
        dm1 = DecisionManager(None, None, None, None, method=method)
        dm2 = DecisionManager(None, None, None, None, method=method)

        yugi = Player("Yugi", yugi_deck, None, decisionmanager=dm1)
        opponent = Player("Opponent", opp_deck, None, decisionmanager=dm2)


    ygogame = Game(yugi, opponent, pre_shuffle=False)

    # Feral Imp, Summoned Skull, Celtic Guardian, Giant Soldier of Stone, Neo the Magic Swordsman
    ygogame.p1.deck.set_first_cards(['SDY-002', 'SDY-004', 'SDY-009', 'SDY-013', 'SDY-035', 'SDY-019'])
    
    # Mystical Elf, Dark Magician, Gaia the Fierce Knight, Mammoth Graveyard, Dragon Zombie, Claw Reacher
    ygogame.p2.deck.set_first_cards(['SDY-001', 'SDY-006', 'SDY-007', 'SDY-010', 'SDY-014', 'SDY-018'])

    ygogame.initialize_game(first_turn=1)
    return ygogame


def setup_one_on_one(ygogame, p1_id, p2_id):
    ygogame.play_phase()

    card = ygogame.p1.hand.get_card_by_id(p1_id)
    move = actions.NormalSummon(ygogame.p1, ygogame.p2, card)

    ygogame.play_full_step(player_action=move)
    ygogame.play_full_step()

    ygogame.play_phase()
    ygogame.play_phase()

    card = ygogame.p2.hand.get_card_by_id(p2_id)
    move = actions.NormalSummon(ygogame.p2, ygogame.p1, card)

    ygogame.play_full_step(player_action=move)
    ygogame.play_full_step()

    return ygogame


def setup_direct_attack(ygogame, p2_id):
    ygogame.play_turn()
    ygogame.play_phase()

    card = ygogame.p2.hand.get_card_by_id(p2_id)
    move = actions.NormalSummon(ygogame.p2, ygogame.p1, card)
    
    ygogame.play_full_step(player_action=move)
    ygogame.play_full_step()

    return ygogame


