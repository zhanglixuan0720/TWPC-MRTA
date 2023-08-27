# BMRTA: Energy Efficient Multi-Robot Task Allocation Constrained by Time Window and Precedence

## Abstract

To meet the demands in terms of energy-efficient and fast production and delivery of goods, robotic fleets began to populate warehouses and industrial environments. To maximize the profitability of the operations, multi-robot systems are required to coordinate agents avoiding downtime efficiently. 
In this paper, agent coordination is formulated as a multi-robot task allocation (MRTA) problem with time and precedence constraints. The method capitalizes on a graph method to build a measure graph reflecting the sparsity of tasks and a precedence graph, which includes the task constraints, to group the tasks into batches. A batch solver is provided to obtain the final solutions to the MRTA.
In this way, the sustainability and environmental impact of logistics operations can be improved by reducing the number of robots needed to complete tasks and also by assigning tasks closest to the robot location, reducing the amount of time and the total energy required for the robots to complete the job.
Extensive experiments on both uniformly distributed and sparse data sets prove the effectiveness of the proposed algorithm compared to state-of-the-art algorithms such as MIP and TePSSI.

## 1. Prerequisites

- Python
- Gurobi 9.5.2

## 2. Dataset

### 2.1 Dataset Overview

Two datasets, the Uniform Distribution (UD) dataset, and the Cluster Distribution (CD) dataset are shown in Floder [Data](./Data/). Both datasets are organized as `RL{is_cluster}{robot number}`, where the `is_cluster` is defined as whether or not with the suffix C and the `robot number` $n_r$ refers $3,5,10$. For example, the Floder [RL3](./Data/RL3/) in [Data](./Data/) contains all samples with the $n_r =3$ in UD dataset; the Floder [RLC3](./Data/RLC3/) in [Data](/Data/) contains all samples with the $n_r =3$ in CD dataset. 

Each sample in the dataset is stored in `.csv` format and named as `r{nr}_t{nt}_m{map_id}_{sample_id}`, where `nr` is the number of robots; `nt` is the number of tasks; `map_id` marks different robots and tasks location instances; `sample_id` marks different time window and precedence constraints. One sample file `r{nr}_t{nt}_m{map_id}_{sample_id}.csv` consists of three parts. The *first* part includes location, duration, and time window constraints where the XCOORD., YCOORD., EST, TWL, and DUR are x coordinate, y coordinate, early start time, time window length, and duration respectively. Especially, the first `nr` lines indicate the initial location of the robots. The *second* part sorted in bool format number is the precedence constraint. The *third* part sorted in float format is the distance between different tasks. The structure of the sample file is as follows.
```
Headline
nr+nt rows {location, duration, and time window constraints}
nr+nt x nr+nt matrix {precedence constraint}
nr+nt x nr+nt matrix {distance}
```

### 2.2 Dataset Parsing

The example code for parsing the sample file [r3_t9_m0_0](./Data/RL3/r3_t9_m0_0.csv) as follows:
```python
from DataGeneration.MRTAData import MRTAData
robotnum = 3  
tasknums = 9
j, k = 0, 0 
InitDataRoot = "./Data/Init/"
DataRoot = "./Data/RL" + str(robotnum) + "/"
Data = MRTAData(robotnum)
Data.SetInitRT(InitDataRoot + "robot10.csv", InitDataRoot + "task60.csv")
Data.SetMap(InitDataRoot + "map.csv")
filename = "r" + str(robotnum) + "_t" + str(tasknum) + "_m" + str(
    j) + "_" + str(k)
data = Data.GetDatafromFile(DataRoot + filename + ".csv")
```

## 3. BMRTA

### 3.1 Config

Refers to the front part of the file [Batch/mrta_batch.py](./Batch/mrta_batch.py) to configure the testing program of BMRTA.
```Python
robotnum = 5  # the number of robots
tasknums = [9, 18, 27, 36]  # the number of tasks
map_epoch = 10
dag_epoch = 10

InitDataRoot = "./Data/Init/"
DataRoot = "./Data/RL" + str(robotnum) + "/"
SolRoot = "./Sol/Batch/RL" + str(robotnum) + "/"
LogRoot = "./Log/Batch/RL"
```
### 3.2 Testing

```Bash
python ./Batch/mrta_batch.py
```

### 3.3 Solution Analysis
The solution files are stored in Floder [Sol](./Sol/). 

**evaluate result**
```bash
python ./SolAnalysis/SolStatistics.py
```
The evaluation metric results are stored in [temp.csv](./SolAnalysis/temp.csv)

**visualize result**
```bash
python ./SolAnalysis/DrawRoadV.py
```
The visualized videos are stored in Floder [Video](./Video/)

### 3.4 Log Checking

The log files are stored in Floder [Log](./Log/). The Log file contains all screen output of the program. 

## 4. MIP and TePSSI

We also implement the MIP and TePSSI algorithms. The codes of both algorithms share the same structure with BMRTA and are stored in Floder [MIP](./MIP/) and [AuctionO](./AuctionO/) respectively.


## 5. Acknowledgments
We use [Gurobi](https://www.gurobi.com/) to solve the Mixed Integer Programming (MIP) model.