import numpy as np

# def TwoDiv(series):
#     series_sorted = sorted(series, key=lambda x: x[1], reverse=True)
#     return series_sorted[0][0]


def TwoDiv(series, begin, end, minnum):
    series_sorted = sorted(series, key=lambda x: x[1], reverse=True)
    for idx, _ in series_sorted:
        if idx - begin >= minnum and end - idx >= minnum:
            return idx
    return series_sorted[0][0]
    # InsertIdx = GetInsertIdx(idx, divpoints)
    # if InsertCheck(divpoints, (InsertIdx, idx), prenum, count, minnum,
    #                maxnum):
    #     divpoints.insert(InsertIdx, idx)

    # if k == 0:
    #     break
    # return series_sorted[0][0]


def InsertCheck(divpoints, InsertIdx, prenum, count, minnum):
    divpoints_temp = divpoints.copy()
    divpoints_temp.insert(InsertIdx[0], InsertIdx[1])
    divpoints_temp = [-prenum] + divpoints_temp + [count]
    for i in range(len(divpoints_temp) - 1):
        delta = divpoints_temp[i + 1] - divpoints_temp[i]
        if delta < minnum:  #or delta > maxnum:
            return False
    return True


def GetInsertIdx(idx, divpoints):
    for i in range(len(divpoints)):
        if idx < divpoints[i]:
            return i
    return 0


def HierCluster(Series, K, prenum, minnum=0, maxnum=np.inf):
    k = K
    divpoints = []
    series = []
    count = 0
    for key in Series:
        series.append([count, Series[key]])
        count += 1

    series_sorted = sorted(series, key=lambda x: x[1], reverse=True)
    for idx, _ in series_sorted:
        InsertIdx = GetInsertIdx(idx, divpoints)
        if InsertCheck(divpoints, (InsertIdx, idx), prenum, count, minnum):
            divpoints.insert(InsertIdx, idx)
            k -= 1
        if k == 0:
            break

    # Insert
    Insert = []
    if divpoints[0] + prenum > maxnum:
        idx = TwoDiv(series[1:divpoints[0]], 1, divpoints[0], minnum)
        Insert.append([0, idx])

    for i in range(len(divpoints) - 1):
        if divpoints[i + 1] - divpoints[i] > maxnum:
            idx = TwoDiv(series[divpoints[i] + 1:divpoints[i + 1]],
                         divpoints[i] + 1, divpoints[i + 1], minnum)
            Insert.append([i + 1, idx])
    if count - divpoints[-1] > maxnum:
        idx = TwoDiv(series[divpoints[-1] + 1:], divpoints[-1] + 1,
                     len(divpoints), minnum)
        Insert.append([len(divpoints), idx])
    counti = 0
    for x in Insert:
        divpoints.insert(x[0] + counti, x[1])
        counti += 1

    return divpoints
    # is_insert = False
    # for i in range(len(divpoints)):
    #     if idx < divpoints[i]:
    #         divpoints.insert(i, idx)
    #         is_insert = True
    #         break
    # if is_insert == False:
    #     divpoints.insert(0, idx)

    # k -= 1
    # if k == 0:
    #     break

    # is_ok = False
    # while is_ok != True:
    #     is_ok = True

    #     # Insert
    #     Insert = []
    #     if divpoints[0] + prenum > maxnum:
    #         idx = TwoDiv(series[1:divpoints[0]])
    #         Insert.append([0, idx])
    #         is_ok = False

    #     for i in range(len(divpoints) - 1):
    #         if divpoints[i + 1] - divpoints[i] > maxnum:
    #             idx = TwoDiv(series[divpoints[i] + 1:divpoints[i + 1]])
    #             Insert.append([i + 1, idx])
    #             is_ok = False
    #     if count - divpoints[-1] > maxnum:
    #         idx = TwoDiv(series[divpoints[-1] + 1:])
    #         Insert.append([len(divpoints), idx])
    #         is_ok = False
    #     counti = 0
    #     for x in Insert:
    #         divpoints.insert(x[0] + counti, x[1])
    #         counti += 1

    #     # Del
    #     Del = []
    #     is_del = True
    #     while is_del:
    #         is_del = False
    #         if len(divpoints) < 2:
    #             continue
    #         if divpoints[0] + prenum < minnum and divpoints[
    #                 1] + prenum <= maxnum:
    #             del divpoints[0]
    #             is_del = True
    #             continue
    #         if len(divpoints) > 1:
    #             if count - divpoints[-1] < minnum and divpoints[
    #                     -2] - divpoints[-1] <= maxnum:
    #                 del divpoints[-1]
    #                 is_del = True
    #                 continue

    #         for i in range(len(divpoints) - 1):
    #             if divpoints[i + 1] - divpoints[i] < minnum:
    #                 neighbor = [[-1, np.inf], [-1, np.inf]]
    #                 if i == 0:
    #                     if divpoints[i + 1] - 0 <= maxnum:
    #                         neighbor[0][0] = divpoints[i] - 0
    #                         neighbor[0][1] = series_sorted[divpoints[i]][0]
    #                 if i > 0:
    #                     if divpoints[i + 1] - divpoints[i - 1] <= maxnum:
    #                         neighbor[0][0] = divpoints[i] - divpoints[i - 1]
    #                         neighbor[0][1] = series_sorted[divpoints[i]][0]
    #                 if i < len(divpoints) - 2:
    #                     if divpoints[i + 1] - divpoints[i - 1] <= maxnum:
    #                         neighbor[1][0] = divpoints[i + 1] - divpoints[i]
    #                         neighbor[1][1] = series_sorted[divpoints[i]][0]
    #                 if i == len(divpoints) - 2:
    #                     if count - divpoints[i] <= maxnum:
    #                         neighbor[1][0] = divpoints[i + 1] - divpoints[i]
    #                         neighbor[1][1] = series_sorted[divpoints[i + 1]][0]
    #                 if neighbor[0][0] != -1 or neighbor[1][0] != -1:
    #                     is_ok = False
    #                     is_del = True
    #                     if neighbor[0][1] < neighbor[1][1]:
    #                         del divpoints[i]
    #                         # Del.append(divpoints[i])
    #                     elif neighbor[0][1] < neighbor[1][1]:
    #                         del divpoints[i + 1]
    #                         # Del.append(divpoints[i + 1])
    #                     else:
    #                         if neighbor[0][0] < neighbor[1][0]:
    #                             # Del.append(divpoints[i])
    #                             del divpoints[i]
    #                         else:
    #                             del divpoints[i + 1]
    #                     break
    #                     # Del.append(divpoints[i + 1])

    # for x in Del:
    #     divpoints.remove(x)
    return divpoints


# d = {0: 0, 1: -7, 2: -8, 3: 2, 4: 7, 5: 5, 6: 11, 7: 2, 8: 6, 9: -2}
# divpoints = HierCluster(d, 3, 6, 3)
# print(divpoints)
#[Series[key] for key in Series]
