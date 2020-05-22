import random
import math
import numpy as np
import logging


class Node():

    def __init__(self, terminal, score):
        self.terminal = terminal
        self.score = score
        self.state_score = score
        self.edges = []
        self.sims = 0


    def get_actions(self):
        actions = []
        for edge in self.edges:
            actions.append(edge.action)
        return actions


    def get_edge_by_action(self, action):
        for edge in self.edges:
            if edge.action == action:
                return edge
        return None


class Edge():
    def __init__(self, pre_node, post_node, action):
        self.pre_node = pre_node
        self.post_node = post_node
        self.action = action
        

class ISMCTS():

    def __init__(self, source_game, root_score, player_perspective):
        self.source_game = source_game
        self.player_perspective = player_perspective

        root = Node(source_game.game_is_over, root_score)
        self.root = root


    def select_sim_node(self, game):
        current_node = self.root
        # Ensure we have a new set of possible moves
        # Must be done here as opposed to the simulator 
        # to ensure that the moves are available
        game.shuffle_unknown_cards(self.player_perspective)
        breadcrumb_edges = []

        while True:
            if current_node.terminal:
                # Return if the node is terminal
                return current_node, breadcrumb_edges, None

            is_player_turn = self.is_player_turn(game)
            player_action = self.choose_action(current_node, game.get_valid_player_moves(), is_player_turn)
            opp_action = self.choose_action(current_node, game.get_valid_opponent_moves(), not is_player_turn)

            # Here we choose the move that will be executed using the 
            # select_move_priority function of the game
            action = game.select_move_priority(player_action, opp_action)
            edge = current_node.get_edge_by_action(action)

            # If we find an edge we move to it and continue
            # Otherwise we return the actions to be simulated
            # We play the step to maintain any randomly selected cards
            # (e.g. Drawing a card) that were done in previous steps 
            if edge:
                game.play_step()
                breadcrumb_edges.append(edge)
                current_node = edge.post_node
            else:
                # print('Exiting')
                return current_node, breadcrumb_edges, action


    def choose_action(self, node, action_list, is_player_moves):
        action_choice = None
        max_ucb1 = 0

        for action in action_list:
            edge = node.get_edge_by_action(action)
            if not edge:
                # Return if the action hasn't been simmed yet
                return action

            post_node = edge.post_node

            # We want to choose based off the inverse of the score if its not the players moves
            if is_player_moves:
                score = post_node.score
            else:
                score = 1 - post_node.score

            ucb1_score = self.ucb1(score, post_node.sims)
            if ucb1_score > max_ucb1:
                action_choice = action
                max_ucb1 = ucb1_score

        return action_choice


    def is_player_turn(self, game):
        if self.player_perspective:
            player = self.source_game.current_phase.player
        else:
            player = self.source_game.current_phase.opponent

        return game.current_phase.player == player


    def expand(self, pre_node, post_node, action):
        edge = Edge(pre_node, post_node, action)
        pre_node.edges.append(edge)
        return edge


    def back_propogate(self, node, edge_path):
        edge_path.reverse()
        current_node = node
        current_node.sims += 1
        for edge in edge_path:
            current_node = edge.pre_node
            current_node.sims += 1
            current_node.score = self.calculate_score(current_node)


    def calculate_score(self, node):
        total_sims = 1
        total_score = node.state_score
        for edge in node.edges:
            sims = edge.post_node.sims
            total_sims += sims
            total_score += sims * edge.post_node.score

        return float(total_score)/total_sims


    def ucb1(self, node_score, sims):
        sim_score = (node_score * sims) + 1
        return math.sqrt((2 * np.log(sim_score))/sims)

