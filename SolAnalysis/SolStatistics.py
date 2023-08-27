import numpy as np
import csv
import sys

sys.path.append("./")


def SolStatisticsWrite(filename, data):
    csvFile = open(filename, "w", encoding='utf-8', newline='')
    writer = csv.writer(csvFile)
    writer.writerow([
        "MAKESPAN", "DISTANCE", "IDLE TIEME", "TASK COMPLETED", "ENERGY COST",
        "RUNTIME"
    ])
    for chip in data:
        writer.writerow([str(round(x, 4)) for x in chip])
    csvFile.close()
    print("write file " + filename + "  sucessfyully.")


def SolRead(filename):
    sol = {'R': [], 'O': [], 'S': [], 'F': [], 'Z': []}
    with open(filename, newline='\n') as f:
        reader = csv.reader(f, delimiter=' ')
        next(reader)  # skip header
        line = next(reader)
        TFnum, TAnum = int(line[3]), int(line[5])
        line = next(reader)
        Makespan, TotalDis, TotalTime = float(line[2][:-1]), float(
            line[5][:-1]), float(line[8])
        next(reader)
        for line in reader:
            for i in range(5):
                if 'inf' in line[i]:
                    line[i] = '-1'
            sol['R'].append(int(line[1]))
            sol['O'].append(int(line[2]))
            sol['S'].append(round(float(line[3])))
            sol['F'].append(round(float(line[4])))
        sol['Z'] = int(max(sol['F']))
    return sol, (Makespan, TotalDis, TFnum, TAnum, TotalTime)


def DataRead(filename):
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
    return d, tasks, prec


def CalDis(solR, solO, d):
    dis = 0
    for j in range(len(solO)):
        k = solO[j]
        if k != -1:
            dis += d[j][k]
    return dis


def CalIdleTime(solR, dur, diss, makespans):
    time = 0

    for i in range(len(dur)):
        if solR[i] != -1:
            time += dur[i]
    time = makespans - diss - time
    return time


def calEnergyCost(solR, dur, diss, ideltime):
    dur_time = 0
    for i in range(len(dur)):
        if solR[i] != -1:
            dur_time += dur[i]
    ec = diss + dur_time + 0.053 * ideltime
    return ec


robotnum = 3  # the number of robots
tasknums = [9, 18, 27, 36]  # the number of tasks
map_epoch = 10
dag_epoch = 10

InitDataRoot = "./Data/Init/"
DataRoot = "./Data/RL" + str(robotnum) + "/"
SolRoot = "./Sol/AuctionO/RL" + str(robotnum) + "/"
# SolRoot = "./Sol/AuctionO/RCA" + str(robotnum) + "/" Batch

metrics = np.zeros(shape=(len(tasknums), map_epoch * dag_epoch, 6))
# data
for k in range(0, 4):
    tasknum = tasknums[k]
    for i in range(0, map_epoch):
        for j in range(0, dag_epoch):
            filename = filename = "r" + str(robotnum) + "_t" + str(
                tasknum) + "_m" + str(i) + "_" + str(j)
            sol, metric = SolRead(SolRoot + filename + ".sol")
            dis, tasks, _ = DataRead(DataRoot + filename + ".csv")
            metrics[k][i * map_epoch + j][0] = metric[0]
            metrics[k][i * map_epoch + j][1] = metric[1]
            metrics[k][i * map_epoch + j][2] = CalIdleTime(
                sol['R'],
                np.array(tasks)[:, -1], metric[1], robotnum * metric[0])
            idletime = (len(np.where(np.array(sol['R']) != -1)[0]) -
                        robotnum) / tasknum
            metrics[k][i * map_epoch + j][3] = idletime
            metrics[k][i * map_epoch + j][4] = calEnergyCost(
                sol['R'],
                np.array(tasks)[:, -1], metric[1], idletime)
            metrics[k][i * map_epoch + j][5] = metric[4]

            if metric[2] != (len(np.where(np.array(sol['R']) != -1)[0]) -
                             robotnum):
                print("debug", filename,
                      (len(np.where(np.array(sol['R']) != -1)[0]) - robotnum))
                #metric[2] / metric[3]

result = np.sum(metrics, axis=1) / metrics.shape[1]
SolStatisticsWrite("./SolAnalysis/temp.csv", result)
print(result)
