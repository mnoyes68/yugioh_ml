import copy
import random

from learning.ISMCTS import Node, Edge, ISMCTS
from learning.statedraw import write_game_state

import tensorflow as tf

from pandas.io.json import json_normalize

from time import clock


class Simulator():

    def __init__(self, model, scaler, graph, session):
        self.model = model
        self.scaler = scaler
        self.graph = graph
        self.session = session


    def create_simmed_game(self, game):
        # The machine learning models are removed to ensure this works while in a Flask app, then they are returned
        # Its important that the shuffle_unknown_cards function is called in the ISMCTS
        # to ensure the appropriate moves are available when running the game

        # Reference Models and Graph
        p1_sim = game.p1.decisionmanager.simulator
        p2_sim = game.p2.decisionmanager.simulator

        # Remove Simulators and Graph
        game.p1.decisionmanager.simulator = None
        game.p2.decisionmanager.simulator = None

        # Copy Game
        sim_game = copy.deepcopy(game)

        # Set to default mode
        sim_game.p1.decisionmanager.method = 'default'
        sim_game.p2.decisionmanager.method = 'default'

        # Return Simulators and Graph
        game.p1.decisionmanager.simulator = p1_sim
        game.p2.decisionmanager.simulator = p2_sim

        return sim_game


    def buildISMCTS(self, game, player_perspective):
        sim_game = self.create_simmed_game(game)

        state = self.get_game_state(sim_game, player_perspective)
        score = self.score_state(state)

        return ISMCTS(sim_game, score, player_perspective)


    def get_corresponding_action(self, external_move, action_list):
        # Compares simulation moves with game moves
        for move in action_list:
            if move == external_move:
                return move
        return None


    def run_simulation(self, tree):
        #t0 = clock()
        sim_game = copy.deepcopy(tree.source_game)
        #t1 = clock()
        pre_node, edges, action = tree.select_sim_node(sim_game)
        #t2 = clock()

        if not pre_node.terminal:
            # Simulate the next step using the chosen move
            if action.player == sim_game.current_phase.player:
                move = self.get_corresponding_action(action, sim_game.get_valid_player_moves())
                sim_game.play_step(player_action=move)
            elif action.player == sim_game.current_phase.opponent:
                move = self.get_corresponding_action(action, sim_game.get_valid_opponent_moves())
                sim_game.play_step(opponent_action=move)
            else:
                raise ValueError('Could not identify player of action passed by select_sim_node')

            is_player_turn = self.is_player_turn(sim_game, tree)
            state = self.get_game_state(sim_game, is_player_turn)
            score = self.score_state(state)

            post_node = Node(sim_game.game_is_over, score)
            edge = tree.expand(pre_node, post_node, action)
            edges.append(edge)

        else:
            # Back propogate from the pre node
            post_node = pre_node
        #t3 = clock()

        tree.back_propogate(post_node, edges)
        #t4 = clock()
        '''
        print("Copy Time: " + str(t1-t0))
        print("Select Sim Time: " + str(t2-t1))
        print("Extend Time: " + str(t3-t2))
        print("Back Prop Time: " + str(t4-t3))
        print("Total Time: " + str(t4-t0))
        '''


    def get_game_state(self, game, is_player_turn):
        # Predict score using the network
        if is_player_turn:
            return write_game_state(game.current_phase.player, game.current_phase.opponent)
        else:
            return write_game_state(game.current_phase.opponent, game.current_phase.player)


    def is_player_turn(self, sim_game, tree):
        if tree.player_perspective:
            player = tree.source_game.current_phase.player
        else:
            player = tree.source_game.current_phase.opponent

        return sim_game.current_phase.player == player


    def score_state(self, state):
        # Score the game_state
        dfx = json_normalize([state])
        X = self.scaler.transform(dfx)
        score = self.model.predict(X)[0][0]

        '''
        print("Normalize Time: " + str(t1-t0))
        print("Scaler Time: " + str(t2-t1))
        print("Score Time: " + str(t3-t2))
        print("Total Time: " + str(t3-t0))
        print("\n")
        '''

        return score



