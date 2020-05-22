import numpy as np

'''
shape = (2,20)
canvas = np.zeros(shape)
canvas[0, 0] = 1
canvas[0, 1] = 3
canvas[0, 2] = 1200
canvas[0, 3] = 1000
canvas[1, 0] = 1
canvas[1, 1] = 4
canvas[1, 2] = 1700
canvas[1, 3] = 1300
'''

def draw_state(state):
    im_size = (10,)*2
    print "im_size " + str(im_size)
    state = state[0]
    print "state " + str(state)
    canvas = np.zeros(im_size)
    print "canvas " + str(canvas)
    canvas[state[0], state[1]] = 1  # draw fruit
    print "canvas " + str(canvas)
    canvas[-1, state[2]-1:state[2] + 2] = 1  # draw basket
    print "canvas " + str(canvas)
    return canvas

n = np.random.randint(0, 10-1, size=1)
m = np.random.randint(1, 10-2, size=1)
state = np.asarray([0, n, m])[np.newaxis]

canvas = draw_state(state)
print canvas.reshape((1, -1))

'''
print n
print m
print state
'''
