import json
import random
import pytest

from yugioh.cards import load_deck_from_file
from yugioh.player import Player
from yugioh.game import Game
import yugioh.actions as actions

from learning.network_factory import initialize_network, create_scaler


random.seed(50)


def setup_game():
    yugi_deck = load_deck_from_file("decks/yugi.json")
    opp_deck = load_deck_from_file("decks/yugi.json")

    model1 = initialize_network('learning/models/model_network_ff.h5')
    model2 = initialize_network('learning/models/model_network_ff.h5')

    scaler1 = create_scaler('learning/models/training_scaler.pkl')
    scaler2 = create_scaler('learning/models/training_scaler.pkl')

    yugi = Player("Yugi", yugi_deck, None, model1, scaler1, decision_method='network', sim_count=150)
    opponent = Player("Opponent", opp_deck, None, model2, scaler2, decision_method='network', sim_count=150)

    ygogame = Game(yugi, opponent)

    ygogame.initialize_game()
    return ygogame


if __name__ == '__main__':
    ygogame = setup_game()
    ygogame.play_game()
