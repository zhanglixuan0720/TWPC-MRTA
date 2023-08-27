import os
from DataGeneration.MRTAData import MRTAData
import sys

sys.path.append("./")

# Get Random Data
robotnum = 3
tasknums = [9, 18, 27, 36]
map_epoch = 10
dag_epoch = 10

InitDataDir = "./Data/Init/"
Data = MRTAData(robotnum)
Data.SetInitRT(InitDataDir + "robot10.csv", InitDataDir + "task60.csv")
Data.SetMap(InitDataDir + "map.csv")

rootr = "./Data/RC"+str(robotnum)
if not os.path.exists(rootr):
    os.makedirs(rootr)

for tasknum in tasknums:
    Data.ResetTaskNum(tasknum)
    for i in range(0, map_epoch):
        filename = rootr + "/r" + str(robotnum) + "_t" + str(
            tasknum) + "_m" + str(i)
        Data.GetMultiDAGData(filename, dag_epoch, True)
