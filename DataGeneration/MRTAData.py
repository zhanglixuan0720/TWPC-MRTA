import sys

sys.path.append("./")
from DataGeneration.DAGGenerator import DAGGenerator
from DataGeneration.graph import mgraph
from DataGeneration.DataGenerator import DataGenerator
from common import AStar
import numpy as np
import csv

# def uniformint(low, high):
#     value = int(uniform(low, high))
#     while value == high:
#         value = uniform(low, high)
#     return value


def GetEDis(coord1, coord2):
    return np.linalg.norm((coord1[0] - coord2[0], coord1[1] - coord2[1]))


def GetMDis(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])


def GetMinDis(grid, coord1, coord2):
    coord1 = coord1[1], coord1[0]
    coord2 = coord2[1], coord2[0]
    dis = AStar.ASatr(grid, coord1, coord2, False)
    if dis == -1:
        return 1000
    return dis


def DataWrite(filename, data):
    csvFile = open(filename, "w", encoding='utf-8', newline='')
    writer = csv.writer(csvFile)
    writer.writerow(["XCOORD.", "YCOORD.", "EST", "TWL", "DUR"])
    for chip in data:
        writer.writerows(chip)
    csvFile.close()
    print("write file " + filename + "  sucessfyully.")


class MRTAData:
    def __init__(self, robotnum=2, tasknum=10):
        self.robotnum = robotnum
        self.tasknum = tasknum
        self.DataG = DataGenerator()
        # self.DataG.SetInitRT("robot.csv", "task.csv")
        G0 = mgraph(self.tasknum, 0)
        self.DAGG = DAGGenerator(G0)
        # self.grid = AStar.MapRead("map.csv", 1)

    def SetInitRT(self, filename_robots, filename_tasks):
        if type(filename_robots) != type("") or type(filename_tasks) != type(
                ""):
            return
        self.DataG.SetInitRT(filename_robots, filename_tasks)

    def SetMap(self, filename_map):
        if type(filename_map) != type(""):
            return
        self.grid = AStar.MapRead(filename_map, 1)

    def ResetTaskNum(self, tasknum):
        self.tasknum = tasknum
        G0 = mgraph(self.tasknum, 0)
        self.DAGG = DAGGenerator(G0)

    def GetDiss(self, tasks, n):
        d = np.zeros(shape=(n, n))
        for i in range(0, n):
            for j in range(i + 1, n):
                d[i][j] = GetMinDis(self.grid.copy(), tasks[i][0:2],
                                    tasks[j][0:2])
                #d[i][j] = GetMDis(tasks[i][0:2], tasks[j][0:2])
        for i in range(0, n):
            for j in range(0, i):
                d[i][j] = d[j][i]
        return d

    def GetNPData(self, logfilename):
        robots, tasks = self.DataG.GetData(self.tasknum, self.robotnum)

        tasks_dummy = []
        for pos in robots:
            tasks_dummy.append([pos[0], pos[1], 0, 16000, 0])
        tasks = np.array(tasks_dummy + tasks)

        d = self.GetDiss(tasks, self.tasknum + self.robotnum)

        prec = np.zeros(shape=(self.tasknum + self.robotnum,
                               self.tasknum + self.robotnum),
                        dtype=int)
        # store the data
        DataWrite(logfilename + ".csv", [tasks, prec, d])
        return True

    def GetData(self, outlog=0, logfilename=None):
        robots, tasks = self.DataG.GetData(self.tasknum, self.robotnum)

        self.DAGG.GetDAG()  # pass
        DAG = self.DAGG.GetDAG()
        tasks_dummy = []
        for pos in robots:
            tasks_dummy.append([pos[0], pos[1], 0, 16000, 0])
        tasks = np.array(tasks_dummy + tasks)

        # calculate return value
        d = self.GetDiss(tasks, self.tasknum + self.robotnum)
        prec = np.zeros(shape=(self.tasknum + self.robotnum,
                               self.tasknum + self.robotnum),
                        dtype=int)
        prec[self.robotnum:self.tasknum + self.robotnum,
             self.robotnum:self.tasknum + self.robotnum] = DAG.arcs
        # store the data
        if outlog:
            if logfilename is None:
                DataWrite("Data_example.csv", [tasks, prec, d])
            else:
                DataWrite(logfilename, [tasks, prec, d])
        return d, tasks[:, 2], tasks[:, 3], tasks[:, 4], prec

    def GetDataM(self, outlog=0, logfilename=None):
        robots, tasks = self.DataG.GetDataM(self.tasknum, self.robotnum)

        self.DAGG.GetDAG()  # pass1
        self.DAGG.GetDAG()  # pass2
        self.DAGG.GetDAG()  # pass3
        self.DAGG.GetDAG()  # pass4
        self.DAGG.GetDAG()  # pass5
        DAG = self.DAGG.GetDAG()
        tasks_dummy = []
        for pos in robots:
            tasks_dummy.append([pos[0], pos[1], 0, 16000, 0])
        tasks = np.array(tasks_dummy + tasks)

        # calculate return value
        d = self.GetDiss(tasks, self.tasknum + self.robotnum)
        prec = np.zeros(shape=(self.tasknum + self.robotnum,
                               self.tasknum + self.robotnum),
                        dtype=int)
        prec[self.robotnum:self.tasknum + self.robotnum,
             self.robotnum:self.tasknum + self.robotnum] = DAG.arcs
        # store the data
        if outlog:
            if logfilename is None:
                DataWrite("Data_example.csv", [tasks, prec, d])
            else:
                DataWrite(logfilename, [tasks, prec, d])
        return d, tasks[:, 2], tasks[:, 3], tasks[:, 4], prec

    # Import data to file directly
    # for every epoch, the distribution of the task is ensured,
    # for every data in epoch, the number of arcs is increased.
    def GetMultiDAGData(self, logfilename, epoch, is_cluster=False):
        robots, tasks = None, None
        if is_cluster:
            robots, tasks = self.DataG.GetDataC(self.tasknum, self.robotnum)
        else:
            robots, tasks = self.DataG.GetData(self.tasknum, self.robotnum)
        tasks_dummy = []
        for pos in robots:
            tasks_dummy.append([pos[0], pos[1], 0, 16000, 0])
        tasks = np.array(tasks_dummy + tasks)

        # calculate return value
        d = self.GetDiss(tasks, self.tasknum + self.robotnum)
        prec = np.zeros(shape=(self.tasknum + self.robotnum,
                               self.tasknum + self.robotnum),
                        dtype=int)
        # store the data
        for i in range(epoch):
            self.DAGG.GetDAG()  # pass
            DAG = self.DAGG.GetDAG()
            prec[self.robotnum:self.tasknum + self.robotnum,
                 self.robotnum:self.tasknum + self.robotnum] = DAG.arcs
            DataWrite(logfilename + "_" + str(i) + ".csv", [tasks, prec, d])
        self.ResetTaskNum(self.tasknum)  #clear the DAG Acculumate
        return True

    def GetDatafromFile(self, filename):
        tasks = []
        arcs = []
        d = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            n = int((len(data) - 1) / 3)
            for i in range(1, n + 1):
                tasks.append(list(map(int, data[i])))
            for i in range(n + 1, 2 * n + 1):
                arcs.append(list(map(float, data[i])))
            for i in range(2 * n + 1, 3 * n + 1):
                d.append(list(map(float, data[i])))
        tasks = np.array(tasks)
        d = np.array(d)
        prec = arcs
        return d, tasks[:, 2], tasks[:, 3], tasks[:, 4], prec

    def GetDatafromFileTemp(self, filename):
        tasks = []
        arcs = []
        data = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            n = int((len(data) - 1) / 2)
            for i in range(1, n + 1):
                tasks.append(list(map(int, data[i])))
            for i in range(n + 1, 2 * n + 1):
                arcs.append(list(map(float, data[i])))
        with open(filename, "w", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
            writer.writerows(self.GetDiss(tasks, n))
        print("modify " + filename + " sucessfully!")

    def GetSolomData(self, filename, outlog=0, logfilename=None):
        robots = []
        tasks = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            for i in range(1, len(data)):
                task = list(map(float, data[i]))
                # print(task)
                tasks.append([
                    int(task[1]),
                    int(task[2]),
                    int(task[3]),
                    int(task[5]),
                    int(task[6])
                ])
        robots = self.DataG.GetRandomRobots(self.robotnum)
        self.DAGG.GetDAG()  # pass
        DAG = self.DAGG.GetDAG()
        tasks_dummy = []
        for pos in robots:
            tasks_dummy.append([int(pos[0]), int(pos[1]), 0, 16000, 0])
        tasks = np.array(tasks_dummy + tasks)

        # calculate return value
        d = self.GetDiss(tasks, self.tasknum + self.robotnum)
        prec = np.zeros(shape=(self.tasknum + self.robotnum,
                               self.tasknum + self.robotnum))
        prec[self.robotnum:self.tasknum + self.robotnum,
             self.robotnum:self.tasknum + self.robotnum] = DAG.arcs
        # store the data
        if outlog:
            if logfilename is None:
                DataWrite("Data_example.csv", [tasks, prec, d])
            else:
                DataWrite(logfilename, [tasks, prec, d])
        return d, tasks[:, 2], tasks[:, 3], tasks[:, 4], prec

    def GetDynamicData(self, filename):
        tasks = []
        arcs = []
        d = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            n = int((len(data) - 1) / 3)
            for i in range(1, n + 1):
                tasks.append(list(map(int, data[i])))
            for i in range(n + 1, 2 * n + 1):
                arcs.append(list(map(float, data[i])))
            for i in range(2 * n + 1, 3 * n + 1):
                d.append(list(map(float, data[i])))
        tasks = np.array(tasks)
        d = np.array(d)
        prec = arcs
        return d, tasks[:, 0:2], tasks[:, 2], tasks[:, 3], tasks[:, 4], prec


# test
# Data = MIPData(3)
# Data.SetMap("map.csv")

# # print("initial_tasks", Data.DataG.initial_tasks)

# d, est, twl, dur, DAG = Data.GetDatafromFile("Data/R3/r3_t36_1.csv")
# print(d, est, twl, dur, DAG)
