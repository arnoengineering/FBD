import numpy as np
Kb = np.array([[1, 0],
               [1.24, 0.107],
               [1.51, 0.157],
               [0.6, 0],
               ])

Kr = np.array([
    [50, 5],
    [10, 1],
    [5, 0.62],
    [4, 0.53],
    [3, 0.44],
    [2, 0.33]])

aa = np.array([[413, 0.77],  # todo order
               [620, 0.83],
               [827, 0.86],
               [1378, 0.82]])

ab = np.array([[1.34, -0.085],
               [2.7, -0.265],
               [14.4, -0.718],
               [39.9, -0.995]])

kb_r = np.array([2.97, 51, 254])
kdt = np.poly1d((- 0.595e-12, 0.104e-8, -0.115e-5, 0.432e-3,0.975)) # [x^: 0, 1 2...]

def val_t(table, val, less=True):
    if less:
        ind = np.argmax(table > val)
    else:
        ind = np.argmax(table.flipud() < val)
    return table[ind,1:]
