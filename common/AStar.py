import csv
import numpy as np
# 1e-5 indicates the cost of  bevel direction is larger than 0°
global BEVEL_COST
BEVEL_COST = 2


def CoordtoIndex(coord, width):
    return coord[0] * width + coord[1]


def IndextoCoord(index, width):
    return int(index / width), index % width


def ArgMin(array):
    if len(array) == 0:
        return -1
    idx = 0
    for i in range(1, len(array)):
        if array[i] < array[idx]:
            idx = i
    return idx


def GetNeighbor(idx, height, width):
    neighbor = []
    i, j = IndextoCoord(idx, width)
    if i - 1 > 0:
        neighbor.append(CoordtoIndex((i - 1, j), width))
    if i + 1 < height:
        neighbor.append(CoordtoIndex((i + 1, j), width))
    if j - 1 > 0:
        neighbor.append(CoordtoIndex((i, j - 1), width))
    if j + 1 < width:
        neighbor.append(CoordtoIndex((i, j + 1), width))
    return neighbor


def Get8Neighbor(idx, height, width):
    neighbor1 = []
    neighbor1_5 = []
    i, j = IndextoCoord(idx, width)
    if i - 1 > 0:
        neighbor1.append(CoordtoIndex((i - 1, j), width))
        if j - 1 > 0:
            neighbor1_5.append(CoordtoIndex((i - 1, j - 1), width))
        if j + 1 < width:
            neighbor1_5.append(CoordtoIndex((i - 1, j + 1), width))
    if i + 1 < height:
        neighbor1.append(CoordtoIndex((i + 1, j), width))
        if j - 1 > 0:
            neighbor1_5.append(CoordtoIndex((i + 1, j - 1), width))
        if j + 1 < width:
            neighbor1_5.append(CoordtoIndex((i + 1, j + 1), width))
    if j - 1 > 0:
        neighbor1.append(CoordtoIndex((i, j - 1), width))
    if j + 1 < width:
        neighbor1.append(CoordtoIndex((i, j + 1), width))

    return neighbor1, neighbor1_5


# Manhattan Distance Heuristic
def GetMHeuristic(grid, dst):
    h = np.zeros(grid.shape)
    for i in range(0, grid.shape[0]):
        for j in range(0, grid.shape[1]):
            h[i][j] = abs(i - dst[0]) + abs(j - dst[1])
    return np.reshape(h, grid.shape[0] * grid.shape[1])


# Euler Distance Heuristic
def GetEHeuristic(grid, dst):
    h = np.zeros(grid.shape)
    for i in range(0, grid.shape[0]):
        for j in range(0, grid.shape[1]):
            h[i][j] = np.linalg.norm((i - dst[0], j - dst[1]))
    return np.reshape(h, grid.shape[0] * grid.shape[1])


# 45° Distance Heuristic
def Get45DHeuristic(grid, dst):
    h = np.zeros(grid.shape)
    for i in range(0, grid.shape[0]):
        for j in range(0, grid.shape[1]):
            x, y = abs(i - dst[0]), abs(j - dst[1])
            h[i][j] = abs(x - y) + min(x, y) * BEVEL_COST
    return np.reshape(h, grid.shape[0] * grid.shape[1])


# The number in grid indicates the status:
# 0: open area
# 1: block area
# 2: unreachable area
# 3: closed area


def ASatr(grid, init, dst, outpath):
    global BEVEL_COST
    height, width = grid.shape
    length = height * width
    # h = GetEHeuristic(grid, dst)
    h = Get45DHeuristic(grid, dst)
    grid = np.reshape(grid, length)
    parents = np.zeros(length, dtype=np.int)
    g = np.zeros(length)
    gt = np.zeros(length)
    init1 = CoordtoIndex(init, width)
    dst1 = CoordtoIndex(dst, width)
    openlist = [init1]
    IsFound = False
    while openlist != []:
        current = openlist[ArgMin([g[i] + h[i] for i in openlist])]
        if current == dst1:
            IsFound = True
            break
        grid[current] = 3
        # neighbor = GetNeighbor(current, height, width)
        neighbor1, neighbor1_5 = Get8Neighbor(current, height, width)
        while neighbor1 != []:
            idx = neighbor1.pop(0)
            if grid[idx] > 0:
                continue
            if idx not in openlist:
                openlist.append(idx)
                g[idx] = g[current] + 1
                gt[idx] = gt[current] + 1
                parents[idx] = current
            elif g[current] + 1 < g[idx]:
                g[idx] = g[current] + 1
                gt[idx] = gt[current] + 1
                parents[idx] = current
        while neighbor1_5 != []:
            idx = neighbor1_5.pop(0)
            if grid[idx] > 0:
                continue
            if idx not in openlist:
                openlist.append(idx)
                g[idx] = g[current] + BEVEL_COST
                gt[idx] = gt[current] + 1
                parents[idx] = current
            elif g[current] + BEVEL_COST < g[idx]:
                g[idx] = g[current] + BEVEL_COST
                gt[idx] = gt[current] + 1
                parents[idx] = current
        openlist.remove(current)
    if IsFound is False:
        print("Warning: No feasible path found.")
        if outpath is True:
            return -1, None
        else:
            return -1
    if outpath is True:
        path = []
        current = dst1
        while current != init1:
            path.append(current)
            current = parents[current]
        path.append(init1)
        path = [
            IndextoCoord(path[i], width) for i in range(len(path) - 1, -1, -1)
        ]
        return int(gt[dst1]), path
    else:
        return int(gt[dst1])


def MapRead(filename, RTSize):
    img = np.zeros((100, 100))
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        grid = list(reader)
        for i in range(0, 20):
            for j in range(0, 20):
                if grid[i][j] == '1':
                    xlow = 5 * i - RTSize if 5 * i - RTSize >= 0 else 5 * i
                    xhigh = 5*(i+1)+RTSize if 5*(i+1) + \
                        RTSize <= 100 else 5*(i+1)
                    ylow = 5 * j - RTSize if 5 * j - RTSize >= 0 else 5 * j
                    yhigh = 5*(j+1)+RTSize if 5*(j+1) + \
                        RTSize <= 100 else 5*(j+1)
                    img[xlow:xhigh, ylow:yhigh].fill(1)
    return img