import numpy as np
from AuctionO.STN import STN


class Robot:
    def __init__(self, ID):
        self.RobotID = ID
        self.stn = STN(ID)
        self.bacth_id = -1
        self.bacth_base = -1

    def bid(self, task, id):
        if self.bacth_id != id:
            self.bacth_id = id
            self.bacth_base = self.stn.tasknum
        b = np.inf
        bidx = -1
        for i in range(self.bacth_base, self.stn.tasknum + 1):
            makespan = self.stn.InsertVerify(i, task)
            b_i = makespan
            if makespan >= 0 and b_i < b:
                b = b_i
                bidx = i
        return bidx, b

    def win(self, idx, task):
        if self.stn.InsertTask(idx, task) is False:
            print("illegal winner.")
            return False
        return True

    def SolidTask(self, t):
        idxs = self.GetAllocatedTask()
        sr, _ = self.GetSFTime()
        for i in range(len(idxs)):
            if t == idxs[i]:
                self.stn.constrain[t][0] = sr[i]
                self.stn.constrain[t][1] = sr[i]
                return True
        return False

    @staticmethod
    def SetMap(d):
        STN.diss = d

    def GetAllocatedTask(self):
        return self.stn.taskorder

    def GetSFTime(self):
        dgraph = self.stn.GetMinNetwork()
        lower = -dgraph[1:self.stn.eventnum, 0]
        return lower[0::2], lower[1::2]

    def GetMaskSpan(self):
        return self.stn.makespan

    def GetDistance(self):
        return self.stn.CountDis()
