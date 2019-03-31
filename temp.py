"""import matplotlib.pyplot as plt
import numpy as np
import mpld3

fig, ax = plt.subplots(1,1)
N = 10
bar = ax.bar(range(N),np.random.normal(size=N))
mpld3.save_html(fig,'./bar.html')



"""
import pandas as pd
xl = pd.read_excel('C:/Users/bhara/Desktop/workspace/questions.xlsx')

#Parsing and divding into sector chunks of data from excel
df_R1 = xl[xl['sector']=='R1']
df_R2 = xl[xl['sector']=='R2']
df_R3 = xl[xl['sector']=='R3']
df_R4 = xl[xl['sector']=='R4']

phy=df_R1[df_R1['subsector']=='Physical']
phy['ab']=55

phy['avgsectscore']=phy.iloc[0]['ab']

print(phy)
