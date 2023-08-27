import numpy as np
from queue import Queue


class graph:
    # gtype: 0 ：normal ; 1: weight
    def __init__(self, n, gtype):
        self.type = gtype
        self.vexnum = n
        self.arcnum = 0


class mgraph(graph):
    # arcs[i][j] = 1 means : there exist an arc from i to j
    def __init__(self, n, gtype, arcs=None):
        graph.__init__(self, n, gtype)
        if not arcs:
            self.arcs = np.zeros((n, n), dtype=np.int8)
        else:
            self.arcs = arcs
        for i in range(0, self.vexnum):
            for j in range(0, self.vexnum):
                if self.arcs[i][j] == 1:
                    self.arcnum += 1
    # only used when gtype is no weighted graph

    def CircuitCheck(self):
        resnum = 0
        indegrees = self.arcs.sum(axis=0)
        vexQueue = Queue(maxsize=self.vexnum)
        for vex in range(0, self.vexnum):
            if indegrees[vex] == 0:
                vexQueue.put(vex)
        while not vexQueue.empty():
            vex = vexQueue.get()
            resnum += 1
            for nextvex in range(0, self.vexnum):
                if self.arcs[vex, nextvex] == 1:
                    indegrees[nextvex] -= 1
                    if indegrees[nextvex] == 0:
                        vexQueue.put(nextvex)
        return resnum != self.vexnum


# test
# g = mgraph(3, 0)
# g.arcs = np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0]])
# print(g.CircuitCheck())
