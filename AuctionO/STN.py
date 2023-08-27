import numpy as np


def FolydMinDis(arcs):
    n = arcs.shape[0]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                arcs[i][j] = min(arcs[i][j], arcs[i][k] + arcs[k][j])
    return arcs


class STN:
    diss = None

    def __init__(self, ID):
        self.initID = ID
        self.eventnum = 1
        self.tasknum = 0
        self.taskorder = []
        # constrain: tasks dict
        # key: task id, value: EST, LST, DUR
        self.constrain = {}
        self.makespan = 0
        self.distance = 0

    @staticmethod
    def SetDiss(d):
        STN.diss = d

    def GetDisGraph(self, temp_order=None, temp_word=None, taskid=None):
        tasknum = self.tasknum
        n = self.eventnum + 2
        if temp_order is None:
            temp_order = self.taskorder
            tasknum -= 1
            n -= 2
        elif temp_order is None or taskid is None:
            print("illegal input.")
            return

        arcs = np.zeros(shape=(n, n))
        arcs.fill(np.inf)
        for i in range(n):
            arcs[i][i] = 0
        for i in range(tasknum + 1):
            tid = temp_order[i]
            word = None
            if tid == taskid:
                word = temp_word
            else:
                word = self.constrain[tid]
            if i == 0:
                arcs[2 * i + 1][0] = -max(word[0], self.diss[self.initID][tid])
            else:
                arcs[2 * i + 1][0] = -word[0]
            arcs[0][2 * i + 1] = word[1]
            arcs[2 * i + 2][2 * i + 1] = -word[2]
            if i != tasknum:
                arcs[2 * i + 3][2 * i + 2] = -self.diss[tid][temp_order[i + 1]]
        return arcs

    def IsConsistent(self, disgraph=None):
        if disgraph is None:
            disgraph = self.GetDisGraph()
        disgraph = FolydMinDis(disgraph)
        flag = True
        for i in range(0, self.eventnum + 2):
            if disgraph[0][0] < 0:
                flag = False
                break
        return flag

    # task:
    # 0：task id, 1: EST, early start time,
    # 2: TWL, time window length,
    # 3: DUR, duration
    def InsertVerify(self, idx, task):
        temp_word = task[1], task[1] + task[2] - task[3], task[3]
        temp_order = self.taskorder.copy()
        temp_order.insert(idx, task[0])
        disgraph = self.GetDisGraph(temp_order, temp_word, task[0])
        if self.IsConsistent(disgraph) is False:
            # print("Insert task " + str(task[0]) + " before idx " + str(idx) +
            #       ": consistent can not be satisfied.")
            return -1
        return -np.min(disgraph[:, 0])

    def InsertTask(self, idx, task):
        ms = self.InsertVerify(idx, task)
        if ms == -1:
            return False
        self.eventnum += 2
        self.tasknum += 1
        self.taskorder.insert(idx, task[0])
        self.constrain[task[0]] = [
            task[1], task[1] + task[2] - task[3], task[3]
        ]
        self.makespan = ms
        # self.distance = self.CountDis()
        return True

    def CountDis(self):
        if self.taskorder == []:
            return 0
        dis = self.diss[self.initID][self.taskorder[0]]
        for i in range(self.tasknum - 1):
            dis += self.diss[self.taskorder[i]][self.taskorder[i + 1]]
        return dis

    def GetMinNetwork(self):
        return FolydMinDis(self.GetDisGraph())

    def STNShow(self):
        print('-' * 25)
        print("tasknum:", self.tasknum, "eventnum", self.eventnum)
        print("makespan:", self.makespan, "distance", self.CountDis())
        print("taskset(order):", self.taskorder)
        print("taskconstrain:")
        print("taskID\tEST\tLST\tDUR")
        for key in self.constrain:
            word = self.constrain[key]
            print(
                str(key) + "\t" + str(word[0]) + "\t" + str(word[1]) + "\t" +
                str(word[2]))
        print('-' * 25)


# from MIPData import MIPData

# robotnum = 3  # the number of robots
# tasknums = [9, 18, 27, 36]  # the number of tasks
# epoch = 10

# InitDataRoot = "Data/Init/"
# DataRoot = "Data/R3/"

# Data = MIPData(robotnum)
# Data.SetInitRT(InitDataRoot + "robot3.csv", InitDataRoot + "task60.csv")
# Data.SetMap(InitDataRoot + "map.csv")
# stn = STN(0)

# # data
# for i in range(0, 1):
#     tasknum = tasknums[i]
#     for i in range(0, 1):
#         filename = "r" + str(robotnum) + "_t" + str(tasknum) + "_" + str(i)
#         data = Data.GetDatafromFile(DataRoot + filename + ".csv")
#         d, est, twl, dur, prec = data
#         STN.SetDiss(d)
#         for i in range(3, 12):
#             mss = []
#             for j in range(stn.tasknum + 1):
#                 ms = stn.InsertVerify(j, [i, est[i], twl[i], dur[i]])
#                 mss.append(ms)
#             mxms = max(mss)
#             if mxms > 0:
#                 idx = mss.index(mxms)
#                 stn.InsertTask(idx, [i, est[i], twl[i], dur[i]])
#             stn.STNShow()
