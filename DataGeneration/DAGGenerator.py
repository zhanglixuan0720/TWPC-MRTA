from DataGeneration.graph import mgraph
from random import uniform
from copy import deepcopy


def uniformint(low, high):
    value = int(uniform(low, high))
    while value == high:
        value = uniform(low, high)
    return value


def GetCoord(low, high):
    while True:
        i, j = uniformint(low, high), uniformint(low, high)
        if i != j:
            break
    return i, j


class Markov:
    def __init__(self, X0):
        self.X0 = deepcopy(X0)
        self.Xt = deepcopy(self.X0)
        self.Xt1 = deepcopy(self.Xt)
        self.n = X0.vexnum

    def upate(self):
        while True:
            i, j = GetCoord(0, self.n)
            if self.Xt.arcs[i][j] != 0:
                self.Xt1.arcs[i][j] = 0
                self.Xt1.arcnum -= 1
                break
            else:
                self.Xt1.arcs[i][j] = 1
                self.Xt1.arcnum += 1
                if not self.Xt1.CircuitCheck():
                    break
                self.Xt1.arcs[i][j] = 0
                self.Xt1.arcnum -= 1
        self.Xt = deepcopy(self.Xt1)

    # ac : arc aconstrain

    def acupdate(self, k):
        arcupper = int(k * self.n) - 1
        while True:
            i, j = GetCoord(0, self.n)
            if self.Xt.arcs[i][j] != 0:
                self.Xt1.arcs[i][j] = 0
                self.Xt1.arcnum -= 1
                break
            else:
                if self.Xt1.arcnum > arcupper:
                    continue
                self.Xt1.arcs[i][j] = 1
                self.Xt1.arcnum += 1
                if not self.Xt1.CircuitCheck():
                    break
                self.Xt1.arcs[i][j] = 0
                self.Xt1.arcnum -= 1
        self.Xt = deepcopy(self.Xt1)


class DAGGenerator:
    def __init__(self, G0):
        self.M = Markov(G0)

    def GetDAG(self, costrain=None):
        if costrain == None:
            self.M.upate()
        else:
            self.M.acupdate(costrain)
        return self.M.Xt
