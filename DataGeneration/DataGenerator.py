import numpy as np
from random import uniform
from random import sample
import csv

tasknum = 10
robotnum = 2


def uniformint(low, high):
    value = int(uniform(low, high))
    while value == high:
        value = uniform(low, high)
    return value


def PosRed(filename):
    pos = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        for i in range(1, len(data)):
            pos.append((int(data[i][1]), int(data[i][2])))
    return pos


def FindMinDis(pos, dsts):
    minidx = 0
    mindis = abs(dsts[minidx][0] - pos[0]) + abs(dsts[minidx][1] - pos[1])
    for i in range(1, len(dsts)):
        curdis = abs(dsts[i][0] - pos[0]) + abs(dsts[i][1] - pos[1])
        if mindis > curdis:
            minidx = i
            mindis = curdis
    return minidx


class DataGenerator:
    def __init__(self, initial_robots=None, initial_tasks=None):
        self.initial_robots = initial_robots
        self.initial_tasks = initial_tasks

    # csv read version
    def SetInitRT(self, filename_robots, filename_tasks):
        if type(filename_robots) != type("") or type(filename_tasks) != type(
                ""):
            return
        self.initial_robots = PosRed(filename_robots)
        self.initial_tasks = PosRed(filename_tasks)

    def GetData(self, tasknum, robotnum=3):
        if robotnum > 10:
            print("The number of robots can not beyond 3.")
            robotnum
        tasks = []
        for _ in range(0, tasknum):
            x, y = uniformint(0, 100), uniformint(0, 100)
            pos = self.initial_tasks[FindMinDis((x, y), self.initial_tasks)]
            est = uniformint(25, 400)
            twl = uniformint(100, 1600)
            dur = uniformint(20, 40)
            tasks.append([pos[0], pos[1], est, twl, dur])

        return [self.initial_robots[i]
                for i in sample(range(10), robotnum)], tasks

    def GetDataM(self, tasknum, robotnum=3):
        robots = []
        if robotnum > 3:
            while robotnum > 3:
                robots += [
                    self.initial_robots[i] for i in sample([0, 1, 2], 3)
                ]
                robotnum -= 3
            robots += [
                self.initial_robots[i] for i in sample([0, 1, 2], robotnum)
            ]
        else:
            robots += [
                self.initial_robots[i] for i in sample([0, 1, 2], robotnum)
            ]
        tasks = []
        for _ in range(0, tasknum):
            x, y = uniformint(0, 100), uniformint(0, 100)
            pos = self.initial_tasks[FindMinDis((x, y), self.initial_tasks)]
            est = uniformint(25, 400)
            twl = uniformint(100, 1600)
            dur = uniformint(20, 40)
            tasks.append([pos[0], pos[1], est, twl, dur])

        return robots, tasks

    def GetDataC(self, tasknum, robotnum=3):
        if robotnum > 3:
            print("The number of robots can not beyond 3.")
        tasks = []
        for tn in range(0, tasknum):
            x, y = uniformint(0, 100), uniformint(0, 100)
            pos = self.initial_tasks[FindMinDis((x, y), self.initial_tasks)]
            shiftC = 40 * int(tn / 3)
            est = uniformint(25 + shiftC, 400 + shiftC)
            twl = uniformint(100, 1600)
            dur = uniformint(20, 40)
            tasks.append([pos[0], pos[1], est, twl, dur])

        return [self.initial_robots[i]
                for i in sample([0, 1, 2], robotnum)], tasks

    def GetRandomRobots(self, robotnum):
        robots = []
        for i in range(0, robotnum):
            robots.append(
                [uniformint(0, 100),
                 uniformint(0, 100), 0, 16000, 0])
        return robots