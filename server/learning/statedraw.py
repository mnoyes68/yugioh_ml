import json


# Utility class for writing the machine learning game state

def write_game_state(player, opponent):
    game_state = {}

    # Player Info
    game_state['PlayerLP'] = player.life_points
    game_state['PlayerHandSize'] = len(player.hand.cards)
    game_state['PlayerMonstersOnBoard'] = player.board.get_occupied_monster_spaces()
    game_state['PlayerDeckSize'] = len(player.deck.cards)
    game_state['OppLP'] = opponent.life_points
    game_state['OppHandSize'] = len(opponent.hand.cards)
    game_state['OppMonstersOnBoard'] = opponent.board.get_occupied_monster_spaces()
    game_state['OppDeckSize'] = len(opponent.deck.cards)

    game_state['ID'] = 1 # TODO Replace with game state counter
    
    # Player Board Info
    player_monsters = player.board.get_monsters()
    for i in range(0, 5):
        prefix = "PlayerMonster" + str(i+1)
        if i < len(player_monsters):
            monster = player_monsters[i]
            monster_state = write_monster_card(monster)
            game_state[prefix] = monster_state
        else:
            monster_state = write_monster_card(None)
            game_state[prefix] = monster_state

    # Opponent Board Info
    opp_monsters = opponent.board.get_monsters()
    for i in range(0, 5):
        prefix = "OpponentMonster" + str(i+1)
        if i < len(opp_monsters):
            monster = opp_monsters[i]
            monster_state = write_monster_card(monster)
            game_state[prefix] = monster_state
        else:
            monster_state = write_monster_card(None)
            game_state[prefix] = monster_state

    return game_state


def write_monster_card(monster):
    card_state = {}
    if monster != None:
        card_state['Exists'] = 1
        card_state['Attack'] = monster.atk
        card_state['Defense'] = monster.defn
        card_state['Level'] = monster.level
        if(monster.attacked_this_turn):
            card_state['AttackedThisTurn'] = 1
        else:
            card_state['AttackedThisTurn'] = 0
        return card_state
    else:
        card_state['Exists'] = 0
        card_state['Attack'] = 0
        card_state['Defense'] = 0
        card_state['Level'] = 0
        card_state['AttackedThisTurn'] = 0
        return card_state


'''
def write_game_state(game, opp_perspective=False):
    game_state = {}

    if opp_perspective:
        player = game.get_opponent()
        opponent = game.turn
    else:
        player = game.turn
        opponent = game.get_opponent()

    # game_state['TurnNumber'] = self.turn_number
    # game_state['Phase'] = self.current_phase.name
    # game_state['StateOpen'] = 1 if self.current_phase.state_open else 0

    # Player Info
    game_state['PlayerLP'] = player.life_points
    game_state['PlayerHandSize'] = len(player.hand.cards)
    game_state['PlayerMonstersOnBoard'] = player.board.get_occupied_monster_spaces()
    game_state['PlayerDeckSize'] = len(player.deck.cards)
    game_state['OppLP'] = opponent.life_points
    game_state['OppHandSize'] = len(opponent.hand.cards)
    game_state['OppMonstersOnBoard'] = opponent.board.get_occupied_monster_spaces()
    game_state['OppDeckSize'] = len(opponent.deck.cards)
    
    game_state = write_board(game_state, player, "Player")
    game_state = write_board(game_state, opponent, "Opponent")

    game_state['ID'] = 1 # TODO have each step iterate the step count

    return game_state


def write_board(game_state, player, prefix):
    # Get monsters and sort by attack
    monsters = player.board.get_monsters()
    monsters = sorted(monsters, key = lambda m: m.atk, reverse=True)

    # Write States
    for i in range(0, 5):
        field = prefix + "Monster" + str(i+1)
        if i < len(monsters):
            monster = monsters[i]
        else:
            monster = None
            
        monster_state = write_monster_card(monster)
        game_state[prefix] = monster_state

    return game_state


def write_monster_card(monster):
    card_state = {}
    if monster != None:
        card_state['Exists'] = 1
        card_state['Attack'] = monster.atk
        card_state['Defense'] = monster.defn
        card_state['Level'] = monster.level
        if(monster.attacked_this_turn):
            card_state['AttackedThisTurn'] = 1
        else:
            card_state['AttackedThisTurn'] = 0
        return card_state
    else:
        card_state['Exists'] = 0
        card_state['Attack'] = 0
        card_state['Defense'] = 0
        card_state['Level'] = 0
        card_state['AttackedThisTurn'] = 0
        return card_state
'''

