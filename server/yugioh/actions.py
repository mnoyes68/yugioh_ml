import numpy as np

import logging

class Action():
    def __init__(self, player, opponent, is_default=False):
        self.player = player
        self.opponent = opponent
        self.is_default = is_default
        self.speed = None


    def activate(self):
        raise NotImplementedError('users must define to use this base class')


    def resolve(self):
        raise NotImplementedError('users must define to use this base class')


    def get_name(self):
        return ""


    def get_canvas(self):
        shape = (2,20)
        canvas = np.zeros(shape)
        return canvas


    def get_console_description(self):
        raise NotImplementedError('users must define to use this base class')


    def serialize(self):
        raise NotImplementedError('users must define to use this base class')


    def is_serial_equal(self, action):
        raise NotImplementedError('users must define to use this base class')


class Chain():
    def __init__(self):
        self.actions = []
        self.top_speed = 1


    def add(self, action):
        if action.speed < self.top_speed:
            raise Exception("Cannot add lower speed action onto chain")

        action.activate()
        self.actions.append(action)

        if self.top_speed == 1:
            self.top_speed = 2
        if action.speed == 3:
            self.top_speed = 3


    def resolve(self):
        return_actions = []
        for i in range(0, len(self.actions)):
            action = self.actions.pop()
            return_actions.append(action)
            action.resolve()
            i += 1

        self.top_speed = 1
        return return_actions


    def __len__(self):
        return self.actions.__len__()


class Advance(Action):
    def __init__(self, player, opponent, is_default=False):
        Action.__init__(self, player, opponent, is_default)
        self.speed = 1


    def get_name(self):
        return "Advance"


    def activate(self):
        pass


    def resolve(self):
        return False


    def get_console_description(self):
        return None


    def serialize(self):
        action_json = {}
        action_json['Name'] = 'Advance'
        action_json['DisplayName'] = 'Advance'
        action_json['IsDefault'] = self.is_default
        action_json['RequiresTarget'] = False
        return action_json


    def is_serial_equal(self, action_json):
        return action_json['Name'] == 'Advance'


    def __eq__(self, other):
        return isinstance(other, Advance)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("Advance")


class EmptyDeckDrawError(Exception):
    pass


class DrawCard(Action):
    def __init__(self, player, opponent, is_default=False):
        Action.__init__(self, player, opponent, is_default)
        self.speed = 1


    def get_name(self):
        return "Draw Card"


    def activate(self):
        if not self.check_validity():
            return False
        self.player.draw_card()
        return True


    def resolve(self):
        pass


    def get_console_description(self):
        return self.player.name + ' drew a card'


    def serialize(self):
        action_json = {}
        action_json['Name'] = 'DrawCard'
        action_json['DisplayName'] = 'Draw Card'
        action_json['IsDefault'] = self.is_default
        action_json['RequiresTarget'] = False
        return action_json


    def is_serial_equal(self, action_json):
        return action_json['Name'] == 'DrawCard'


    def check_validity(self):
        if len(self.player.deck) == 0:
            raise EmptyDeckDrawError()
        return True


    def __eq__(self, other):
        if isinstance(other, DrawCard):
            return self.player == other.player and \
            self.opponent == other.opponent
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("DrawCard:" + self.player.hashed_id + ":" + self.opponent.hashed_id)


class NormalSummon(Action):
    def __init__(self, player, opponent, monster, is_default=False):
        Action.__init__(self, player, opponent, is_default)
        self.monster = monster
        self.speed = 1


    def get_name(self):
        return "Normal Summon " + self.monster.name


    def get_console_description(self):
        return self.player.name + ' summoned ' + self.monster.name


    def serialize(self):
        action_json = {}
        action_json['Name'] = 'NormalSummon'
        action_json['DisplayName'] = 'Normal Summon'
        action_json['Monster'] = self.monster.serialize()
        action_json['IsDefault'] = self.is_default
        action_json['RequiresTarget'] = False
        return action_json


    def is_serial_equal(self, action_json):
        if action_json['Name'] == 'NormalSummon':
            return action_json['Monster']['CardID'] == self.monster.card_id
        return False


    def check_validity(self):
        if self.monster not in self.player.hand.cards:
            return False
        if self.player.board.get_occupied_monster_spaces() >= 5:
            return False
        return True


    def activate(self):
        if not self.check_validity():
            return False
        card = self.monster
        self.player.hand.cards.remove(self.monster)
        for space in self.player.board.monster_spaces:
            if not space.occupied:
                space.add_card(card)
                break

        logging.debug("Summoning " + card.name)
        return True


    def resolve(self):
        pass


    def __eq__(self, other):
        if isinstance(other, NormalSummon):
            return self.player == other.player and \
            self.opponent == other.opponent and \
            self.monster == other.monster

        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("NormalSummon:" + self.player.hashed_id + ":" + self.opponent.hashed_id + ":" + self.monster.hashed_id)


class Attack(Action):
    def __init__(self, player, opponent, monster, target, is_default=False):
        Action.__init__(self, player, opponent, is_default)
        self.monster = monster
        self.target = target
        self.speed = 1


    def get_name(self):
        return "Attack {0} ({1}) with {2} ({3})".format(self.target.name, self.target.atk, self.monster.name, self.monster.atk)


    def get_console_description(self):
        return "{0} attacked {1} with {2}".format(self.player.name, self.target.name, self.monster.name)


    def serialize(self):
        action_json = {}
        action_json['Name'] = 'Attack'
        action_json['DisplayName'] = 'Attack'
        action_json['Monster'] = self.monster.serialize()
        action_json['Target'] = self.target.serialize()
        action_json['IsDefault'] = self.is_default
        action_json['RequiresTarget'] = True
        return action_json


    def is_serial_equal(self, action_json):
        if action_json['Name'] == 'Attack':
            return action_json['Monster']['CardID'] == self.monster.card_id and action_json['Target']['CardID'] == self.target.card_id
        return False


    def check_validity(self):
        if self.monster not in self.player.board.get_monsters():
            return False
        if self.target not in self.opponent.board.get_monsters():
            return False
        return True


    def activate(self):
        if not self.check_validity():
            return False
        message = "Attacking " + self.target.name + " with " + self.monster.name
        logging.debug(message)

        self.process_attack()
        self.monster.attacked_this_turn = True
        return True


    def resolve(self):
        pass


    def process_attack(self):
        if self.monster.atk > self.target.atk:
            diff = self.monster.atk - self.target.atk
            self.opponent.board.destroy_monster(self.target)
            self.opponent.decrease_life_points(diff)
        elif self.monster.atk < self.target.atk:
            diff = self.target.atk - self.monster.atk
            self.player.board.destroy_monster(self.monster)
            self.player.decrease_life_points(diff)
        elif self.monster.atk == self.target.atk:
            self.opponent.board.destroy_monster(self.target)
            self.player.board.destroy_monster(self.monster)


    def __eq__(self, other):
        if isinstance(other, Attack):
            return self.monster == other.monster and \
            self.target == other.target and \
            self.player == other.player and \
            self.opponent == other.opponent
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("Attack:" + self.player.hashed_id + ":" + self.opponent.hashed_id + ":" + self.monster.hashed_id + ":" + self.target.hashed_id)


class DirectAttack(Action):
    def __init__(self, player, opponent, monster, is_default=False):
        Action.__init__(self, player, opponent, is_default)
        self.monster = monster
        self.speed = 1


    def get_name(self):
        return "Attack {0} directly with {1} ({2})".format(self.opponent.name, self.monster.name, self.monster.atk)


    def check_validity(self):
        if self.opponent.board.get_occupied_monster_spaces() > 0:
            return False
        if self.player.board.get_occupied_monster_spaces() <= 0:
            return False
        return True


    def get_console_description(self):
        return "{0} attacked directly with {1}".format(self.player.name, self.monster.name)


    def serialize(self):
        action_json = {}
        action_json['Name'] = 'DirectAttack'
        action_json['DisplayName'] = 'Direct Attack'
        action_json['Monster'] = self.monster.serialize()
        action_json['IsDefault'] = self.is_default
        action_json['RequiresTarget'] = False
        return action_json


    def is_serial_equal(self, action_json):
        if action_json['Name'] == 'DirectAttack':
            return action_json['Monster']['CardID'] == self.monster.card_id
        return False


    def activate(self):
        if not self.check_validity():
            return False
        message = "Attacking " + self.opponent.name + " directly with " + self.monster.name
        logging.debug(message)
        
        self.opponent.decrease_life_points(self.monster.atk)
        self.monster.attacked_this_turn = True
        return True


    def resolve(self):
        pass


    def __eq__(self, other):
        if isinstance(other, DirectAttack):
            return self.monster == other.monster and \
            self.player == other.player and \
            self.opponent == other.opponent
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("DirectAttack:" + self.player.hashed_id + ":" + self.opponent.hashed_id + ":" + self.monster.hashed_id)


# Grouping Utility, pass in a list of serialized actions
def group_actions_by_name(action_list):
    action_group = {}
    for action in action_list:
        name = action['Name']
        if name in action_group:
            action_group[name].append(action)
        else:
            action_group[name] = [action]
    return action_group


