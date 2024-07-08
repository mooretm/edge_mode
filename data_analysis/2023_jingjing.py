import pandas as pd
import data
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

datapath = r'C:\Users\MooTra\Downloads\All_SRT_data.csv'
df = pd.read_csv(datapath)
d = data.Data(df)

d.normality_tests(list(df['Percent']), title="All Percent Data")

d.normality_plots(list(df['Percent']), title="All Percent Data")

# boxplot = df.boxplot(column=['Percent'], by='Memory')
# plt.show()

# boxplot = df.boxplot(column=['Percent'], by='SNR')
# plt.show()

mems = ['M1', 'M2', 'M3', 'M4']

for mem in mems:
    temp = df[df['Memory']==mem]
    boxplot = temp.boxplot(column=['Percent'], by='SNR')
    plt.show()
