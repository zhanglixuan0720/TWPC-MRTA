import cv2
import numpy as np
import csv

# mouse left button down : set the initial robot
# mouse right button down : set the poetntial task
# mouse middle button dowm : cancel the task or robot setting
# after setting finished, put keyword 's', the information,
# including task coordinates, robot coordinates and the overview
# of map with task and robots, will be stored in the root directory.



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

pos_robot = []
pos_task = []
img0 = MapRead("./Data/Init/map.csv")


def PosWrite(filename, pos):
    csvFile = open(filename+".csv",
                   "w", encoding='utf-8', newline='')
    writer = csv.writer(csvFile)
    writer.writerow([filename + " ID", "XCOORD.", "YCOORD."])
    for i in range(0, len(pos)):
        writer.writerow([i, pos[i][0], pos[i][1]])
    csvFile.close()
    print("write "+filename+" coordinate sucessfyully.")


def onMouse(event, x, y, flags, param):
    global pos_robot
    global pos_task
    x = int(x/20)
    y = int(y/20)
    if event == cv2.EVENT_LBUTTONDOWN:
        print("left detection")
        for pos in pos_robot:
            if abs(pos[0] - x) < 3 and abs(pos[1] - y) < 3:
                print("Robots can not be put too closely!")
                return
        for pos in pos_task:
            if abs(pos[0] - x) < 3 and abs(pos[1] - y) < 3:
                print("Robot and task can not be put too closely!")
                return
        xlow = x - 1 if x - 1 >= 0 else x
        xhigh = x + 1 if x + 1 < 100 else x
        ylow = y - 1 if y - 1 >= 0 else y
        yhigh = y + 1 if y + 1 < 100 else y
        for i in range(20*ylow, 20*yhigh + 1):
            for j in range(20*xlow, 20*xhigh + 1):
                if param[i][j][2] < 235:
                    print("Robots can not be put on block!")
                    return
        print("set robot (" + str(x) + "," + str(y) + ")")
        param[20*ylow:20*yhigh + 1, 20*xlow:20*xhigh + 1].fill(0)
        pos_robot.append((x, y))
        # for i in range(ylow, yhigh + 1):
        #     for j in range(xlow, xhigh + 1):
        #         param[i][j] = np.array([0, 0, 0])
    elif event == cv2.EVENT_RBUTTONDOWN:
        print("right detection")
        for pos in pos_robot:
            if abs(pos[0] - x) < 3 and abs(pos[1] - y) < 3:
                print("Robots can not be put too closely!")
                return
        for pos in pos_task:
            if abs(pos[0] - x) < 3 and abs(pos[1] - y) < 3:
                print("Robot and task can not be put too closely!")
                return
        xlow = x - 1 if x - 1 >= 0 else x
        xhigh = x + 1 if x + 1 <= 100 else x
        ylow = y - 1 if y - 1 >= 0 else y
        yhigh = y + 1 if y + 1 <= 100 else y
        for i in range(20*ylow, 20*yhigh + 1):
            for j in range(20*xlow, 20*xhigh + 1):
                if param[i][j][2] < 235:
                    print("Robots can not be put on block!")
                    return
        print("set task (" + str(x) + "," + str(x) + ")")
        cv2.circle(param, (20*x, 20*y), 15, (0, 0, 255), -1)
        pos_task.append((x, y))
    elif event == cv2.EVENT_MBUTTONDOWN:
        print("middle detection")
        for pos in pos_robot:
            if abs(pos[0] - x) < 3 and abs(pos[1] - y) < 3:
                pos_robot.remove(pos)
                param[20*(pos[1] - 1):20*(pos[1] + 1)+1, 20*(pos[0] - 1):20*(pos[0] + 1)+1
                      ] = img0[20*(pos[1] - 1):20*(pos[1] + 1)+1, 20*(pos[0] - 1):20*(pos[0] + 1)+1]
                print("delete robot (" + str(pos[0]) + "," + str(pos[1]) + ")")
                return
        for pos in pos_task:
            if abs(pos[0] - x) < 3 and abs(pos[1] - y) < 3:
                xlow = pos[0] - 1 if pos[0] - 1 >= 0 else pos[0]
                xhigh = pos[0] + 1 if pos[0] + 1 < 100 else pos[0]
                ylow = pos[1] - 1 if pos[1] - 1 >= 0 else pos[1]
                yhigh = pos[1] + 1 if pos[1] + 1 < 100 else pos[1]
                param[20*ylow:20*yhigh+1, 20*xlow:20*xhigh +
                      1] = img0[20*ylow:20*yhigh + 1, 20*xlow:20*xhigh + 1]
                pos_task.remove(pos)
                print("delete task (" + str(pos[0]) + "," + str(pos[1]) + ")")
                return


img = img0.copy()
cv2.namedWindow('map grid', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
cv2.setMouseCallback("map grid", onMouse, img)


while True:
    cv2.imshow("map grid", img)
    flag = cv2.waitKey(30)
    if flag == 27:
        break
    elif flag == 115:
        cv2.imwrite("Robot3Task.jpg", img)
        PosWrite("robotn", pos_robot)
        PosWrite("taskrn", pos_task)
