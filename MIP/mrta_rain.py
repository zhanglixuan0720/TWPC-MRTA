import sys

sys.path.append("./")
from MIP.MIPSolve import TWPCMIP
from DataGeneration.MRTAData import MRTAData
from common.logger import Logger
import time

import os

robotnum = 3  # the number of robots
tasknums = [9]  #, 18]  #, 27, 36]  # the number of tasks
map_epoch = 100

InitDataRoot = "./Data/Init/"
DataRoot = "./Data/TR" + str(robotnum) + "/"
SolRoot = "./Sol/MIP/TR" + str(robotnum) + "/"
LogRoot = "./Log/MIP/T"

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
        filename = "r" + str(robotnum) + "_t" + str(tasknum) + "_m" + str(j)

        twpcmip = TWPCMIP(filename)

        data = Data.GetDatafromFile(DataRoot + filename + ".csv")
        twpcmip.solve(tasknum, robotnum, data)
        twpcmip.write(SolRoot + filename + ".sol")
