import matplotlib # 追加
import pandas as pd
matplotlib.use('Agg') # 追加

import GPy
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.cm import ScalarMappable
from sklearn.preprocessing import MinMaxScaler

import os
import json
import sys

###############
f = open(os.getcwd() + '/commit_log.json', 'r')
json_dict = json.load(f)

p_list = []  # パラメータのリスト
for x in json_dict.values():
    for y in x.values():
        for i in y['parameter']:
            p_list.append(i)
p_list = [x for x in set(p_list) if x is not None]
print(p_list)

m_list = []  # 評価値のリスト
for x in json_dict.values():
    for y in x.values():
        for i in y['metrics']:
            m_list.append(i)
m_list = [x for x in set(m_list) if x is not None]
print(m_list)

# パラメータとパラメータのグラフ
px = p_list[1]  # 好きな評価値を二つ選んでね！(ブラウザで選択してもらう)
py = p_list[0]
m = m_list[1]  # 好きなメトリクスを選んでね！(ブラウザで選択してもらう)
px_num = None
py_num = None
m_num = None

l = []
q = []
lpx = []
lpy = []
lm = []
num = 0

for keys in json_dict.keys():
    hash_dict = json_dict[keys]
    if not bool(hash_dict): continue
    for i in hash_dict.keys():
        if not hash_dict.get(i): continue  # ファイルが空だったら次へ
        if px not in hash_dict[i]['parameter']: continue  # jsonのメトリクスリストにmxがなかった場合
        if py not in hash_dict[i]['parameter']: continue  # jsonのメトリクスリストにmyがなかった場合
        if m not in hash_dict[i]['metrics']: continue  # jsonのパラメータリストにparamがなかった場合
        m_num = hash_dict[i]['metrics'].index(m)  # paramの位置
        px_num = hash_dict[i]['parameter'].index(px)  # mxの位置
        py_num = hash_dict[i]['parameter'].index(py)  # myの位置
        #print(keys + '_' + i)
        #node_name = keys + '_' + i
        l = [float(hash_dict[i]['parameter_change'][px_num].split()[2]),
             float(hash_dict[i]['parameter_change'][py_num].split()[2]),
             int(hash_dict[i]['metrics_value'][0][:-1])]
        lpx.append(float(hash_dict[i]['parameter_change'][px_num].split()[2]))
        lpy.append(float(hash_dict[i]['parameter_change'][py_num].split()[2]))
        lm.append(int(hash_dict[i]['metrics_value'][0][:-1]))
        q.append(l)

        #G.add_node(node_name)  # Add node
        #G.nodes[node_name]["pos"] = (int(hash_dict[i]['metrics_value'][mx_num][:-1]), int(hash_dict[i]['metrics_value'][my_num][:-1]))  # Add node position
        #if pre_node_name in G.nodes(): G.add_edge(node_name, pre_node_name)
        #pre_node_name = node_name
        #G.nodes[node_name]["node_info"] = hash_dict[i]  # Add node_info for customdata
   # pre_h = keys
###############


#l0 = [50, 15, 68]
#l1 = [0, 0, 44]
#l2 = [25, 15, 58]
#l3 = [50, 0, 85]
#l4 = [45, 0, 94]
#l5 = [25, 6, 50]
#l6 = [50, 6, 90]
#l7 = [0, 15, 46]

#q = [l0, l1, l2, l3, l4, l5, l6, l7]
print(l)

df = pd.DataFrame(data=q, columns=[px, py, m])
""" 実験データの逐次記入 """
#df.loc[0] = [50, 15, 68] #初期点
#df.loc[1] = [0, 0, 44]   #初期点
#df.loc[2] = [25, 15, 58] #実験1回目のデータ
#df.loc[3] = [50, 0, 85]  #2回目
#df.loc[4] = [45, 0, 94]  #3回目...
#df.loc[5] = [25, 6, 50]
#df.loc[6] = [50, 6, 90]
#df.loc[7] = [0, 15, 46]

"""データサイズn"""
n = len(df)

""" 入力変数をMinMaxスケーリング """
scaler = MinMaxScaler()
scaler.fit(np.array([min(lpx),max(lpx)]).reshape(-1,1))
df[px] = scaler.transform(df[px].values.reshape(-1,1))

scaler = MinMaxScaler()
scaler.fit(np.array([min(lpy),max(lpy)]).reshape(-1,1))
df[py] = scaler.transform(df[py].values.reshape(-1,1))

"""入力の整形"""
x_train = np.stack([df[px], df[py]], axis=1)
y_train = df[m].values

"""既知のデータをもとにガウス過程回帰"""
kern = GPy.kern.RBF(2)#, ARD=True)
gpy_model = GPy.models.GPRegression(X=x_train.reshape(-1, 2),
                                    Y=y_train.reshape(-1, 1),
                                    kernel=kern,
                                    normalizer=True)

"""モデルの可視化"""
fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(111)

gpy_model.optimize() # カーネル最適化
gpy_model.plot_mean(ax=ax, cmap="jet")  # カーネル最適化後の予測


"""データ点の描画(defaultでは見辛い)"""
[ax.plot(xi, yi, marker=".", color="k", markersize=10) for xi, yi in zip(df[px].values, df[py].values)]
ax.set_ylabel(px, fontsize=18)
ax.set_xlabel(py, fontsize=20)
ax.tick_params(labelsize=20)

"""color bar追加"""
axpos = ax.get_position()
cbar_ax = fig.add_axes([1, 0.15, 0.02, 0.8])
norm = colors.Normalize(vmin=y_train.min(), vmax=y_train.max())
mappable = ScalarMappable(cmap='jet',norm=norm)
cbar_ax.tick_params(labelsize=10)
fig.colorbar(mappable, cax=cbar_ax)

fig.tight_layout()
plt.savefig(f"2dim_gaussian_n={n}.png")

"""
作った回帰モデルをもとに新たな入力xに対する出力yをみて
獲得関数acqを最大化する点(=次に実験を行うべき条件)を探す。
"""
x = np.linspace(0, 1.0, 11)
acq_list = []
for i in range(6):
    x_pred = np.array([x, np.full(11, i * 0.2)]).T
    y_mean, y_var = gpy_model.predict(x_pred)
    acq = (y_mean + ((np.log(n) / n) ** 0.5 * y_var)).max()
    acq_list.append(acq)

next_lem = acq_list.index(max(acq_list)) * 0.2  # 次のレモンの分量
print("max p:", next_lem)

""" 入力を1次元固定して予測(レモン)"""
x_pred = np.array([x, np.full(11, next_lem)]).T
y_mean, y_var = gpy_model.predict(x_pred)

gpy_model.plot(fixed_inputs=[(1, next_lem)], plot_data=False, plot_limits=[-.01, 1.01])
plt.xlabel(px, fontsize=14)
plt.ylabel(m, fontsize=14)

"""獲得関数acq"""
acq = (y_mean + ((np.log(n) / n) ** 0.5 * y_var)) / 5

"""獲得関数の可視化"""
plt.plot(np.linspace(-.01, 1.01, 11), acq, color="g")
plt.plot(acq.argmax() * 0.1,
         acq.max(),
         marker=".", color="r", markersize=14)

plt.legend(["Mean", "Acquisition", "Acq Max", "Confidence"])
plt.savefig(f"1dim_gaussian_n={n}_{next_lem}.png")