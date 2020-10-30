import matplotlib
matplotlib.use('Agg')
import pandas as pd
import argparse
from matplotlib import pyplot as plt

filenames = ['uniswapv2/convergence-10950202-0xa2107fa5b38d9bbd2c461d6edf11b11a50f6b974.csv', 'uniswapv2/convergence-10984435-0xd3d2e2692501a5c9ca623199d38826e513033a17.csv', 'uniswapv2/convergence-10986514-0x2fdbadf3c4d5a8666bc06645b8358ab803996e28.csv', 'uniswapv2/convergence-10786519-0xc5be99a02c6857f9eac67bbce58df5572498f40c.csv'] #harcode, plot convergence for these 4 runs atleast

dataframes = []

i = 0
for filename in filenames:
    df = pd.read_csv(filename)
    df['mev'] = df['mev'] / df['mev'].max() * 100
    df.set_index('pathnum', inplace=True)
    dataframes.append(df)
    '''
    df.plot('pathnum', 'mev')
    ax = df.plot('pathnum', 'mev', kind='line', legend=None)
    ax.set_ylabel('MEV')
    ax.set_xlabel('PathNum')
    plt.savefig('convergence' + str(i) + '.png')
    i+=1
    '''

df = pd.concat(dataframes,axis=1,sort=False)
df.plot(logx=True)
plt.savefig('convergence_random.png')

#df = pd.concat(dataframes)

