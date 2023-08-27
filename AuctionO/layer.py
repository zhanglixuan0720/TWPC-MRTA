import numpy as np

# Draw

# ts: the priority of the node in graph, the order in vector indicate its priority
# prior: the prior value for node 0 - n


def topsort(prec):
    n = prec.shape[0]
    queue = []
    ts = []
    out_degrees = np.sum(prec, axis=1)
    for i in range(0, n):
        if not out_degrees[i]:
            queue.append(i)
    while queue != []:
        node = queue.pop()
        ts.append(node)
        for i in range(0, n):
            if prec[i][node]:
                out_degrees[i] -= 1
                if not out_degrees[i]:
                    queue.append(i)
    return ts


def PHeuristic(prec, dur, dis=None):
    n = len(dur)
    travel = 0
    if dis is not None:
        travel = 1
    else:
        dis = np.zeros(shape=(n, n))
    ts = topsort(prec)
    prior = np.zeros(n)
    for idx in ts:
        dismin = 0
        childp = np.multiply(prec[idx, :], prior)
        maxp = np.max(childp)
        maxi = np.where(childp == maxp)
        if len(maxi) > 1:
            dismin = np.max([travel*dis[idx][j]*prec[idx][j]
                             for j in range(0, n)])
        prior[idx] = dur[idx]+maxp+dismin
    return prior


# test
# arcs = np.zeros(shape=(10, 10), dtype=np.int)
# arcs[0][1] = 1
# arcs[1][2] = 1
# arcs[3][0] = 1
# arcs[1][4] = 1
# arcs[5][2] = 1
# arcs[3][6] = 1
# arcs[6][7] = 1
# arcs[4][7] = 1
# arcs[5][8] = 1
# arcs[7][8] = 1
# arcs[9][7] = 1
# dur = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# pp = PHeuristic(arcs, dur)
# print(pp)
