import random

from learning.simulator import Simulator


class DecisionManager():
    def __init__(self, model, scaler, graph, session, method='default', sim_count=150):
        self.simulator = Simulator(model, scaler, graph, session)
        self.sim_count = sim_count

        # Validate method
        valid_types = ['default', 'random', 'network']
        if method in valid_types:
            self.method = method
        else:
            raise AttributeError('Invalid method, must equal default, random, or network')


    def make_decision(self, game, player_perspective=True):
        if self.method == 'default':
            return self.make_default_decision(game, player_perspective)
        elif self.method == 'random':
            return self.make_random_decision(game, player_perspective)
        elif self.method == 'network':
            return self.make_network_decision(game, player_perspective)
        else:
            raise AttributeError('DecisionManager has invalid method ' + \
            str(method) + ', must equal default, random, or network')


    def make_default_decision(self, game, player_perspective):
        if player_perspective:
            return game.get_default_player_move()
        else:
            return game.get_default_opponent_move()


    def make_random_decision(self, game, player_perspective):
        actions = self.get_valid_moves_by_perspective(game, player_perspective)
        return random.choice(actions)


    def make_network_decision(self, game, player_perspective):
        if not self.simulator.model or not self.simulator.scaler:
            raise AttributeError('Cannot make network decision if model or scaler are not defined for this DecisionManager')
        
        tree = self.buildISMCTS(game, player_perspective)

        for i in range(0, self.sim_count):
            # print('Simulation ' + str(i))
            self.simulator.run_simulation(tree)

        max_score = 0
        action_choice = None

        filtered_edges = self.filter_edges(tree.root.edges, game, player_perspective)
        
        for edge in filtered_edges:
            score = edge.post_node.score
            print(edge.action.get_name())
            print(score)
            if not action_choice or score > max_score:
                action_choice = edge.action
                max_score = score

        if action_choice:
            game_actions = self.get_valid_moves_by_perspective(game, player_perspective)
            return self.simulator.get_corresponding_action(action_choice, game_actions)
        else:
            return self.make_default_decision(game, player_perspective)


    def get_valid_moves_by_perspective(self, game, player_perspective):
        if player_perspective:
            return game.get_valid_player_moves()
        else:
            return game.get_valid_opponent_moves()


    def filter_edges(self, edges, game, player_perspective):
        filtered_edges = []
        if player_perspective:
            valid_actions = game.get_valid_player_moves()
        else:
            valid_actions = game.get_valid_opponent_moves()

        for edge in edges:
            if edge.action in valid_actions:
                filtered_edges.append(edge)

        return filtered_edges


    def buildISMCTS(self, game, player_perspective):
        return self.simulator.buildISMCTS(game, player_perspective)


