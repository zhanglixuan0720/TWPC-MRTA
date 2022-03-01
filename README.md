# TWPC-MRTA
This repository is created for the dataset of Multi-robot task allocation problem with time window and precedence constraints (TWPC-MRTA)   
There are two data sets in Floder '/Data' - the uniform distribution (UD) data set and the cluster distribution (CD) data set. 

The UD data for $n_r =2,3$ can be found in Foler 'R2.zip' and 'R3.zip' respectively. The CD data for $n_r =2,3$ can be found in Foler 'RC2.zip' and 'RC3.zip' respectively. All files in 'R*.zip' are stored as '.csv' format and named as 'r{n1}\_t{n2}\_m{n3}\_{n4}', where n1 is the number of robots; n2 is number of tasks; n3 marks different robots and tasks location instances; n4 marks different time window and precedence constraints.

As shown in file 'r{n1}\_t{n2}\_m{n3}\_{n4}.csv', the signal task set file consists of three parts. The first part includes location, duration, and time window constraints. The XCOORD., YCOORD., EST, TWL, DUR are x coordinate, y coordinate, early start time, time window length, and duration respectively. In particular, The first n1 lines indicate the initial location of robots. The second part sorted in bool format number is precedence constraints. The third part sorted in float format is the distance between different tasks.

The code for parsing the data set file can be found in 'DataGneration/DataGenerator.py', For example, we can get the robots and tasks information by running:

```python
from DataGeneration.MRTAData import MRTAData
robotnum = 3  
tasknums = 9 
InitDataRoot = "./Data/Init/"
DataRoot = "./Data/R" + str(robotnum) + "/"
Data = MRTAData(robotnum)
Data.SetInitRT(InitDataRoot + "robot3.csv", InitDataRoot + "task60.csv")
Data.SetMap(InitDataRoot + "map.csv")
filename = "r" + str(robotnum) + "_t" + str(tasknum) + "_m" + str(
    j) + "_" + str(k)
data = Data.GetDatafromFile(DataRoot + filename + ".csv")
```
