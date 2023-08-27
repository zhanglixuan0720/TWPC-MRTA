import cv2
import numpy as np
import csv

# mouse left button down : set the block
# mouse right button down : cancel the block
# after setting finished, put keyword 's', the information,
# including  the overview of map and the data of map (0: nothing 1: block),
# will be stored in the root directory.


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


box = BoxGenerator()

#box = cv2.resize(box, (5, 5), interpolation=cv2.INTER_CUBIC)


def onMouse(event, x, y, flags, param):
    global box
    i = int(y / 100)
    j = int(x / 100)
    if event == cv2.EVENT_LBUTTONDOWN:
        print("left detection")
        param[100 * i:100 * (i + 1), 100 * j:100 * (j + 1)] = box
    elif event == cv2.EVENT_RBUTTONDOWN:
        print("right detection")
        if (i + j) % 2:
            param[i * 100:(i + 1) * 100, j * 100:(j + 1) * 100].fill(240)
        else:
            param[i * 100:(i + 1) * 100, j * 100:(j + 1) * 100].fill(255)


img = np.zeros(shape=(2000, 2000, 3), dtype=np.uint8)
grid = np.zeros(shape=(20, 20), dtype=np.uint8)

img.fill(255)
for i in range(0, 20):
    for j in range(0, 20):
        if (i + j) % 2:
            img[i * 100:(i + 1) * 100, j * 100:(j + 1) * 100].fill(240)

cv2.namedWindow('map grid', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
cv2.setMouseCallback("map grid", onMouse, img)
while True:
    cv2.imshow("map grid", img)
    flag = cv2.waitKey(30)
    if flag == 27:
        break
    elif flag == 115:
        cv2.imwrite("map.jpg", img)
        csvFile = open("map.csv",
                       "w", encoding='utf-8', newline='')
        writer = csv.writer(csvFile)
        # ____________________________
        for i in range(0, 20):
            for j in range(0, 20):
                grid[i][j] = img[i*100][j*100][0] < 235
        writer.writerows(grid)
        csvFile.close()
        print("write map sucessfyully.")
