import numpy as np
from AuctionO.layer import PHeuristic
from AuctionO.Robot import Robot
import time

def child(t, arcs):
    return [i for i in range(arcs.shape[0]) if arcs[t][i]]
    # childs = []
    # for i in range(0, arcs.shape[0]):
    #     if arcs[t][i]:
    #         childs.append(i)
    # return childs


def parent(t, arcs):
    return [i for i in range(arcs.shape[0]) if arcs[i][t]]
    # parents = []
    # for i in range(0, arcs.shape[0]):
    #     if arcs[i][t]:
    #         parents.append(i)
    # return parents


def intersection(set1, set2):
    return [x for x in set1 if x in set2]


def unionset(set1, set2):
    set0 = set1.copy()
    for x in set2:
        if x not in set0:
            set0.append(x)
    return set0


def is_subset(set1, set2):
    for x in set1:
        if x not in set2:
            return False
    return True


def free(prec, idxset):
    indegrees = {key: 0 for key in idxset}
    for i in idxset:
        for j in idxset:
            if prec[i][j] > 0:
                indegrees[j] += 1
    return [key for key in indegrees if indegrees[key] == 0]


class pIA:
    def __init__(self, name=""):
        self.TS = []  # scheduled tasks
        self.TF = []  # free layer
        self.TL = []  # second layer
        self.TH = []  # hidden layer
        self.TFailed = set()
        self.layer_number = 0

        self.F = None  # the latest finish time of the scheduled tasks
        self.PC = None  # the earliest valid start time for availiable tasks
        self.robots = []
        self.tasks = []
        self.robotnum = 0
        self.tasknum = 0
        self.prec = None
        self.modelname = name

    def SetRobot(self, robotsID):
        for ronbotID in robotsID:
            self.robots.append(Robot(ronbotID))

    def SetMap(self, d):
        Robot.SetMap(d)

    def SetData(self, data):
        d, tasks, prec = data
        self.SetMap(d)
        self.robotnum = 0
        self.tasks = []
        for task in tasks:
            if task[-1] == 0:
                self.robotnum += 1
            else:
                self.tasks.append(task)
        self.tasknum = len(self.tasks)
        self.SetRobot([i for i in range(self.robotnum)])
        self.prec = np.array(prec)[self.robotnum:self.robotnum + self.tasknum,
                                   self.robotnum:self.robotnum + self.tasknum]

        self.F = np.zeros((self.tasknum))
        self.PC = np.zeros((self.tasknum))

    def ModifiedSSI(self, Tact):
        failed_tasks = []
        for t in Tact:
            bids = np.zeros(shape=(self.robotnum, 2))
            for i in range(self.robotnum):
                bids[i][0], bids[i][1] = self.robots[i].bid(
                    self.tasks[t], self.layer_number)
            minbididx = np.argmin(bids[:, 1])
            if bids[minbididx][0] == -1:
                print("Allocate task " + str(t) + " failed.")
                failed_tasks.append(t)
            else:
                self.robots[minbididx].win(int(bids[minbididx][0]),
                                           self.tasks[t])
        self.layer_number += 1
        return failed_tasks

    def UpdateF(self):
        for robot in self.robots:
            idxs = robot.GetAllocatedTask()
            _, fr = robot.GetSFTime()

            for i in range(len(idxs)):
                self.F[idxs[i] - self.robotnum] = fr[i]

    def solidtask(self, t):
        if child(t, self.prec) != []:
            for robot in self.robots:
                if t + self.robotnum in robot.GetAllocatedTask():
                    if robot.SolidTask(t + self.robotnum) == False:
                        print("Error in solid task " + str(t))
                    return True
        return False

    def UpdatePrecGraph(self, t):
        self.TS.append(t)
        self.TF.remove(t)
        for t1 in intersection(self.TL, child(t, self.prec)):
            if is_subset(parent(t1, self.prec), self.TS):
                self.TF.append(t1)
                self.TL.remove(t1)
                self.PC[t1] = np.max(
                    [self.F[t2] for t2 in parent(t1, self.prec)])
                self.tasks[t1][2] += min(0, self.tasks[t1][1] - self.PC[t1])
                self.tasks[t1][1] = max(self.tasks[t1][1], self.PC[t1])

                for t2 in intersection(self.TH, child(t1, self.prec)):
                    if is_subset(parent(t2, self.prec),
                                 unionset(self.TS, self.TF)):
                        self.TL.append(t2)
                        self.TH.remove(t2)

    def DeleteFaildTask(self, t):
        tf = [t]
        print("Task " + str(t) +
              " failed, temporal consistent can not be satisfied.")
        while tf != []:
            t0 = tf.pop()
            self.TFailed.add(t0)
            if t0 in self.TF:
                self.TF.remove(t0)
            if t0 in self.TL:
                self.TL.remove(t0)
            if t0 in self.TH:
                self.TH.remove(t0)
            childs = child(t0, self.prec)
            if len(childs):
                for t in childs:
                    print(
                        "Task " + str(t) +
                        " failed, precedence consistent can not be satisfied.")
                tf += childs

    def ScheduleShow(self):
        print('-' * 25)
        print("model:", self.modelname)
        print("Allocate " + str(self.tasknum) + " tasks to " +
              str(self.robotnum) + " robots")
        print("TS", self.TS)
        print("TF", self.TF)
        print("TL", self.TL)
        print("TH", self.TH)
        print("TFailed", self.TFailed)
        for robot in self.robots:
            print("Robot" + str(robot.RobotID) + ": ",
                  robot.GetAllocatedTask())
        print('-' * 25)

    def GetSol(self):
        R = np.zeros(self.robotnum + self.tasknum, dtype=int)
        O = np.zeros(self.robotnum + self.tasknum, dtype=int)
        S = np.zeros(self.robotnum + self.tasknum)
        F = np.zeros(self.robotnum + self.tasknum)
        O.fill(-1)
        R.fill(-1)
        S.fill(-1)
        F.fill(-1)
        TotalDis = 0
        Makespan = 0
        for i in range(self.robotnum):
            R[i] = i
            O[i] = 0
            S[i] = 0
            F[i] = 0
        for robot in self.robots:
            TotalDis += robot.GetDistance()
            Makespan = max(Makespan, robot.GetMaskSpan())
            idxs = robot.GetAllocatedTask()
            sr, fr = robot.GetSFTime()

            O[robot.RobotID] = idxs[0] if idxs != [] else -1
            for i in range(len(idxs)):
                R[idxs[i]] = robot.RobotID
                S[idxs[i]] = sr[i]
                F[idxs[i]] = fr[i]
            for i in range(0, len(idxs) - 1):
                O[idxs[i]] = idxs[i + 1]
        return R, O, S, F, TotalDis, Makespan

    def write(self, filename):
        R, O, S, F, TotalDis, Makespan = self.GetSol()
        with open(filename, "w", encoding='utf-8') as f:
            f.write("# Solution for model " + self.modelname + "\n")
            f.write("# Finished Task: " + str(len(self.TS)) + " / " +
                    str(self.tasknum) + "\n")
            f.write("# Makespan: " + str(Makespan) + ", Total Distance: " +
                    str(TotalDis) + ", Total Time: "+ '%.4f'%self.Dur +"\n")
            f.write(' '.join(['#', 'R', 'O', 'S', 'F']) + '\n')
            for i in range(self.robotnum + self.tasknum):
                f.write(' '.join(
                    [str(x) for x in [i, int(R[i]),
                                      int(O[i]), S[i], F[i]]]) + '\n')

    def Schedule(self, data):
        t0 = time.perf_counter()
        d, est, twl, dur, prec = data
        tasks = [[i, est[i], twl[i], dur[i]] for i in range(len(dur))]
        self.SetData((d, tasks, prec))
        prior = PHeuristic(self.prec, dur[self.robotnum:])
        self.TF = free(self.prec, [i for i in range(self.tasknum)])
        self.TL = free(self.prec,
                       [i for i in range(self.tasknum) if i not in self.TF])
        self.TH = [
            i for i in range(self.tasknum)
            if i not in unionset(self.TF, self.TL)
        ]
        while len(self.TS) + len(self.TFailed) < self.tasknum:
            c = np.max([prior[t] for t in self.TL] + [0])
            Tact = [t for t in self.TF if prior[t] >= c]
            failed_tasks = self.ModifiedSSI(Tact)
            self.UpdateF()
            for t in failed_tasks:
                self.DeleteFaildTask(t)
            for t in Tact:
                if t not in failed_tasks:
                    # self.solidtask(t)
                    self.UpdatePrecGraph(t)
        self.Dur = time.perf_counter() - t0
