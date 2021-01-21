import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import sys
import pandas as pd
import numpy as np
import math


df = pd.read_csv(sys.argv[1])
df['CPUTime'] = df['UserTime'] + df['SysTime']
df['logCPUTime'] = np.log10(df['CPUTime'])
df['logTxCount'] = np.log10(df['TxCount'])

x = []
y = []
z = []
df_copy = df[0:0]


space = np.linspace(0,20000,20)
for index in range(1,len(space)):
    df2 = df[(df['TxCount'] < space[index]) & (df['TxCount'] >= math.floor(space[index-1]))]
    count = df2.count()[0]
    if count != 0:
        p = df2.sample(min(2, count))
        for index, row in p.iterrows():
            x = x + [row['TxCount']]
            y = y + [row['CPUTime']]
            z = z + [row['RealTime']]


space = np.linspace(20000,120000,500)
for index in range(1,len(space)):
    df2 = df[(df['TxCount'] < space[index]) & (df['TxCount'] >= math.floor(space[index-1]))]
    count = df2.count()[0]
    if count != 0:
        avg_cpu = (1.0 * df2['CPUTime'].sum()) / count
        avg_tx = (df2['TxCount'].sum()) // count
        avg_real = (1.0 * df2['RealTime'].sum()) / count

        x = x + [avg_tx]
        y = y + [avg_cpu]
        z = z + [avg_real]


fig = plt.figure()
plt.xlabel('Transaction Count')
plt.ylabel('Time (in seconds)')
# plt.xlim(0.5, 150000)
# plt.ylim(10, 15000)
# plt.gca().set_aspect('equal', adjustable='box')

plt.scatter(x,y, marker='.', color='#377eb8', label="CPU Time") #7293CB'
plt.scatter(x,z, marker='+', linewidth=0.5, color='#ff7f00', label="Real Time")  #D35E60
plt.legend(loc="upper left")

# fig, ax1 = plt.subplots()
# ax2 = ax1.twinx()
# ax1.set_xlabel('Transaction Count')
# ax1.set_ylabel('CPU Time (in seconds)')

# ax2.set_ylabel('Real Time (in seconds)')


# ax1.scatter(x,y, marker='.', color='b')
# ax2.scatter(x,z, marker='.', color='g')
plt.savefig('updated-execution_times.pdf',bbox_inches='tight')
