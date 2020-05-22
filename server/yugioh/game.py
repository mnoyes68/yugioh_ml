import cards
import player

from actions import Advance, DrawCard, NormalSummon, Attack, DirectAttack, Chain, EmptyDeckDrawError, group_actions_by_name

import math
import json
import numpy as np
import pdb
import tensorflow as tf

from pandas.io.json import json_normalize
from timeit import default_timer as timer
from sklearn import preprocessing

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras.layers import Flatten
from keras import regularizers

import copy
import random
import operator
import logging

from learning.statedraw import write_game_state

logging.basicConfig(filename='yugioh_game.log', level=logging.INFO, filemode='w')


class Game():
    def __init__(self, p1, p2, pre_shuffle=True, graph=None):
        self.p1 = p1
        self.p2 = p2
        self.turn_number = 1
        self.winner = None
        self.game_is_over = False
        self.game_has_begun = False
        self.ended_in_draw = False
        self.console = ["Console Initialized"]
        self.pre_shuffle = pre_shuffle
        self.graph = graph


    def play_game(self):
        if self.game_is_over:
            return

        if not self.game_has_begun:
            self.initialize_game()

        while not self.game_is_over:
            self.play_turn()

        self.declare_winner()


    def begin_turn(self):
        self.turn.summons_remaining = 1
        for monster in self.turn.board.get_monsters():
            monster.attacked_this_turn = False


    def play_turn(self):
        if self.is_game_over():
            return False

        turn_player = self.turn

        while turn_player == self.turn:
            self.play_phase()

        if self.game_is_over:
            return False
        return True


    def play_phase(self):
        if self.is_game_over():
            return False

        phase_in_progress = True
        while phase_in_progress:
            phase_in_progress = self.play_step()
        if self.is_game_over():
            return False


    def play_full_step(self, player_action=None, opponent_action=None):
        phase_continue = self.play_step(player_action=player_action, opponent_action=opponent_action)
        while self.current_phase.state_open and phase_continue:
            phase_continue = self.play_step()


    def play_step(self, player_action=None, opponent_action=None):
        self.write_state()
        if self.is_game_over():
            return False

        if not player_action:
            player_action = self.cpu_select_player_move()
        if not opponent_action:
            opponent_action = self.cpu_select_opponent_move()

        try:
            phase_continue, console_description = self.current_phase._execute_step(player_action, opponent_action)
        except EmptyDeckDrawError:
            self.game_is_over = True
            self.declare_winner(draw_error_player=self.turn)
            return False

        if console_description:
            self.console.append(console_description)

        # Change Phase Here if not phase continue
        if self.is_game_over():
            self.declare_winner()
            return False
        if not phase_continue:
            self.change_phase()

        return phase_continue


    def change_phase(self):
        self.console.append(self.current_phase.name + ' Complete')
        phase_index = self.phase_list.index(self.current_phase) + 1
        if phase_index == len(self.phase_list):
            self.change_turn()
            return False
        else:
            self.current_phase = self.phase_list[phase_index]

        self.console.append('Beginning ' + self.current_phase.name)
        return True


    def change_turn(self):
        self.console.append(self.turn.name + "'s turn is over")
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
        self.turn_number += 1
        self.begin_turn()
        self.console.append("It is now " + self.turn.name + "'s turn")
        self.phase_list = self.get_phase_list(self.turn, self.get_opponent())
        self.current_phase = self.phase_list[0]


    def flip_coin(self):
        return random.randint(0, 1)


    def get_default_player_move(self):
        return self.current_phase.get_default_player_move()


    def get_default_opponent_move(self):
        return self.current_phase.get_default_opponent_move()


    def get_valid_player_moves(self):
        return self.current_phase.get_valid_player_moves()


    def get_valid_opponent_moves(self):
        return self.current_phase.get_valid_opponent_moves()


    def cpu_select_player_move(self):
        return self.turn.make_decision(self, True)


    def cpu_select_opponent_move(self, move=None):
        return self.get_opponent().make_decision(self, False)


    def is_game_over(self):
        if self.p1.life_points <= 0 or self.p2.life_points <= 0:
            self.game_is_over = True
            self.declare_winner()
        return self.game_is_over


    def get_opponent(self):
        if self.turn == self.p1:
            return self.p2
        else:
            return self.p1


    def get_player(self):
        if self.turn == self.p1:
            return self.p1
        else:
            return self.p2


    def get_whos_turn_number(self):
        if self.turn == self.p1:
            return 1
        else:
            return 2


    def get_phase_list(self, player, opponent):
        turn = self.get_whos_turn_number()
        turn_number = self.turn_number

        phase_list = []
        phase_list.append(DrawPhase(player, opponent, turn, turn_number))
        phase_list.append(MainPhase(player, opponent, turn, turn_number))
        if self.turn_number > 1:
            phase_list.append(BattlePhase(player, opponent, turn, turn_number))
        phase_list.append(MainPhase2(player, opponent, turn, turn_number))
        return phase_list


    def select_move_priority(self, player_move, opponent_move):
        return self.current_phase.select_move_priority(player_move, opponent_move)


    # Functions for launching game
    def initialize_game(self, first_turn=None):
        if self.pre_shuffle:
            self.p1.deck.shuffle()
            self.p2.deck.shuffle()
        for i in range (0,5):
            self.p1.draw_card()
            self.p2.draw_card()
        self.begin_game(first_turn=first_turn)


    def begin_game(self, first_turn=None):
        logging.debug('\n' + "BEGIN GAME!!!" + '\n')
        self.console.append('BEGIN GAME!!!')

        # Decide whos turn it is
        self.decide_first_turn(first_turn=first_turn)
        logging.debug(self.turn.name + " goes first")

        self.phase_list = self.get_phase_list(self.turn, self.get_opponent())
        self.current_phase = self.phase_list[0]
        self.game_has_begun = True
        self.begin_turn()


    def decide_first_turn(self, first_turn=None):
        if first_turn == 1:
            self.turn = self.p1 
        elif first_turn == 2:
            self.turn = self.p2
        else:
            coin_flip = self.flip_coin()
            if coin_flip == 0:
                self.turn = self.p1 
            else:
                self.turn = self.p2


    def declare_winner(self, draw_error_player=None):
        if self.winner or self.ended_in_draw:
            return
            
        self.write_state()

        if draw_error_player == self.p1:
            self.winner = self.p2
        elif draw_error_player == self.p2:
            self.winner = self.p1
        else:
            if self.p1.life_points <= 0 and self.p2.life_points > 0:
                self.winner = self.p2
            elif self.p2.life_points <= 0 and self.p1.life_points > 0:
                self.winner = self.p1
            else:
                self.ended_in_draw = True
        self.console.append('GAME OVER')

        if self.ended_in_draw:
            self.console.append('Game Ended In a Draw')
        else:
            self.console.append('Winner: ' + self.winner.name)


    def shuffle_unknown_cards(self, player_perspective):
        if player_perspective:
            player = self.turn
            opponent = self.get_opponent()
        else:
            player = self.get_opponent()
            opponent = self.turn

        opp_hand_size = opponent.hand.get_size()
        opp_hand_cards = opponent.hand.get_cards()

        opponent.add_cards_to_deck()

        player.deck.shuffle()
        opponent.deck.shuffle()

        for i in range(0, opp_hand_size):
            opponent.draw_card()


    def get_console(self):
        return '\n'.join(self.console)


    def write_state(self):
        # Used to write game as JSON state to the players memories for Machine Learning methods
        self.turn.memory.append(write_game_state(self.turn, self.get_opponent()))
        self.get_opponent().memory.append(write_game_state(self.get_opponent(), self.turn))
        # self.turn.memory.append(write_game_state(self))
        # self.get_opponent().memory.append(write_game_state(self, opp_perspective=True))


    def get_move_from_action(self, action, opp_perspective=False):
        # Compares action from client to game moves
        if action:
            # Find the related action for the appropriate player
            if opp_perspective:
                move_list = [self.cpu_select_opponent_move()]
            else:
                move_list = self.get_valid_player_moves()

            # Search for move
            for move in move_list:
                if move.is_serial_equal(action):
                    return move
            raise ValueError('Action could not be recognized')
        else:
            # Use CPU to get the move if null
            if opp_perspective:
                return self.cpu_select_opponent_move()
            else:
                return self.cpu_select_player_move()


    def serialize(self, group_actions=False):
        # Used to write game as JSON for the UI
        game_json = {}

        # Players
        game_json['PlayerName'] = self.p1.name
        game_json['PlayerLP'] = self.p1.life_points
        game_json['PlayerPortrait'] = self.p1.portrait
        
        game_json['OpponentName'] = self.p2.name
        game_json['OpponentLP'] = self.p2.life_points
        game_json['OpponentPortrait'] = self.p2.portrait

        #Turn
        if self.turn == self.p1:
            game_json['Turn'] = 1
        else:
            game_json['Turn'] = 2
        game_json['Phase'] = self.current_phase.name

        # State
        game_json['StateOpen'] = self.current_phase.state_open

        # Hand
        player_hand = []
        for card in self.p1.hand.cards:
            player_hand.append(card.serialize())
        game_json['PlayerHand'] = player_hand
        game_json['OppHandSize'] = len(self.p2.hand.cards)

        # Actions
        player_actions = []
        if self.turn == self.p1:
            for action in self.get_valid_player_moves():
                player_actions.append(action.serialize())
        else:
            for action in self.get_valid_opponent_moves():
                player_actions.append(action.serialize())
        if group_actions:
            game_json['PlayerActions'] = group_actions_by_name(player_actions)
        else:
            game_json['PlayerActions'] = player_actions

        # Board Spaces
        self.populate_if_present('PlayerMonster1', self.p1, 0, game_json)
        self.populate_if_present('PlayerMonster2', self.p1, 1, game_json)
        self.populate_if_present('PlayerMonster3', self.p1, 2, game_json)
        self.populate_if_present('PlayerMonster4', self.p1, 3, game_json)
        self.populate_if_present('PlayerMonster5', self.p1, 4, game_json)
        self.populate_if_present('OpponentMonster1', self.p2, 0, game_json)
        self.populate_if_present('OpponentMonster2', self.p2, 1, game_json)
        self.populate_if_present('OpponentMonster3', self.p2, 2, game_json)
        self.populate_if_present('OpponentMonster4', self.p2, 3, game_json)
        self.populate_if_present('OpponentMonster5', self.p2, 4, game_json)

        # Console
        game_json['Console'] = self.console

        #print(json.dumps(game_json, indent=2))
        return game_json


    def populate_if_present(self, key, player, index, json_object):
        try:
            json_object[key] = player.board.monster_spaces[index].card.serialize()
        except:
            pass


class Phase():
    def __init__(self, player, opponent, turn, turn_number):
        self.player = player
        self.opponent = opponent
        self.turn = turn
        self.turn_number = turn_number
        self.name = ""
        self.chain = Chain()
        self.state_open = False


    def get_default_player_move(self):
        # Overriden on Draw Phase to mandate draw
        return Advance(self.player, self.opponent, is_default=True)


    def get_default_opponent_move(self):
        return Advance(self.opponent, self.player, is_default=True)


    def get_valid_player_moves(self):
        raise NotImplementedError('users must define to use this base class')


    def get_valid_opponent_moves(self):
        return [self.get_default_opponent_move()]


    '''
    Removing these functions because they 
    def cpu_select_player_move(self):
        return self.player.make_decision(self, True)


    def cpu_select_opponent_move(self, move=None):
        return self.opponent.make_decision(self, False)
    '''


    def record_actions(self, actions):
        pass


    def _execute_step(self, player_move=None, opponent_move=None):
        # TODO refactor to make decision manager in charge instead of default selection
        if not player_move:
            player_move = self.get_default_player_move()
            #player_move = self.cpu_select_player_move()
        if not opponent_move:
            opponent_move = self.get_default_opponent_move()
            #opponent_move = self.cpu_select_opponent_move()

        # Determine what to do about the moves
        if isinstance(player_move, Advance) and isinstance(opponent_move, Advance):
            if len(self.chain) == 0:
                # Advance phase
                return False, None
            else:
                # Resolve chain
                action_list = self.chain.resolve()
                self.record_actions(action_list)
                self.state_open = False
                return True, None
        else:
            # Add move to chain
            move = self.select_move_priority(player_move, opponent_move)
            self.chain.add(move)
            self.state_open = True
            return True, move.get_console_description()


    def select_move_priority(self, player_move, opponent_move):
        # Select the other move if one is Advance
        if isinstance(opponent_move, Advance):
            return player_move
        if isinstance(player_move, Advance):
            return opponent_move

        # Select by higher speed
        if player_move.speed > opponent_move.speed:
            return player_move
        elif opponent_move.speed > player_move.speed:
            return opponent_move
        else:
            # Select player or opposite turn player
            if len(self.chain.actions) == 0:
                return player_move
            elif self.chain.actions[-1].player == self.player:
                return opponent_move
            elif self.chain.actions[-1].player == self.opponent:
                return player_move
            else:
                raise Exception("Issue with player definition, couldn't locate action player")


class DrawPhase(Phase):
    def __init__(self, player, opponent, turn, turn_number):
        Phase.__init__(self, player, opponent, turn, turn_number)
        self.name = "Draw Phase"
        self.has_drawn = False


    def get_default_player_move(self):
        if not self.state_open and not self.has_drawn:
            return DrawCard(self.player, self.opponent, is_default=True)
        else:
            return Advance(self.player, self.opponent, is_default=True)


    def get_valid_player_moves(self):
        move_list = []
        move_list.append(self.get_default_player_move())
        return move_list


    def record_actions(self, action_list):
        for action in action_list:
            if isinstance(action, DrawCard):
                self.has_drawn = True
                break


class MainPhase(Phase):
    def __init__(self, player, opponent, turn, turn_number):
        Phase.__init__(self, player, opponent, turn, turn_number)
        self.name = "Main Phase"


    def get_valid_player_moves(self):
        move_list = []
        move_list.append(self.get_default_player_move())
        if len(self.player.board.get_monsters()) < 5 and len(self.player.hand.cards) > 0 and self.player.summons_remaining > 0 and not self.state_open:
            move_list.extend(self.get_summons())
        return move_list


    def get_summons(self):
        summon_list = []
        if self.player.summons_remaining > 0:
            for card in self.player.hand.get_cards():
                if isinstance(card, cards.MonsterCard):
                    move = NormalSummon(self.player, self.opponent, card)
                    summon_list.append(move)
        return summon_list


    def record_actions(self, action_list):
        for action in action_list:
            if isinstance(action, NormalSummon):
                self.player.summons_remaining = 0
                break


class BattlePhase(Phase):
    def __init__(self, player, opponent, turn, turn_number):
        Phase.__init__(self, player, opponent, turn, turn_number)
        self.name = "Battle Phase"


    def get_valid_player_moves(self):
        move_list = []
        move_list.append(self.get_default_player_move())
        if not self.state_open:
            move_list.extend(self.get_attacks())
        return move_list


    def get_attacks(self):
        attacks = []
        if self.opponent.board.get_occupied_monster_spaces() == 0:
            for monster in self.player.board.get_monsters():
                if monster.attacked_this_turn == False:
                    move = DirectAttack(self.player, self.opponent, monster)
                    attacks.append(move)
        else:
            for monster in self.player.board.get_monsters():
                if monster.attacked_this_turn == False:
                    for target in self.opponent.board.get_monsters():
                        move = Attack(self.player, self.opponent, monster, target)
                        attacks.append(move)
        return attacks


class MainPhase2(Phase):
    def __init__(self, player, opponent, turn, turn_number):
        Phase.__init__(self, player, opponent, turn, turn_number)
        self.name = "Main Phase 2"


    def get_valid_player_moves(self):
        move_list = []
        move_list.append(self.get_default_player_move())
        return move_list

