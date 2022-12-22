import numpy as np
import pandas as pd


# scales node output to 0-1
def sig(p):
    return 1/(1+np.exp(p))

class NN:
    def __init__(self, lay_size=None):
        self.lay_size = lay_size  # note size 1 is input
        self.weight_lay = []
        self.tot_weight = []
        self.out_scale = 10
        self.biases = []

        if self.lay_size is None:
            self.lay_size = [20,15,18]

        self.nodes = []
        self._init_lay()

    def square_cost(self,out,ex):
        ex2 = out -ex
        return np.sum(ex2**2)

    # def total_cost(self):
    def _init_lay(self):
        li = len(self.lay_size)
        for n in range(1,li):  # posibly class layer, # todo add if remember
            weight = np.random.rand(self.lay_size[n], self.lay_size[n-1])
            print('Weit size:', weight.shape)
            self.tot_weight.append(weight)
            self.biases.append(np.random.rand(self.lay_size[n], 1))

    def run_fun(self,inp):  # note since first lay is input not weight added
        if len(inp.shape) == 1:  # todo inp out scale
            inp = inp.reshape((-1, 1))
        for n, lay in enumerate(self.tot_weight):
            print(f'-----lay{n}-----')
            out_mat = lay @ inp
            out_mat += self.biases[n]
            inp = sig(out_mat)
            print('value ', inp)
        print(f'-out, {inp*10}\n--------\n')
        return inp*10

    def error(self, out,ex):  # todo total error if multi output
        er = np.abs((out-ex)/ex)
        return er

    def train_2(self, data):
        print('train 2')
        if isinstance(data, pd.DataFrame):
            names = list(data.columns[:-1])
            out_n = data.columns[-1]
            data = data.to_numpy()
        else:
            names = range(data.shape[1]-1)
            out_n = data.shape[1]
        di = []
        for n in range(data.shape[0]):
            print('--------------\n--------------\nnew data\n----------')
            inp_d = data[n,:-1]
            out_nn = self.run_fun(inp_d)  # todo add names print in main
            ex = data[n,-1]
            # todo data if multiple output, or one out of list
            err = self.error(out_nn, ex)
            print(f'\n\ndataset: {n}, inp data')
            print(names)
            print(inp_d)
            print(f'Output, {out_n}={out_nn}, expected: {ex}, error: {err}')
            di.append((out_nn, err))  # todo total eror for all inputs
        print('\n----------\n----------')
        for ddd in di:
            print('output {}: error {}\n'.format(*ddd))  # todo loop
        total_cost = np.mean([n[1] for n in di])
        print('toal cost = ', total_cost)
        return total_cost
    # def _init_nodes(self):
    #     for n, lay in enumerate(self.lay_size):  # posibly class layer
    #         no = []
    #
    #         for i in range(lay):  # add i nodes
    #             if n == 0:  # todo remember order
    #                 no.append(Node(lay=n, n=i))  # inputs to nn
    #             else:
    #                 no.append(Node(self.nodes[n-1], lay=n,n=i))  # todo on -1
    #         self.nodes.append(np.array(no))

    def weights(self):
        print('Weight')
        for w in self.tot_weight:
            print(w)

    def gen_out(self):
        # call just last or back propegate ie for layer: lay out = [node_out for node in lay], in next, or
        # for node in last lay, out(x)-->sum(out(x-1)-->sum(out(x-3)) etc
        pass

    def train(self, data):
        di = []
        for d in data:
            di.append(self.run_norm(d))

        w = []
        for l in self.nodes:  # todo py multy, arrylike, save
            for n in l:
                w.append(n.weights)
        weight = np.sum(di)
        self.weight_lay.append({'sum': weight, 'weights':w})  # todo recursion vs strait, todo foreach datata,
        # last column

        print(self.weight_lay)
        pass

    def train_csv(self, file):
        data = pd.read_csv(file,delimiter=';')
        print(data)
        data = data.head(3)
        self.train_2(data)

    def run_norm(self,inp):
        for n, node in enumerate(self.nodes[0]):
            node.act = inp[n]  # todo on set, set weights
            node.weights = 1

        out = [n.value() for n in self.nodes[-1]]
        print('Output = ', out)  # output names
        return out


# def in_fun():
#     print('in_f')
#
#
# # gen layer
# def node_layer(si, si_0=0):
#     n = np.zeros(si)  # layer of size si, with previes layer si_0
#     for no in n:  # each node needs all previes as activations and weights
#         weights = np.zeros(si_0)
#
#
# class Node:  # remember act or just nodes
#     def __init__(self, previous_nodes=None, weights=None, lay=None, n=None):
#         self.act = previous_nodes  # todo if acts are input or other nodes
#         self.weights = weights
#         self.lay =lay
#         self.n = n
#         if self.weights is None and self.act is not None:  # todo input, output name
#             self.set_weights()
#
#     def set_weights(self):
#         self.weights = np.random.rand(*self.act.shape)
#
#     # act = previous activations
#     # weight edges = all weights for act
#     def value(self):
#         s2 = f'Layer: {self.lay}; node: {self.n}'
#         # (s2)
#         p = np.sum(self.act * self.weights)
#         si = sig(p)
#         # print(f'{s2}, value: {si}')
#         return si
#
#     def v2(self, act):
#         p = np.sum(act * self.weights)
#         return sig(p)
#
#     def __mul__(self, other):
#         return other*self.value()
#
#     def __add__(self,other):
#         return other + self.value()
#
#     def __getitem__(self, item):
#         print(f'get: {item}')
#         print(f'itemtype: {type(item)}')
#         if isinstance(item, tuple):
#             it_0 = item[1]
#             item = item[0]
#             return self.__getitem__(item)[it_0]
#
#         elif isinstance(item, str):
#             return self.__getattribute__(item)
#         return self.act[item], self.weights[item]
#
#     def __setitem__(self, key, value):
#         print(f'set, {key}: {value}')
#         print(f'Keytype: {type(key)}')
#         pass
#
#
# class NodeInput:
#     def __init__(self):
#
#         # super.__init__()
#         pass
#
#     def value(self, a2):
#         pass  # if first node use inputs


# def se
if __name__ =='__main__':
    nn = NN([11,15,15,1])
    nn.train_csv('winequality-red.csv')
    nn.weights()
