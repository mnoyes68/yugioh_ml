import cards
import player
import numpy as np


class MatrixGenerator():
    def __init__(self, player):
        self.player = player
        self.canvas = self.get_canvas()

    def get_canvas(self):
        shape = (2,20)
        canvas = np.zeros(shape)
        return canvas

    def draw_state(self):
        canvas = self.get_canvas()
        return canvas

    def draw_board(self):
        for mnstr in self.player.board.get_monsters():
            i, j = 0, 0
            self.canvas[i, j] = 1
            j += 1
            self.canvas[i, j] = mnstr.level
            j += 1
            self.canvas[i, j] = mnstr.atk
            j += 1
            self.canvas[i, j] = mnstr.defn
            j += 1

