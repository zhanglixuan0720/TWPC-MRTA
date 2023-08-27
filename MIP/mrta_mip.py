import os
import time
from DataGeneration.MRTAData import MRTAData
from common.logger import Logger
from MIP.MIPSolve import TWPCMIP
import sys

sys.path.append("./")


robotnum = 5  # the number of robots
tasknums = [9, 18]  # , 27, 36]  # the number of tasks
map_epoch = 10
dag_epoch = 10

InitDataRoot = "./Data/Init/"
DataRoot = "./Data/RL" + str(robotnum) + "/"
SolRoot = "./Sol/MIP/RL" + str(robotnum) + "/"
LogRoot = "./Log/MIP/"

if not os.path.exists(SolRoot):
    os.makedirs(SolRoot)
if not os.path.exists(LogRoot):
    os.makedirs(LogRoot)

Data = MRTAData(robotnum)
Data.SetInitRT(InitDataRoot + "robot3.csv", InitDataRoot + "task60.csv")
Data.SetMap(InitDataRoot + "map.csv")
# log output
sys.stdout = Logger(LogRoot + "R" + str(robotnum) + "-" +
                    time.strftime("%Y-%m-%d %H-%M", time.localtime()) + ".txt")
# data
for i in range(0, 1):
    tasknum = tasknums[i]
    for j in range(0, map_epoch):
        for k in range(0, dag_epoch):
            filename = "r" + str(robotnum) + "_t" + str(tasknum) + "_m" + str(
                j) + "_" + str(k)

            twpcmip = TWPCMIP(filename)

            data = Data.GetDatafromFile(DataRoot + filename + ".csv")
            twpcmip.solve(tasknum, robotnum, data)
            twpcmip.write(SolRoot + filename + ".sol")
