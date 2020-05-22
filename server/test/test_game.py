import sys
import os
import logging
import json
import random
import pytest

from yugioh.cards import load_deck_from_file
from yugioh.player import ComputerPlayer
from yugioh.game import Game, DrawPhase, MainPhase, BattlePhase, MainPhase2
import yugioh.actions as actions


random.seed(20)


## UTILITY FUNCTIONS

def create_training_game():
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')

    yugi_deck = load_deck_from_file("decks/yugi.json")
    opp_deck = load_deck_from_file("decks/yugi.json")

    yugi_deck.shuffle()
    opp_deck.shuffle()

    yugi = ComputerPlayer("Yugi", yugi_deck, None, None, None)
    opponent = ComputerPlayer("Opponent", opp_deck, None, None, None)

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


def play_blowout(ygogame):
    ygogame.play_phase()
    move = actions.Advance(ygogame.p1, ygogame.p2)
    ygogame.play_full_step(player_action=move)
    ygogame.play_full_step()

    ygogame.play_phase()
    card1 = ygogame.p2.hand.get_card_by_id('SDY-006') # Dark Magician
    card2 = ygogame.p2.hand.get_card_by_id('SDY-007') # Gaia the Fierce Knight
    move = actions.NormalSummon(ygogame.p2, ygogame.p1, card1)
    ygogame.play_full_step(player_action=move)
    move = actions.NormalSummon(ygogame.p2, ygogame.p1, card2)
    ygogame.play_full_step(player_action=move)

    ygogame.play_full_step()

    move = actions.DirectAttack(ygogame.p2, ygogame.p1, card1)
    ygogame.play_full_step(player_action=move)
    move = actions.DirectAttack(ygogame.p2, ygogame.p1, card2)
    ygogame.play_full_step(player_action=move)

    return ygogame


def confirm_card_list_identity(card_list, id_validation_list):
    card_id_list = list(map(lambda c: c.card_id, card_list))
    for i in id_validation_list:
        try: 
            card_id_list.index(i)
        except:
            return False

    return True


## TESTS

def test_initialize_game():
    ygogame = create_training_game()

    assert ygogame.p1.name == "Yugi"
    assert ygogame.p2.name == "Opponent"

    assert ygogame.p1.life_points == 4000
    assert ygogame.p2.life_points == 4000

    assert ygogame.p1.hand.get_size() == 5
    assert ygogame.p2.hand.get_size() == 5

    assert ygogame.current_phase.player.name == "Yugi"
    assert ygogame.current_phase.opponent.name == "Opponent"
    assert isinstance(ygogame.current_phase, DrawPhase)


def test_first_step():
    ygogame = create_training_game()
    ygogame.play_step()

    # Assert it opens the game with a draw
    assert isinstance(ygogame.current_phase, DrawPhase)
    assert len(ygogame.current_phase.chain) == 1
    assert isinstance(ygogame.current_phase.chain.actions[0], actions.DrawCard)

    assert ygogame.p1.hand.get_size() == 6
    assert len(ygogame.p1.memory) == 1

    assert ygogame.p2.hand.get_size() == 5
    assert len(ygogame.p2.memory) == 1


def test_resolve_first_step():
    ygogame = create_training_game()
    ygogame.play_step()
    ygogame.play_step()

    # Assert it opens the game with a draw
    assert isinstance(ygogame.current_phase, DrawPhase)
    assert len(ygogame.current_phase.chain) == 0

    assert ygogame.p1.hand.get_size() == 6
    assert len(ygogame.p1.memory) == 2

    assert ygogame.p2.hand.get_size() == 5
    assert len(ygogame.p2.memory) == 2


def test_full_step():
    ygogame = create_training_game()
    ygogame.play_full_step()

    # Assert it opens the game with a draw
    assert isinstance(ygogame.current_phase, DrawPhase)
    assert len(ygogame.current_phase.chain) == 0

    assert ygogame.p1.hand.get_size() == 6
    assert len(ygogame.p1.memory) == 2

    assert ygogame.p2.hand.get_size() == 5
    assert len(ygogame.p2.memory) == 2


def test_step_to_main_phase():
    ygogame = create_training_game()
    ygogame.play_full_step()
    ygogame.play_step()

    assert isinstance(ygogame.current_phase, MainPhase)


def test_play_first_main_phase_with_advance():
    ygogame = create_training_game()
    ygogame.play_phase()

    move = actions.Advance(ygogame.p1, ygogame.p2)
    ygogame.play_full_step(player_action=move)
    assert isinstance(ygogame.current_phase, MainPhase2)


def test_play_first_main_phase_with_summon():
    ygogame = create_training_game()
    ygogame.play_phase()

    card = ygogame.p1.hand.get_card_by_id('SDY-002')
    move = actions.NormalSummon(ygogame.p1, ygogame.p2, card)

    ygogame.play_full_step(player_action=move)
    assert ygogame.p1.hand.get_size() == 5
    assert ygogame.p1.board.get_occupied_monster_spaces() == 1
    assert ygogame.p1.board.get_monsters()[0].name == 'Feral Imp'

    assert ygogame.p2.hand.get_size() == 5
    assert ygogame.p2.board.get_occupied_monster_spaces() == 0

    assert isinstance(ygogame.current_phase, MainPhase)


def test_step_to_battle_phase():
    # Will need to be updated with extended tests
    ygogame = create_training_game()
    setup_one_on_one(ygogame, 'SDY-002', 'SDY-007')

    assert isinstance(ygogame.current_phase, BattlePhase)
    assert ygogame.p1.board.get_occupied_monster_spaces() == 1
    assert ygogame.p2.board.get_occupied_monster_spaces() == 1

    assert ygogame.p1.board.get_monsters()[0].name == 'Feral Imp'
    assert ygogame.p2.board.get_monsters()[0].name == 'Gaia the Fierce Knight'


def test_play_turn():
    ygogame = create_training_game()
    ygogame.play_turn()

    assert isinstance(ygogame.current_phase, DrawPhase)
    assert ygogame.turn == ygogame.p2


def test_winning_fight():
    # Will need to be updated with extended tests
    ygogame = create_training_game()
    setup_one_on_one(ygogame, 'SDY-002', 'SDY-007')

    monster = ygogame.p2.board.get_monsters()[0]
    target = ygogame.p1.board.get_monsters()[0]
    move = actions.Attack(ygogame.p2, ygogame.p1, monster, target)

    # Gaia (2300) vs. Feral (1300)
    ygogame.play_full_step(player_action=move)
    assert ygogame.p1.board.get_occupied_monster_spaces() == 0
    assert ygogame.p2.board.get_occupied_monster_spaces() == 1 
    assert ygogame.p1.life_points == 3000
    assert ygogame.p2.life_points == 4000


def test_losing_fight():
    # Will need to be updated with extended tests
    ygogame = create_training_game()
    setup_one_on_one(ygogame, 'SDY-004', 'SDY-010')

    monster = ygogame.p2.board.get_monsters()[0]
    target = ygogame.p1.board.get_monsters()[0]
    move = actions.Attack(ygogame.p2, ygogame.p1, monster, target)

    # Gaia (2300) vs. Feral (1300)
    ygogame.play_full_step(player_action=move)
    assert ygogame.p1.board.get_occupied_monster_spaces() == 1
    assert ygogame.p2.board.get_occupied_monster_spaces() == 0 
    assert ygogame.p1.life_points == 4000
    assert ygogame.p2.life_points == 2700


def test_draw_both_attack_mode():
    # Will need to be updated with extended tests
    ygogame = create_training_game()
    setup_one_on_one(ygogame, 'SDY-004', 'SDY-006')

    monster = ygogame.p2.board.get_monsters()[0]
    target = ygogame.p1.board.get_monsters()[0]
    move = actions.Attack(ygogame.p2, ygogame.p1, monster, target)

    # Gaia (2300) vs. Feral (1300)
    ygogame.play_full_step(player_action=move)
    assert ygogame.p1.board.get_occupied_monster_spaces() == 0
    assert ygogame.p2.board.get_occupied_monster_spaces() == 0 
    assert ygogame.p1.life_points == 4000
    assert ygogame.p2.life_points == 4000


def test_advance_phase():
    # Will need to be updated with extended tests
    ygogame = create_training_game()
    assert ygogame.current_phase.player.name == "Yugi"
    assert ygogame.current_phase.opponent.name == "Opponent"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, MainPhase)
    assert ygogame.current_phase.player.name == "Yugi"
    assert ygogame.current_phase.opponent.name == "Opponent"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, MainPhase2)
    assert ygogame.current_phase.player.name == "Yugi"
    assert ygogame.current_phase.opponent.name == "Opponent"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, DrawPhase)
    assert ygogame.current_phase.player.name == "Opponent"
    assert ygogame.current_phase.opponent.name == "Yugi"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, MainPhase)
    assert ygogame.current_phase.player.name == "Opponent"
    assert ygogame.current_phase.opponent.name == "Yugi"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, BattlePhase)
    assert ygogame.current_phase.player.name == "Opponent"
    assert ygogame.current_phase.opponent.name == "Yugi"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, MainPhase2)
    assert ygogame.current_phase.player.name == "Opponent"
    assert ygogame.current_phase.opponent.name == "Yugi"

    ygogame.play_phase()
    assert isinstance(ygogame.current_phase, DrawPhase)
    assert ygogame.current_phase.player.name == "Yugi"
    assert ygogame.current_phase.opponent.name == "Opponent"


def test_battle_victory():
    ygogame = create_training_game()
    play_blowout(ygogame)

    assert ygogame.p2.life_points == 4000
    assert ygogame.p1.life_points == 0
    assert ygogame.game_is_over
    assert ygogame.winner == ygogame.p2


def test_empty_deck_victory():
    ygogame = create_training_game()
    ygogame.p1.deck.cards = []
    ygogame.play_full_step()

    assert ygogame.game_is_over
    assert ygogame.winner == ygogame.p2


def test_draw():
    ygogame = create_training_game()
    ygogame.p1.life_points = 0
    ygogame.p2.life_points = 0
    ygogame.play_full_step()

    assert ygogame.game_is_over
    assert ygogame.winner == None
    assert ygogame.ended_in_draw


def test_shuffle_unknown_cards():
    ygogame = create_training_game()

    assert confirm_card_list_identity(ygogame.p1.hand.cards, ['SDY-002', 'SDY-004', 'SDY-009', 'SDY-013', 'SDY-035'])
    assert confirm_card_list_identity(ygogame.p2.hand.cards, ['SDY-001', 'SDY-006', 'SDY-007', 'SDY-010', 'SDY-014'])

    ygogame.shuffle_unknown_cards(True) # P1 Perspective, shuffle P2 cards
    assert confirm_card_list_identity(ygogame.p1.hand.cards, ['SDY-002', 'SDY-004', 'SDY-009', 'SDY-013', 'SDY-035'])
    assert not confirm_card_list_identity(ygogame.p2.hand.cards, ['SDY-001', 'SDY-006', 'SDY-007', 'SDY-010', 'SDY-014'])

    ygogame = create_training_game()
    ygogame.shuffle_unknown_cards(False) # P2 Perspective, shuffle P1 cards
    assert not confirm_card_list_identity(ygogame.p1.hand.cards, ['SDY-002', 'SDY-004', 'SDY-009', 'SDY-013', 'SDY-035'])
    assert confirm_card_list_identity(ygogame.p2.hand.cards, ['SDY-001', 'SDY-006', 'SDY-007', 'SDY-010', 'SDY-014'])



