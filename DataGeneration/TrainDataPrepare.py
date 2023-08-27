import sys

sys.path.append("./")
from DataGeneration.MRTAData import MRTAData
import os

# Get Random Data
robotnum = 3
tasknums = [9]
map_epoch = 100

InitDataDir = "./Data/Init/"
Data = MRTAData(robotnum)
Data.SetInitRT(InitDataDir + "robot3.csv", InitDataDir + "task60.csv")
Data.SetMap(InitDataDir + "map.csv")

rootr = "./Data/TR3"
if not os.path.exists(rootr):
    os.makedirs(rootr)

for tasknum in tasknums:
    Data.ResetTaskNum(tasknum)
    for i in range(0, map_epoch):
        filename = rootr + "/r" + str(robotnum) + "_t" + str(
            tasknum) + "_m" + str(i)
        Data.GetNPData(filename)
