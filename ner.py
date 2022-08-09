import numpy as np


# scales node output to 0-1
def sig(p):
    return 1/(1+np.exp(p))


def in_fun():
    print('in_f')


# gen layer
def node_layer(si, si_0=0):
    n = np.zeros(si)  # layer of size si, with previes layer si_0
    for no in n:  # each node needs all previes as activations and weights
        weights = np.zeros(si_0)

class NN:
    def __init__(self, lay_size=None):
        self.lay_size = lay_size

        if self.lay_size is None:
            self.lay_size = [20,15,18]

        self.nodes = []

    def _init_nodes(self):
        for n, lay in enumerate(self.lay_size):  # posibly class layer
            no = []

            for i in range(lay):  # add i nodes
                if n == 0:
                    no.append(Node(func=in_fun))  # inputs to nn
                else:
                    no.append(Node(self.nodes[n-1]))  # todo on -1
            self.nodes.append(no)

    def gen_out(self):
        # call just last or back propegate ie for layer: lay out = [node_out for node in lay], in next, or
        # for node in last lay, out(x)-->sum(out(x-1)-->sum(out(x-3)) etc
        pass


class Node:  # remember act or just nodes
    def __init__(self, previous_nodes, weights = None):
        self.act = previous_nodes  # todo if acts are input or other nodes
        self.weights = weights
        if self.weights is None:
            self.set_weights()

    def set_weights(self):
        self.weights = np.random.rand(*self.act.shape)

    # act = previous activations
    # weight edges = all weights for act
    def value(self):
        p = np.sum(self.act * self.weights)
        return sig(p)

    def v2(self, act):
        p = np.sum(act * self.weights)
        return sig(p)

    def __mul__(self, other):
        return other*self.value()

    def __add__(self,other):
        return other + self.value()

    def __getitem__(self, item):
        print(f'get: {item}')
        print(f'itemtype: {type(item)}')
        if isinstance(item, tuple):
            it_0 = item[1]
            item = item[0]
            return self.__getitem__(item)[it_0]

        elif isinstance(item, str):
            return self.__getattribute__(item)
        return self.act[item], self.weights[item]

    def __setitem__(self, key, value):
        print(f'set, {key}: {value}')
        print(f'Keytype: {type(key)}')
        pass


# def se
if __name__ =='__main__':
    at = np.arange(10)
    ni = Node(at)
    print('ni2')
    print(ni[2])
    print('ni[2][1]')
    print(ni[2][1])
    print('ni [2,1]')
    print(ni[2,1])
    print(ni['act', 2])