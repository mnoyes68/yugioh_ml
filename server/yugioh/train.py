import cards
import player
import game
import json
import csv
import numpy as np

from sklearn import preprocessing
from sklearn.externals import joblib

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras.layers import Flatten
from keras import regularizers

from pandas.io.json import json_normalize

import pdb
import logging

def create_model_structure():
    model = Sequential()
    model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    #model.add(Dense(100, input_dim=58, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
    model.add(BatchNormalization())
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])
    model.load_weights("model.h5")
    return model


def create_scaler():
    scaler = joblib.load('training_scaler.pkl') 
    return scaler


# Code to play the game
def create_and_launch_game(model1, model2, scaler, j):
    logging.basicConfig(filename='training.log', level=logging.INFO, filemode='w')
    logging.info('Beginning Game: ' + str(j))
    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        ygogame = create_training_game(deck_json, model1, model2, scaler)
        ygogame.initialize_game()
        return ygogame

# Create Cards
def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'), c.get('img'))
        deck_list.append(card)
    deck = cards.Deck(deck_list, shuffle=False)
    return deck


def create_training_game(deck_json, model1, model2, scaler):
    yugi_deck = create_deck(deck_json)
    opp_deck = create_deck(deck_json)

    yugi = player.ComputerPlayer("Yugi", yugi_deck, model1, scaler)
    opponent = player.ComputerPlayer("Opponent", opp_deck, model2, scaler)

    ygogame = game.Game(yugi, opponent)
    return ygogame


def fill_memory(winner, loser, memory, results):
    win_mem = winner.memory
    loss_mem = loser.memory
    for i in win_mem:
        memory.append(i)
        results.append(1)
    for j in loss_mem:
        memory.append(j)
        results.append(0)


def train_network():
    epoch = 30000
    memory = []
    results = []
    yugi_win_count = 0
    opp_win_count = 0
    yugi_model = create_model_structure()
    opp_model = create_model_structure()
    scaler = create_scaler()

    '''
    ygogame = create_and_launch_game(yugi_model, opp_model, scaler)
    ygogame.play_game()
    print ygogame.p1.performance_memory
    print ygogame.p2.performance_memory
    '''
    perf_csv = open('pefromance_results.csv', 'w')
    writer = csv.writer(perf_csv)
    writer.writerow(['Game ID', 'P1 Score', 'P2 Score'])

    j = 1
    for i in range(epoch):
        yugi_game_count = 0
        opp_game_count = 0
        if len(memory) > 0:
            for x in memory:
                x['ID'] = 1
            norm = json_normalize(memory)
            mem_array = np.array(norm)
            res_array = np.array(results)
            opp_model.fit(mem_array, res_array)
            del memory[:]
            del results[:]
        while yugi_game_count < 4 and opp_game_count < 4:
            ygogame = create_and_launch_game(yugi_model, opp_model, scaler, j)
            try:
                ygogame.play_game()
            except:
                continue

            winner = ygogame.winner
            print "The winner is " + winner.name
            if winner.name == "Yugi":
                yugi_game_count += 1
                fill_memory(ygogame.p1, ygogame.p2, memory, results)
            elif winner.name == "Opponent":
                opp_game_count += 1
                fill_memory(ygogame.p2, ygogame.p1, memory, results)
            else:
                print "ERROR: No winner found"
                continue

            # Write Performance Memory
            p1_perf = ygogame.p1.performance_memory
            p2_perf = ygogame.p2.performance_memory
            p1_loss = sum(p1_perf)/float(len(p1_perf))
            p2_loss = sum(p2_perf)/float(len(p2_perf))
            writer.writerow([j, p1_loss, p2_loss])
            j += 1

        if yugi_game_count >= 4:
            yugi_win_count += 1
            print "Yugi wins match"
        elif opp_game_count >= 4:
            opp_win_count += 1
            yugi_model.set_weights(opp_model.get_weights())
            print "Opponent wins match"

    yugi_model.save_weights("model.h5", overwrite=True)
    perf_csv.close()


# main
if __name__ == "__main__":
    train_network()


