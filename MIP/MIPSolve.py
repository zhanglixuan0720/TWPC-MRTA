import numpy as np
import gurobipy as gp
from gurobipy import GRB
import time
global MIP_M

MIP_M = 1e5  # big M method


class TWPCMIP():
    def __init__(self, name=""):
        self.modelname = name
        self.dis = None
        self.Sol = None
        self.Status = None

    def solve(self, tasknum, robotnum, data):
        global MIP_M
        t0 = time.perf_counter()
        d, est, twl, dur, prec = data
        self.dis = d
        # declare model
        m = gp.Model(self.modelname)

        # Time Limited
        m.setParam(GRB.Param.TimeLimit, 120.0)
        # m.setParam(GRB.Param.TimeLimit, 3600.0)
        # Min Gap
        # m.setParam(GRB.Param.MIPGap, 0.05)
        # define the decesion variable
        A = m.addMVar(shape=(tasknum + robotnum, robotnum),
                      vtype=GRB.BINARY,
                      name="A")  # allocation martix

        # allocation martix (for last task of every robot)
        Y = m.addMVar(shape=(tasknum + robotnum, robotnum),
                      vtype=GRB.BINARY,
                      name="Y")
        X = m.addMVar(shape=(robotnum, tasknum + robotnum, tasknum + robotnum),
                      vtype=GRB.BINARY,
                      name="X")  # precedence marix
        S = m.addMVar(shape=tasknum + robotnum, vtype=GRB.CONTINUOUS,
                      name="S")  # start time
        F = m.addMVar(shape=tasknum + robotnum, vtype=GRB.CONTINUOUS,
                      name="F")  # finish time
        Z = m.addMVar(shape=1, vtype=GRB.CONTINUOUS,
                      name="Z")  # objective varibale

        # define the objective function
        # m.setObjective(Z, GRB.MINIMIZE)
        m.setObjectiveN(A.sum(), 0, 1, weight=-1)
        m.setObjectiveN(
            0.053 * tasknum * Z +
            0.947 * gp.quicksum(X[i][j][k] * d[j][k] for i in range(robotnum)
                                for j in range(robotnum + tasknum)
                                for k in range(robotnum + tasknum)) +
            0.947 * gp.quicksum(A[j][i] * dur[j] for i in range(robotnum)
                                for j in range(robotnum + tasknum)), 1, 0)

        # add constrain
        for j in range(0, tasknum + robotnum):  # robotnum
            m.addConstr(Z >= F[j], name="maxZforF" + str(j))
        #choose the initial task
        for j in range(0, robotnum):
            m.addConstr(A[j][j] == 1, name="InitC" + str(j))
            # m.addConstr(F[j] == 0, name="InitC" + str(j))
            # m.addConstr(S[j] == 0, name="InitC" + str(j))

        # signal robot task constrain
        for j in range(0, robotnum):
            m.addConstr(A[j, :].sum() == 1, name="SRT" + str(j))
        for j in range(robotnum, tasknum + robotnum):
            m.addConstr(A[j, :].sum() <= 1, name="SRT" + str(j))

        for i in range(0, robotnum):
            m.addConstr(A[0:robotnum, i].sum() == 1,
                        name="SSTR" + str(i))  # signal start task robot
            m.addConstr(Y[:, i].sum() == 1,
                        name="SFTR" + str(i))  # signal finish task robot

            # signal pre task of task k for robot i
            for k in range(robotnum, tasknum + robotnum):
                m.addConstr(X[i, :, k].sum() - X[i][k][k] == A[k][i],
                            name="R" + str(i) + "SPreT" + str(k))

            # signal post task of task j for robot i
            for j in range(0, tasknum + robotnum):
                m.addConstr(X[i, j, robotnum:robotnum + tasknum].sum() -
                            X[i][j][j] + Y[j][i] == A[j][i],
                            name="R" + str(i) + "SPostT" + str(j))

            # order ensure
            for j in range(0, tasknum + robotnum):
                for k in range(0, tasknum + robotnum):
                    m.addConstr(F[j] + d[j][k] - MIP_M *
                                (1 - X[i][j][k]) <= S[k],
                                name="R" + str(i) + "oe" + str(j) + str(k))

        # duration constrain
        for j in range(0, tasknum + robotnum):  # robotnum
            m.addConstr(F[j] - S[j] >= dur[j], name="durc" + str(j))

        # precedence constrain
        for j in range(0, tasknum + robotnum):
            for k in range(0, tasknum + robotnum):
                if prec[j][k] == 1:
                    m.addConstr(S[k] - F[j] >= 0,
                                name="precc" + str(j) + "," + str(k))
                    m.addConstr(A[j, :].sum() - A[k, :].sum() >= 0,
                                name="preic" + str(j) + "," + str(k))

        # temporal constrain
        for j in range(0, tasknum + robotnum):
            m.addConstr(S[j] >= est[j], name="estc" + str(j))
            # m.addConstr(F[j] <= est[j] + twl[j] + MIP_M * (1 - A[j, :].sum()),name="twlc" + str(j))
            m.addConstr(F[j] <= est[j] + twl[j] + MIP_M *
                        (1 - gp.quicksum(A[j][i] for i in range(robotnum))),
                        name="twlc" + str(j))

        # save the model
        # m.write('mrat_opt_m.lp')

        # compute IIS
        # m.computeIIS()
        # m.write("mrat_opt_m.ilp")

        # solve
        m.optimize()

        # print solution
        print("Solve Status", m.Status)
        self.Dur = time.perf_counter() - t0
        self.Status = m.Status
        self.Sol = A.x, X.x, S.x, F.x

    def GetSol(self):
        solA, solX, solS, solF = self.Sol

        robotnum = solA.shape[1]
        tasknum = solA.shape[0] - robotnum
        R = np.zeros(robotnum + tasknum, dtype=int)
        O = np.zeros(robotnum + tasknum, dtype=int)
        S = np.zeros(robotnum + tasknum)
        F = np.zeros(robotnum + tasknum)
        O.fill(-1)
        R.fill(-1)
        S.fill(-1)
        F.fill(-1)
        TotalDis = 0
        Makespan = 0

        for k in range(robotnum):
            for i in range(robotnum + tasknum):
                if solA[i][k] > 0.9:
                    R[i] = k
                    continue

        for i in range(robotnum + tasknum):
            S[i] = round(solS[i])
            F[i] = round(solF[i])

        for i in range(0, solX.shape[0]):
            mx = solX[i]
            for j in range(0, mx.shape[0]):
                for k in range(0, mx.shape[1]):
                    if mx[j][k] > 0.99:
                        O[j] = k
                        TotalDis += self.dis[j][k]
        for i in range(len(R)):
            if R[i] != -1:
                Makespan = max(Makespan, F[i])

        return R, O, S, F, Makespan, TotalDis

    def write(self, filename):
        solA, solX, solS, solF = self.Sol

        robotnum = solA.shape[1]
        tasknum = solA.shape[0] - robotnum
        R = np.zeros(robotnum + tasknum)
        O = np.zeros(robotnum + tasknum)
        S = np.zeros(robotnum + tasknum)
        F = np.zeros(robotnum + tasknum)
        O.fill(-1)
        R.fill(-1)
        S.fill(-1)
        F.fill(-1)
        TotalDis = 0
        Makespan = 0

        for k in range(robotnum):
            for i in range(robotnum + tasknum):
                if solA[i][k] > 0.9:
                    R[i] = k
                    continue

        for i in range(robotnum + tasknum):
            S[i] = round(solS[i])
            F[i] = round(solF[i])

        for i in range(0, solX.shape[0]):
            mx = solX[i]
            for j in range(0, mx.shape[0]):
                for k in range(0, mx.shape[1]):
                    if mx[j][k] > 0.9:
                        O[j] = k
                        TotalDis += self.dis[j][k]

        Makespan = np.max(F)
        R, O, S, F, Makespan, TotalDis = self.GetSol()
        with open(filename, "w", encoding='utf-8') as f:
            f.write("# Solution for model " + self.modelname + "\n")
            f.write("# Finished Task: " +
                    str(int(np.array(solA).sum()) - robotnum) + " / " +
                    str(tasknum) + "\n")
            f.write("# Makespan: " + str(Makespan) + ", Total Distance: " +
                    str(TotalDis) + ", Total Time: " + '%.4f' % self.Dur +
                    "\n")
            f.write(' '.join(['#', 'R', 'O', 'S', 'F']) + '\n')
            for i in range(robotnum + tasknum):
                f.write(' '.join(
                    [str(x) for x in [i, int(R[i]),
                                      int(O[i]), S[i], F[i]]]) + '\n')
