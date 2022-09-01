import numpy as np

mat = np.random.random((20, 20))


def abs_x(gx, gy):
    return np.abs(gx) + np.abs(gy)


def stroble(matrix, kern=3, func=None):
    gx = np.array([[-1,0,1],
                   [-2,0,2],
                   [-1,0,-1]])
    gy = np.rot90(gx)
    if func is None:
        func = abs_x

