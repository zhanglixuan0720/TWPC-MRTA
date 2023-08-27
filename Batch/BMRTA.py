from Auction.pIA import *
import numpy as np
from DataGeneration.MRTAData import GetMinDis
from Batch.cluster import HierCluster
from common import AStar
from copy import deepcopy
from MIP.MIPSolve import TWPCMIP
import time
global K_BATCH

# K_BATCH = np.array([0.83063073, 0.01185164, 0.24965855, 0.01755108])
K_BATCH = np.array([0.84051778, 0.01229193, 0.26850491])


# Batch MRTA
class BMRTA:
    def __init__(self, name=""):
        self.modelname = name
        self.batchnum = 0

        self.TFinshed = {}
        self.TFailed = set()
        self.SFTime = {}
        self.TBatch = None

        self.TuA = []

        self.robotnum = 0
        self.tasknum = 0
        self.tasks = []

        self.diss = None

        self.prec = None

        self.precursors = None

        self.MaxBatchNum = None
        self.distance = 0

    def SetMap(self, filename_map):
        if type(filename_map) != type(""):
            return
        self.grid = AStar.MapRead(filename_map, 1)

    def SetData(self, data):
        d, tasks, prec = data

        self.diss = d

        self.robotnum = 0
        self.tasks = []
        for task in tasks:
            if task[-1] == 0:
                self.robotnum += 1
            else:
                self.TuA.append(task[0])
            self.tasks.append(task)

        self.tasknum = len(self.tasks) - self.robotnum
        self.prec = np.array(prec)
        self.dprec = deepcopy(self.prec)
        self.precursors = np.sum(prec, axis=0)

        self.MaxBatchNum = 3 * self.robotnum + 2  #+ 2

        for i in range(self.robotnum):
            self.TFinshed[i] = []

    def PrecCheck(self, idx, runbatchidx, waitingidx):
        parents = parent(idx, self.prec)
        for par in parents:
            if par in runbatchidx:
                parents.remove(par)
        if parents is []:
            return True
        for par in parents:
            is_ok = False
            if par in waitingidx:
                is_ok = self.PrecCheck(par, runbatchidx, waitingidx)
            if is_ok:
                parents.remove(par)
        if parents is []:
            return True
        return False

    def updatePre(self, idx):
        for i in range(self.robotnum, self.robotnum + self.tasknum):
            if self.prec[idx][i]:
                self.precursors[i] -= 1

    def GetInitTask(self):
        RTDict = {}
        InitTask = []
        is_allocate = [-1] * self.robotnum
        for r in range(self.robotnum):
            for t in self.TuA:
                RTDict[(r, t)] = min(self.tasks[t][1], self.diss[r][t])
        RTDict = sorted(RTDict.items(), key=lambda x: x[1])
        while len(InitTask) != self.robotnum:
            for key in RTDict:
                # print(key)
                r, t = key[0]
                if self.precursors[t] == 0 and is_allocate[
                        r] == -1 and t in self.TuA:
                    is_allocate[r] = t
                    InitTask.append(t)
                    self.TuA.remove(t)
                    RTDict.remove(key)
                    self.updatePre(t)
                    break
        return InitTask

    def GetTimeDis(self):
        global K_BATCH
        TDiss = np.zeros(
            (self.robotnum + self.tasknum, self.robotnum + self.tasknum))
        for i in range(self.robotnum, self.robotnum + self.tasknum):
            for j in range(i + 1, self.robotnum + self.tasknum):
                taski = self.tasks[i]
                taskj = self.tasks[j]
                x = np.array([
                    taski[1] - taskj[1],
                    taski[2] - taskj[2],
                    taski[3] - taskj[3]  #, self.diss[i][j]
                ])
                TDiss[i][j] = np.dot(x, K_BATCH)
                TDiss[j][i] = -TDiss[i][j]
        return TDiss

    def GetBatch(self):
        if self.tasknum <= self.MaxBatchNum:
            return [[
                idx
                for idx in range(self.robotnum, self.robotnum + self.tasknum)
            ]]
        TaskSeries = {}
        InitTask = self.GetInitTask()
        TaskPA = deepcopy(InitTask)
        TimeDiss = self.GetTimeDis()
        # print("debug")
        for _ in range(self.tasknum - self.robotnum):
            TTDict = {}
            for t in self.TuA:
                TTDict[t] = max([TimeDiss[j][t] for j in TaskPA])
            TTDict = sorted(TTDict.items(), key=lambda x: x[1], reverse=True)
            for key in TTDict:
                t = key[0]
                if self.precursors[t] == 0:
                    TaskPA.append(t)
                    self.TuA.remove(t)
                    self.updatePre(t)
                    TaskSeries[t] = -key[1]  #TTDict[t]
                    break
        # cluster
        divpoints = HierCluster(TaskSeries,
                                int(self.tasknum / self.MaxBatchNum),
                                self.robotnum, int(self.MaxBatchNum / 2),
                                self.MaxBatchNum)
        tseris = [key for key in TaskSeries]
        batches = []
        if divpoints != []:
            batches.append(InitTask + tseris[:divpoints[0]])
        for i in range(len(divpoints) - 1):
            batches.append(tseris[divpoints[i]:divpoints[i + 1]])
        batches.append(tseris[divpoints[-1]:])
        return batches

    def GetDis(self, batchidx):
        # batchidx = batchidx.astype(int)
        n = len(batchidx)
        d = np.zeros(shape=(n, n))
        for i in range(0, n):
            for j in range(0, n):
                d[i][j] = self.diss[batchidx[i]][batchidx[j]]
        return d

    def GetPrec(self, batchidx):
        n = len(batchidx)
        prec = np.zeros(shape=(n, n))
        for i in range(0, n):
            for j in range(0, n):
                prec[i][j] = self.prec[batchidx[i]][batchidx[j]]
        return prec

    def DelFailed(self, failedidx):
        self.TFailed.add(failedidx)
        for idx in child(failedidx, self.prec):
            self.TFailed.add(idx)
            self.DelFailed(idx)

    def update(self, sol, batchidx):
        if sol == None:
            return self.tasks[0:self.robotnum]
        R, O, S, F, _, TotalDis = sol
        robots = []
        for i in range(self.robotnum):
            nx = O[i]
            ls = i
            while nx != -1:
                idx = batchidx[nx]
                self.TFinshed[i].append(idx)
                self.SFTime[idx] = (S[nx], F[nx])
                ls = nx
                nx = O[nx]
            robots.append([batchidx[ls], int(F[ls]), 1600, 0])
        self.distance += TotalDis
        for i in range(len(R)):
            if R[i] == -1:
                self.DelFailed(batchidx[i])
        return np.array(robots)

    def FailedCheck(self, batch):
        Truebatch = []
        for t in batch:
            if t not in self.TFailed:
                Truebatch.append(t)
        return Truebatch

    def Precupdate(self, batch):
        TF = []
        for i in range(self.robotnum):
            TF += self.TFinshed[i]
        for t in batch:
            parent_t = intersection(TF, parent(t[0], self.prec))
            if parent_t != []:
                ptF = [self.SFTime[t1][1] for t1 in parent_t]
                maxFT = max(ptF)
                t[2] += min(t[1] - maxFT, 0)
                t[1] = max(maxFT, t[1])

    def Schedule(self, data):
        t0 = time.perf_counter()
        dis, est, twl, dur, prec = data
        tasks = [[i, est[i], twl[i], dur[i]] for i in range(len(dur))]
        self.SetData((dis, tasks, prec))
        # batches = self.GetBatch()
        self.TBatch = self.GetBatch()
        sol, d = None, None
        taskbatch = np.zeros((self.robotnum, 4), dtype=int)
        for batch in self.TBatch:

            print("batch " + str(self.batchnum) + " start.")
            # update system
            robots = np.array(self.update(sol, taskbatch[:, 0]))

            # batch allocate
            TrueBatch = self.FailedCheck(batch)
            newbatch = np.array(self.tasks)[TrueBatch]
            self.Precupdate(newbatch)

            taskbatch = np.concatenate([robots, newbatch],
                                       axis=0)  #np.array(robots + newbatch)

            d = self.GetDis(taskbatch[:, 0])
            prec = self.GetPrec(taskbatch[:, 0])

            print("batch", batch)

            # solve

            data = d, taskbatch[:, 1], taskbatch[:, 2], taskbatch[:, 3], prec
            twpcmip = TWPCMIP(self.modelname + "_bacth_" + str(self.batchnum))
            twpcmip.solve(len(newbatch), self.robotnum, data)
            sol = twpcmip.GetSol()

            self.batchnum += 1

        self.update(sol, taskbatch[:, 0])
        self.Dur = time.perf_counter() - t0

    def ScheduleShow(self):
        print('-' * 25)
        print("model:", self.modelname)
        print("Allocate " + str(self.tasknum) + " tasks to " +
              str(self.robotnum) + " robots | bacth number : " +
              str(self.batchnum))
        print("TFailed", self.TFailed)
        for key in self.TFinshed:
            print("Robot" + str(key) + ": ", self.TFinshed[key])

        print('-' * 25)

    def GetSol(self):
        R = np.zeros(self.robotnum + self.tasknum, dtype=int)
        O = np.zeros(self.robotnum + self.tasknum, dtype=int)
        S = np.zeros(self.robotnum + self.tasknum)
        F = np.zeros(self.robotnum + self.tasknum)
        Batch = np.zeros((self.robotnum + self.tasknum), dtype=int)

        O.fill(-1)
        R.fill(-1)
        S.fill(-1)
        F.fill(-1)
        Batch.fill(-1)

        for i in range(self.robotnum):
            R[i] = i
            S[i] = 0
            F[i] = 0
            Batch[i] = -1

        for ridx in range(self.robotnum):
            idxs = self.TFinshed[ridx]

            O[ridx] = idxs[0] if idxs != [] else -1
            for idx in idxs:
                R[idx] = ridx
                S[idx] = self.SFTime[idx][0]
                F[idx] = self.SFTime[idx][1]

            for i in range(0, len(idxs) - 1):
                O[idxs[i]] = idxs[i + 1]

        for i in range(len(self.TBatch)):
            for t in self.TBatch[i]:
                Batch[t] = i
        TotalDis = self.distance
        Makespan = max(F)
        return R, O, S, F, Batch, TotalDis, Makespan

    def write(self, filename):
        R, O, S, F, Batch, TotalDis, Makespan = self.GetSol()
        with open(filename, "w", encoding='utf-8') as f:
            f.write("# Solution for model " + self.modelname +
                    " Batch Number: " + str(self.batchnum) + "\n")
            f.write("# Finished Task: " +
                    str(self.tasknum - len(self.TFailed)) + " / " +
                    str(self.tasknum) + "\n")
            f.write("# Makespan: " + str(Makespan) + ", Total Distance: " +
                    str(TotalDis) + ", Total Time: " + '%.4f' % self.Dur +
                    "\n")
            f.write(' '.join(['#', 'R', 'O', 'S', 'F', 'Batch']) + '\n')
            for i in range(len(R)):
                f.write(' '.join([
                    str(x)
                    for x in [i, int(R[i]),
                              int(O[i]), S[i], F[i], Batch[i]]
                ]) + '\n')
