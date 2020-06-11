from yugioh.game import Game
from yugioh.player import Player
from yugioh.cards import load_deck_from_file

from learning.network_factory import initialize_network_structure
from learning.decisionmanager import DecisionManager

import numpy as np
import pickle

from pandas.io.json import json_normalize
from sklearn import preprocessing


def create_game(p1_name, p1_deck_file, p2_name, p2_deck_file):
    p1_deck = load_deck_from_file(p1_deck_file)
    p2_deck = load_deck_from_file(p2_deck_file)

    dm1 = DecisionManager(None, None, None, None, method='random')
    dm2 = DecisionManager(None, None, None, None, method='random')

    p1 = Player(p1_name, p1_deck, None, decisionmanager=dm1)
    p2 = Player(p2_name, p2_deck, None, decisionmanager=dm2)

    game = Game(p1, p2)
    game.initialize_game()
    return game


def fill_memory(player, score, memory, results):
    for state in player.memory:
        memory.append(state)
        results.append(score)


def train_network(memory, results):
    model = initialize_network_structure()
    scaler = preprocessing.MinMaxScaler()

    df = json_normalize(memory)
    res_array = np.array(results)

    X = scaler.fit_transform(df)
    model.fit(X, res_array)

    return model, scaler


def rollout_train():
    epoch = 250
    memory = []
    results = []

    for i in range(epoch):
        print('Game: ', i + 1)
        p1_name = 'Yugi'
        p2_name = 'Opponent'
        p1_deck_file = 'decks/yugi.json'
        p2_deck_file = 'decks/yugi.json'

        # Create and play the game
        game = create_game(p1_name, p1_deck_file, p2_name, p2_deck_file)
        game.play_game()

        # Record the results
        if game.ended_in_draw:
            fill_memory(game.p1, 0.5, memory, results)
            fill_memory(game.p2, 0.5, memory, results)
        elif game.winner.name == p1_name:
            fill_memory(game.p1, 1, memory, results)
            fill_memory(game.p2, 0, memory, results)
        elif game.winner.name == p2_name:
            fill_memory(game.p1, 0, memory, results)
            fill_memory(game.p2, 1, memory, results)
        else:
            raise ValueError('Game winner name not recognized, and game has not ended in a draw')

    # Train and save the results
    model, scaler = train_network(memory, results)
    pickle.dump(scaler, open('learning/models/rollout_train_25.pkl', 'wb'))
    model.save_weights('learning/models/rollout_train_25.h5', overwrite=True)


if __name__ == "__main__":
    rollout_train()

