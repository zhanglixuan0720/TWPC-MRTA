import numpy as np

# Draw


def priority(arcs):
    n = arcs.shape[0]
    queue = []
    ts = []
    prior = np.zeros(shape=n, dtype=np.int)
    out_degrees = np.sum(arcs, axis=1)
    for i in range(0, n):
        if not out_degrees[i]:
            queue.append(i)
    while queue != []:
        node = queue.pop()
        ts.append(node)
        for i in range(0, n):
            if arcs[i][node]:
                out_degrees[i] -= 1
                prior[i] += prior[node]+1
                if not out_degrees[i]:
                    queue.append(i)
    # print("ts", ts)
    # print("prior", prior)
    return ts, prior


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
# ts, p = priority(arcs)
