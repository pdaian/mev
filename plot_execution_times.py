import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
df['CPUTime'] = df['UserTime'] + df['SysTime']
df.plot.scatter('TxCount', 'CPUTime')
plt.savefig('execution_times.png')
