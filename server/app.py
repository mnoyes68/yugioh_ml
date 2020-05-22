import json
import logging
import random

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from yugioh.game import Game
from yugioh.player import Player, HumanPlayer
from yugioh.cards import Deck, MonsterCard, load_deck_from_file

import tensorflow as tf

from learning.network_factory import initialize_multithread_newtork, create_scaler
from learning.decisionmanager import DecisionManager

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app)

# Game logic


def create_game(player_details, opp_details, username):
    global model
    global scaler
    global graph
    global thread_session

    player_name = player_details['name']
    player_deck_file = player_details['deck']
    player_portrait = player_details['portrait']

    opp_name = opp_details['name']
    opp_deck_file = opp_details['deck']
    opp_portrait = opp_details['portrait']

    player_deck = load_deck_from_file(player_deck_file)
    opp_deck = load_deck_from_file(opp_deck_file)

    # Override player name with username if provided
    if username:
        player_name = username


    cpu_dm = DecisionManager(model, scaler, graph, thread_session, method='network')

    yugi = Player(player_name, player_deck, player_portrait)
    opponent = Player(opp_name, opp_deck, opp_portrait, decisionmanager=cpu_dm)

    game = Game(yugi, opponent, graph=graph)
    game.initialize_game()
    return game


def get_player_details(name):
    global player_list
    if name == 'yugi':
        return player_list[0]
    elif name == 'kaiba':
        return player_list[1]
    elif name == 'joey':
        return player_list[2]
    elif name == 'pegasus':
        return player_list[3]
    else:
        return random.choice(player_list)


# Global variables

# Yugi, Kaiba, Joey, Pegasus
player_list = [
    {'name': 'Yugi', 'deck': 'decks/yugi.json', 'portrait': 'YugiThumbnail.png'}, 
    {'name': 'Kaiba', 'deck': 'decks/kaiba.json', 'portrait': 'Kaiba.png'}, 
    {'name': 'Joey', 'deck': 'decks/joey.json', 'portrait': 'Joey.png'}, 
    {'name': 'Pegasus', 'deck': 'decks/pegasus.json', 'portrait': 'Pegasus.png'}
]

model, graph, thread_session = initialize_multithread_newtork('learning/models/model_network_ff.h5')
scaler = create_scaler('learning/models/training_scaler.pkl')
#graph = tf.get_default_graph()

ygogame = None
p1_name = None
p2_name = None
username = None


# Routes
@app.route("/launchgame", methods=['POST'])
def launch_game():
    global ygogame
    global p1_name
    global p2_name
    global username

    p1_name = request.json['Player']
    p2_name = request.json['Opponent']
    username = request.json['Username']

    player_details = get_player_details(p1_name)
    opp_details = get_player_details(p2_name)

    ygogame = create_game(player_details, opp_details, username)

    return jsonify('Game Launched')


@app.route("/getconsole")
def getconsole():
    return jsonify(ygoconsole=ygogame.console)


@app.route("/addtoconsole", methods=['POST'])
def add_to_console():
    statement = request.json['Statement']
    ygogame.console.append(statement)
    return jsonify(ygoconsole=ygogame.console)


@app.route("/game")
def game():
    return jsonify('Game URL Hit!')


@app.route("/advancegame", methods=['POST'])
def iterate_game():
    player_move = request.json['PlayerMove']
    # Assumes the human player is P1
    if ygogame.turn == ygogame.p1:
        move = ygogame.get_move_from_action(player_move)
        ygogame.play_step(player_action=move)
    else:
        move = ygogame.get_move_from_action(player_move, opp_perspective=True)
        ygogame.play_step(opponent_action=move)
    return jsonify('Game Advanced')


@app.route("/resetgame", methods=['POST'])
def reset_game():
    global ygogame

    player_details = get_player_details(p1_name)
    opp_details = get_player_details(p2_name)

    ygogame = create_game(player_details, opp_details, username)

    return jsonify('Game Reset')


@app.route("/getgame", methods=['GET'])
def get_game():
    return jsonify(ygogame.serialize())


if __name__ == "__main__":
    app.run(debug=True)

