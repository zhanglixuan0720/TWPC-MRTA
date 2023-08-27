import sys

sys.path.append("./")
import cv2
import csv
import numpy as np
from common import priority
from common import AStar
# r3_t9_m2_1
filename = "r3_t36_m2_2"
mapfilename = "./Data/Init/map.csv"
datafilename = "./Data/RL3/" + filename + ".csv"
solfilename = "./Sol/Batch/RL3/" + filename + ".sol"
videofilename = "./Video/" + filename + "b-u" + ".avi"
is_write = False
is_show = False

# Noting that  if the data set is cluster set,
# the number showed in column 47 should be replaced by 16000.


def MapRead(filename):
    img = np.zeros(shape=(2000, 2000, 3), dtype=np.uint8)
    img.fill(255)
    for i in range(0, 20):
        for j in range(0, 20):
            if (i + j) % 2:
                img[i * 100:(i + 1) * 100, j * 100:(j + 1) * 100].fill(240)
    box = BoxGenerator()
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        grid = list(reader)
        for i in range(0, 20):
            for j in range(0, 20):
                if grid[i][j] == '1':
                    img[100 * i:100 * (i + 1), 100 * j:100 * (j + 1)] = box
    return img


def DataRead(filename):
    tasks = []
    robots = []
    arcs = []
    d = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
        n = int((len(data) - 1) / 3)
        for i in range(1, n + 1):
            if int(data[i][3]) == 16000:
                robots.append(list(map(int, data[i])))
            else:
                tasks.append(list(map(int, data[i])))
        for i in range(n + 1, 2 * n + 1):
            arcs.append(list(map(float, data[i])))
        for i in range(2 * n + 1, 3 * n + 1):
            d.append(list(map(float, data[i])))
    d = np.array(d)
    return robots, tasks, robots + tasks, np.array(arcs).astype(int), d


def SolRead(filename):
    sol = {'R': [], 'O': [], 'S': [], 'F': [], 'Z': []}
    with open(filename, newline='\n') as f:
        reader = csv.reader(f, delimiter=' ')
        next(reader)  # skip header
        next(reader)
        next(reader)
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
    return sol


def BoxGenerator():
    color = (230, 185, 140)
    box = np.zeros(shape=(100, 100, 3), dtype=np.uint8)
    block = np.zeros(shape=(50, 100, 3), dtype=np.uint8)
    block.fill(color[0])
    block[5:45, 5:95].fill(color[1])
    block[45:50, 5:95].fill(color[2])
    block[5:50, 95:100].fill(color[2])
    for i in range(0, 5):
        for j in range(0, 5):
            if i + j >= 4:
                block[i + 45][j] = color[2]
                block[i][j + 95] = color[2]

    box[0:50, 0:100] = block
    box[50:100, 0:50] = block[0:50, 50:100]
    box[50:100, 50:100] = block[0:50, 0:50]

    return box


def GetColor(ts, prior):
    l = len(set(prior)) - 1
    n = len(ts)
    color = np.zeros(shape=(1, n, 3), dtype=np.uint8)
    color.fill(255)
    color[0][ts[n - 1]][0] = 0
    # color[0][ts[n - 1]][1] =
    count = 0.0
    for i in range(n - 2, -1, -1):
        color[0][ts[i]][0] = 0
        if l:
            if prior[ts[i]] < prior[ts[i + 1]]:
                count += 1
            color[0][ts[i]][1] = int(220 * (count / l) +
                                     35)  # h -> s int(count * 120 / l)
        else:
            color[0][ts[i]][1] = 255

    color = cv2.cvtColor(color, cv2.COLOR_HSV2BGR)
    color = np.reshape(color, (n, 3))
    return color


def DrawTasks(img, tasks, colors):
    pos_colors = []
    pos_dict = {}
    for task in tasks:
        pos = (task[0] * 20, task[1] * 20)
        if pos not in pos_dict:
            pos_dict[pos] = 1
        else:
            pos_dict[pos] += 1
    draw_pos_dict = dict.fromkeys(pos_dict.keys(), 0)
    for i in range(0, len(tasks)):
        pos = (tasks[i][0] * 20, tasks[i][1] * 20)
        alph = draw_pos_dict[pos] / pos_dict[pos]
        beta = (draw_pos_dict[pos] + 1) / pos_dict[pos]
        color = tuple(int(x - alph * 255) for x in colors[i])
        cv2.ellipse(img, pos, (15, 15), 0, alph * 360, beta * 360, color, -1)
        draw_pos_dict[pos] += 1
        pos_colors.append([alph, beta, color])
    return pos_colors


def DrawLines(img, solR, solO):
    lines_color = [(255, 0, 0), (255, 255, 0), (128, 0, 128)]
    for j in range(len(solO)):
        k = solO[j]
        if k != -1:
            start = (20 * dtasks[j][0], 20 * dtasks[j][1])
            end = (20 * dtasks[k][0], 20 * dtasks[k][1])
            mid = (10 * (dtasks[j][0] + dtasks[k][0]),
                   10 * (dtasks[j][1] + dtasks[k][1]))
            cv2.line(img,
                     start,
                     end,
                     lines_color[solR[j]],
                     thickness=2,
                     lineType=cv2.LINE_AA)
            cv2.arrowedLine(img,
                            start,
                            mid,
                            lines_color[solR[j]],
                            thickness=2,
                            line_type=cv2.LINE_AA,
                            shift=0,
                            tipLength=0.05)


def DrawRoads(img, solR, solO, solS, grid):
    lines_color = [(255, 0, 0), (255, 255, 0), (128, 0, 128)]
    for j in range(len(solO)):
        k = solO[j]
        if k != -1:
            cost, path = AStar.ASatr(grid.copy(), (dtasks[j][1], dtasks[j][0]),
                                     (dtasks[k][1], dtasks[k][0]), True)
            if cost != -1:
                for i in range(len(path) - 1):
                    start = (20 * path[i][1], 20 * path[i][0])
                    end = (20 * path[i + 1][1], 20 * path[i + 1][0])
                    cv2.line(img,
                             start,
                             end,
                             lines_color[solR[j]],
                             thickness=2,
                             lineType=cv2.LINE_AA)


img = MapRead(mapfilename)
grid = AStar.MapRead(mapfilename, 1)

robots, tasks, dtasks, arcs, d = DataRead(datafilename)
robotnum = len(robots)

sol = SolRead(solfilename)
solR, solO, solS, solF = sol['R'], sol['O'], sol['S'], sol['F']

Roads = np.zeros(shape=(sol['Z'], len(robots), 2), dtype=int)
Roads.fill(-1)
TFailed = []
for j in range(len(solR)):
    if solR[j] == -1:
        TFailed.append(j)

for j in range(len(solO)):
    k = solO[j]
    if k != -1:
        cost, path = AStar.ASatr(grid.copy(), (dtasks[j][1], dtasks[j][0]),
                                 (dtasks[k][1], dtasks[k][0]), True)
        if cost != -1:
            for i in range(len(path) - 1):
                Roads[solF[j] + i][solR[j]] = np.array(path[i]).astype(int)

for j in range(len(solF)):
    t = solS[j]
    t_end = max(0, solS[j] + dtasks[j][-1])
    if t != -1:
        while t != t_end:
            if Roads[t][solR[j]][0] == -1:
                Roads[t][solR[j]][1] = j
            t += 1

for i in range(len(robots)):
    robot = robots[i]
    cv2.putText(img, "R" + str(i), (robot[0] * 20 - 30, robot[1] * 20 + 15),
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 3)
    cv2.rectangle(img, (robot[0] * 20 - 30, robot[1] * 20 - 30),
                  (robot[0] * 20 + 30, robot[1] * 20 + 30), (0, 0, 0), 2)

ts, prior = priority.priority(arcs[len(robots):len(dtasks),
                                   len(robots):len(dtasks)])
colors = GetColor(ts, prior)
pos_colors = DrawTasks(img, tasks, colors)

# Draw Video
lines_color = [(255, 0, 0), (255, 255, 0), (128, 0, 128)]
if is_show == True:
    cv2.namedWindow('map grid', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

video = None
if is_write == True:
    video = cv2.VideoWriter(videofilename,
                            cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                            (2000, 2000))

figure_count = 0
for i in range(Roads.shape[0]):
    img1 = img.copy()
    cv2.putText(img1, "Time: " + str(i) + " sec", (10 * 20, 14 * 20),
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 2)
    #Deal Failed Task
    remove_list = []
    for ft in TFailed:
        task = dtasks[ft]
        if task[2] + task[3] - task[4] < i:
            pos = (task[0] * 20, task[1] * 20)
            alph = pos_colors[ft - robotnum][0]
            beta = pos_colors[ft - robotnum][1]
            cv2.ellipse(img, pos, (25, 25), 0, alph * 360, beta * 360,
                        (192, 192, 192), 3)
            remove_list.append(ft)
    for ft in remove_list:
        TFailed.remove(ft)
    for r in range(Roads.shape[1]):
        robot = Roads[i][r]
        if robot[0] == -1:
            ir = robot[1]
            if ir >= robotnum:
                task = dtasks[ir]
                pos = (dtasks[ir][0] * 20, dtasks[ir][1] * 20)
                alph = pos_colors[ir - robotnum][0]
                beta = pos_colors[ir - robotnum][1]
                beta = alph + (beta - alph) * ((i - solS[ir]) / dtasks[ir][-1])
                color = pos_colors[ir - robotnum][2]
                cv2.ellipse(img, pos, (25, 25), 0, alph * 360, beta * 360,
                            color, 3)
            Roads[i][r] = Roads[i - 1][r]
            robot = Roads[i][r]
        elif i != 0:
            start = tuple(Roads[i - 1][r][::-1] * 20)
            end = tuple(Roads[i][r][::-1] * 20)
            cv2.line(img,
                     start,
                     end,
                     lines_color[r],
                     thickness=2,
                     lineType=cv2.LINE_AA)
        robot = robot[1], robot[0]
        img1[robot[1] * 20 - 30:robot[1] * 20 + 31,
             robot[0] * 20 - 30:robot[0] * 20 + 31].fill(0)
        cv2.putText(img1, "R" + str(r),
                    (robot[0] * 20 - 30, robot[1] * 20 + 15),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (255, 255, 255), 3)

    if is_write == True:
        video.write(img1)

    # if i in [0, 143, 287, Roads.shape[0] - 1]:
    # cv2.putText(img, "Time: " + str(i + 1) + " sec", (10 * 20, 14 * 20),
    #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 0), 2)
    # for ft in TFailed:
    #     task = dtasks[ft]
    #     pos = (task[0] * 20, task[1] * 20)
    #     alph = pos_colors[ft - robotnum][0]
    #     beta = pos_colors[ft - robotnum][1]
    #     cv2.ellipse(img, pos, (25, 25), 0, alph * 360, beta * 360,
    #                 (192, 192, 192), 3)
    # TFailed.remove(ft)
    # cv2.imwrite(
    #     "./Figure/DEMO-experiment-R" + str(robotnum) + "-" +
    #     str(figure_count) + ".jpg", img1)
    # figure_count += 1
    # print("write " + "" + " sucessfully.")
    # if i == Roads.shape[0] - 1:
    #     break

    if is_show == True:
        cv2.imshow("map grid", img1)
        if cv2.waitKey(30) == 27:
            break
cv2.imwrite(
        "./Figure/Image-experiment-R" + str(robotnum)  + ".jpg", img1)

cv2.waitKey(0)
