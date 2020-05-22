import cards
import player
import game 
import json
import csv
import os
import logging
import random

from keras.models import Sequential, load_model
from keras.layers.core import Dense
from keras.optimizers import sgd


def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'), c.get('img'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck


def run_rollout_game(deck_json):
    yugi_deck = create_deck(deck_json)
    opp_deck = create_deck(deck_json)

    yugi = player.ComputerPlayer("Yugi", yugi_deck, None, None)
    opponent = player.ComputerPlayer("Opponent", opp_deck, None, None)

    ygogame = game.Game(yugi, opponent, rollout=True)
    ygogame.play_game()
    winner = ygogame.winner
    if winner == yugi:
        victory = True
    else:
        victory = False
    return yugi.memory, victory


def execute_games(json_file, csv_file, deck_file, n):
    deck_json = json.loads(open(deck_file, "r").read())
    with open(json_file, 'w') as data_file, open(csv_file, 'w') as result_file:
        fieldnames = ['ID', 'Result']
        writer = csv.writer(result_file, delimiter=',')
        writer.writerow(fieldnames)
        data_file.write('[')
        for i in range(n):
            id_counter = i + 1
            print "Game:", id_counter
            memory, victory = run_rollout_game(deck_json)
            for state in memory:
                state['ID'] = id_counter
                if victory:
                    writer.writerow([id_counter, 1])
                else:
                    writer.writerow([id_counter, 0])
                json.dump(state, data_file, indent=4)
                data_file.write(',\n')
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.write(']')
        data_file.close()
        result_file.close()


# main
if __name__ == "__main__":
    random.seed(60)

    logging.basicConfig(filename='rollout.log', level=logging.INFO, filemode='w')
    id_counter = 1

    execute_games('small_training_data.json', 'small_training_results.csv', 'decks/yugi.json', 13000)
    execute_games('small_test.json', 'small_test.csv', 'decks/yugi.json', 3000)





