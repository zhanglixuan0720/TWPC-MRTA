import sys

sys.path.append("./")
from MIP.MIPSolve import TWPCMIP
from DataGeneration.MRTAData import MRTAData
from common.logger import Logger
import time

import os

# robotnum = 2  # the number of robots
# tasknums = [9, 18]  #, 27, 36]  # the number of tasks
# map_epoch = 10
# dag_epoch = 10

InitDataRoot = "./Data/Init/"
# DataRoot = "./Data/RC" + str(robotnum) + "/"
SolRoot = "./Sol/MIP/MAXSolve6/"
LogRoot = "./Log/MAXSolve6/"

if not os.path.exists(SolRoot):
    os.makedirs(SolRoot)
if not os.path.exists(LogRoot):
    os.makedirs(LogRoot)

# log output
sys.stdout = Logger(LogRoot + "MAXSolve-Test-R-" +
                    time.strftime("%Y-%m-%d %H-%M", time.localtime()) + ".txt")

for robotnum in range(2, 10):
    Data = MRTAData(robotnum)
    Data.SetInitRT(InitDataRoot + "robot3.csv", InitDataRoot + "task60.csv")
    Data.SetMap(InitDataRoot + "map.csv")
    for tasknum in range(2 * robotnum, 60):
        Data.ResetTaskNum(tasknum)
        filename = "max_test_r" + str(robotnum) + "_t" + str(tasknum)

        twpcmip = TWPCMIP(filename)
        data = Data.GetDataM()
        twpcmip.solve(tasknum, robotnum, data)
        twpcmip.write(SolRoot + filename + ".sol")
        if twpcmip.Status != 2 and twpcmip.Status == 9:
            print("MAX NUM LIMITED: R " + str(robotnum) + " T " + str(tasknum))
            break
