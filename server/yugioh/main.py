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

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Flatten
from keras import regularizers

from sklearn.externals import joblib

def initialize_network(weights):
    model = Sequential()
    
    # Feed Forward
    model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
    model.load_weights(weights)
    
    return model

# Code to play the game

# Create Cards
def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'), c.get('img'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck


def create_scaler():
    scaler = joblib.load('training_scaler.pkl') 
    return scaler


def run_game(deck_json_file, model, scaler):
    with open(deck_json_file, "r") as deck:
        deck_json = json.loads(deck.read())

    yugi_deck = create_deck(deck_json)
    opp_deck = create_deck(deck_json)

    yugi = player.ComputerPlayer("Yugi", yugi_deck, model, scaler)
    opponent = player.ComputerPlayer("Opponent", yugi_deck, model, scaler)

    ygogame = game.Game(yugi, opponent)
    ygogame.play_game()
    winner = ygogame.winner
    "The winner is " + winner.name
    if winner == yugi:
        victory = True
    else:
        victory = False
    return yugi.memory, victory


# main
if __name__ == "__main__":
    logging.basicConfig(filename='yugioh_game.log', level=logging.INFO, filemode='w')

    model = initialize_network('model_network_ff.h5')
    scaler = create_scaler()
    run_game('decks/yugi.json', model, scaler)

    '''
    random.seed(60)

    logging.basicConfig(filename='yugioh_game.log', level=logging.INFO, filemode='w')
    id_counter = 1

    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())

    with open('conv_training_data.json', 'w') as data_file, open('conv_training_results.csv', 'w') as result_file:
        fieldnames = ['ID', 'Result']
        writer = csv.writer(result_file, delimiter=',')
        writer.writerow(fieldnames)
        data_file.write('[')
        #while id_counter < 3250000:
        for i in range(1):
            print "Game:", i + 1
            memory, victory = run_training_game(deck_json)
            for state in memory:
                state['ID'] = id_counter
                if victory:
                    writer.writerow([id_counter, 1])
                else:
                    writer.writerow([id_counter, 0])
                json.dump(state, data_file, indent=4)
                data_file.write(',\n')
                id_counter += 1
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.write(']')
        data_file.close()
        result_file.close()
    '''







