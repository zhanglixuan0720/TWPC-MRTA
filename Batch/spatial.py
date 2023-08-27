from sklearn.neural_network import MLPRegressor
import csv
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

data = []
traffic_feature = []
traffic_target = []
csv_file = csv.reader(open('packSize_all.csv'))
for content in csv_file:
    content = list(map(float, content))
    if len(content) != 0:
        data.append(content)
        traffic_feature.append(content[0:6])
        traffic_target.append(content[-1])
print('data=', data)
print('traffic_feature=', traffic_feature)
print('traffic_target=', traffic_target)
scaler = StandardScaler()  # 标准化转换
scaler.fit(traffic_feature)  # 训练标准化对象
traffic_feature = scaler.transform(traffic_feature)  # 转换数据集
feature_train, feature_test, target_train, target_test = train_test_split(
    traffic_feature, traffic_target, test_size=0.3, random_state=0)
# 神经网络输入为2，第一隐藏层神经元个数为5，第二隐藏层神经元个数为2，输出结果为2分类。
# solver='lbfgs',  MLP的求解方法：L-BFGS 在小数据上表现较好，Adam 较为鲁棒，
# SGD在参数调整较优时会有最佳表现（分类效果与迭代次数）,SGD标识随机梯度下降。
clf = MLPRegressor(solver='lbfgs',
                   alpha=1e-5,
                   hidden_layer_sizes=(5, 2),
                   random_state=1)
clf.fit(feature_train, target_train)
predict_results = clf.predict(feature_test)
print(accuracy_score(predict_results, target_test))
conf_mat = confusion_matrix(target_test, predict_results)
print(conf_mat)
print(classification_report(target_test, predict_results))
